#!/usr/bin/env python3
import argparse
import os
import asyncio
import logging
from datetime import datetime
from opensearchpy import AsyncOpenSearch

from src.db.libs.opensearch import (
    create_predictions_index,
    save_predictions_to_opensearch,
    wait_for_opensearch,
)
from src.db.libs.model import generate_prediction

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index-name",
        type=str,
        default=os.getenv("PRED_INDEX_NAME", "pred-result-{dt}"),
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    # Get OpenSearch configuration
    opensearch_host = os.getenv("OPENSEARCH_HOST", "localhost")
    opensearch_port = int(os.getenv("OPENSEARCH_PORT", "9200"))
    index_name = args.index_name.format(dt=datetime.now().strftime("%Y%m%d%H%M%S"))

    logger.info(f"Connecting to OpenSearch at {opensearch_host}:{opensearch_port}")

    # Create AsyncOpenSearch client
    client = AsyncOpenSearch(
        hosts=[{"host": opensearch_host, "port": opensearch_port}],
        http_compress=True,
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )

    try:
        # Wait for OpenSearch to be ready
        if not await wait_for_opensearch(client):
            logger.error("OpenSearch is not ready. Exiting.")
            return

        # Generate fake prediction data
        predictions = generate_prediction()

        sample_key = list(predictions.keys())[0]
        sample_pred = predictions[sample_key]
        prob_dim = sample_pred["prob"].shape[0]
        embed_dim = sample_pred["embedding"].shape[0]
        sim_top_k = sample_pred["most_similar_id"].shape[0]

        # Create the predictions index
        if not await create_predictions_index(
            client, index_name, prob_dim, embed_dim, sim_top_k
        ):
            logger.error("Failed to create index. Exiting.")
            return

        # Save predictions to OpenSearch
        success_count = await save_predictions_to_opensearch(
            client, predictions, index_name
        )

        logger.info(f"Index name: {index_name}")
        logger.info(f"Total records: {success_count} / Target records: 2708")

    except Exception as e:
        logger.error(
            f"Unexpected error while indexing prediction results to opensearch: {e}"
        )
    finally:
        # Always close the client connection
        await client.close()


def run_async_main():
    """Wrapper to run the async main function"""
    asyncio.run(main())


if __name__ == "__main__":
    run_async_main()
