import time
import asyncio
import logging
from typing import Dict
from opensearchpy import AsyncOpenSearch
from opensearchpy.helpers import async_bulk

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def wait_for_opensearch(client: AsyncOpenSearch, max_retries=30):
    """Wait for OpenSearch to be ready"""
    for i in range(max_retries):
        try:
            if await client.ping():
                logger.info("OpenSearch is ready!")
                return True
        except Exception:
            logger.info(f"Waiting for OpenSearch... ({i + 1}/{max_retries})")
            await asyncio.sleep(2)
    return False


async def create_predictions_index(
    client: AsyncOpenSearch,
    index_name: str,
    prob_dim: int,
    embed_dim: int,
    sim_top_k: int,
):
    """Create index for prediction results with proper mapping"""

    # Delete index if it exists
    if await client.indices.exists(index=index_name):
        await client.indices.delete(index=index_name)
        logger.info(f"Deleted existing index: {index_name}")

    # Index mapping optimized for ML prediction data
    index_mapping = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "knn": True,  # Enable k-NN for embedding search
            }
        },
        "mappings": {
            "properties": {
                "paper_id": {"type": "integer"},
                "probability": {
                    "type": "knn_vector",
                    "dimension": prob_dim,
                    "method": {"name": "hnsw", "space_type": "l2", "engine": "lucene"},
                },
                "prediction": {"type": "float"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": embed_dim,
                    "method": {"name": "hnsw", "space_type": "l2", "engine": "lucene"},
                },
                "most_similar_id": {
                    "type": "knn_vector",
                    "dimension": sim_top_k,
                    "method": {"name": "hnsw", "space_type": "l2", "engine": "lucene"},
                },
                "most_similar_score": {
                    "type": "knn_vector",
                    "dimension": sim_top_k,
                    "method": {"name": "hnsw", "space_type": "l2", "engine": "lucene"},
                },
                "timestamp": {"type": "date"},
                "metadata": {
                    "type": "object",
                    "properties": {"gnn_version": {"type": "keyword"}},
                },
            }
        },
    }

    try:
        await client.indices.create(index=index_name, body=index_mapping)
        logger.info(f"Created index: {index_name} with k-NN support")
        return True
    except Exception as e:
        logger.error(f"Failed to create index: {e}")
        return False


async def save_predictions_to_opensearch(
    client: AsyncOpenSearch, predictions: Dict[int, Dict], index_name="pred-result"
):
    """Save prediction results to OpenSearch using bulk indexing"""

    logger.info(f"Saving {len(predictions)} predictions to OpenSearch...")

    # Prepare documents for bulk indexing
    documents = []

    for paper_id, data in predictions.items():
        # Convert numpy arrays to lists for JSON serialization
        doc = {
            "_index": index_name,
            "_id": paper_id,
            "_source": {
                "paper_id": paper_id,
                "probability": data["prob"].tolist(),  # Convert numpy array to list
                "prediction": float(data["pred"]),  # Extract single prediction value
                "embedding": data["embedding"].tolist(),  # Convert numpy array to list
                "most_similar_id": data[
                    "most_similar_id"
                ].tolist(),  # Convert numpy array to list
                "most_similar_score": data[
                    "most_similar_score"
                ].tolist(),  # Convert numpy array to list
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "metadata": {
                    "gnn_version": "v1.0.0",
                },
            },
        }
        documents.append(doc)

    # Bulk index all documents
    try:
        start_time = time.time()
        success_count, failed_items = await async_bulk(
            client, documents, index=index_name, chunk_size=50
        )
        duration = time.time() - start_time

        logger.info(
            f"Successfully indexed {success_count} documents in {duration:.2f}s"
        )

        if failed_items:
            logger.warning(f"Failed to index {len(failed_items)} documents")
            for item in failed_items[:5]:  # Show first 5 failures
                logger.warning(f"   Failed: {item}")

        return success_count

    except Exception as e:
        logger.error(f"Bulk indexing failed: {e}")
        return 0
