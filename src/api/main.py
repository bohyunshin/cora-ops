from fastapi import FastAPI, HTTPException
import os
import logging
from contextlib import asynccontextmanager
from opensearchpy import AsyncOpenSearch


from src.api.schema import (
    PredictRequest,
    SimilarRequest,
    PredictResponse,
    SimilarResponse,
    HealthResponse,
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global OpenSearch client
opensearch_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage OpenSearch connection lifecycle"""
    global opensearch_client

    # Startup
    opensearch_host = os.getenv("OPENSEARCH_HOST", "localhost")
    opensearch_port = int(os.getenv("OPENSEARCH_PORT", "9200"))

    logger.info(f"Connecting to OpenSearch at {opensearch_host}:{opensearch_port}")

    opensearch_client = AsyncOpenSearch(
        hosts=[{"host": opensearch_host, "port": opensearch_port}],
        http_compress=True,
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )

    # Test connection
    try:
        if await opensearch_client.ping():
            logger.info("Connected to OpenSearch successfully")
        else:
            logger.error("Failed to connect to OpenSearch")
    except Exception as e:
        logger.error(f"OpenSearch connection error: {e}")

    yield

    # Shutdown
    if opensearch_client:
        await opensearch_client.close()
        logger.info("Closed OpenSearch connection")


# Create FastAPI app with lifespan
app = FastAPI(
    title="ML Prediction API",
    description="API for retrieving ML predictions and similar papers from OpenSearch",
    version="1.0.0",
    lifespan=lifespan,
)


# Helper function to get document from OpenSearch
async def get_paper_document(index_name: str, paper_id: int):
    """Retrieve paper document from OpenSearch"""
    try:
        response = await opensearch_client.get(index=index_name, id=paper_id)
        return response["_source"]
    except Exception as e:
        logger.error(f"paper_id {paper_id} not found in {index_name}: {e}")
        raise HTTPException(
            status_code=404, detail=f"Paper {paper_id} not found in index {index_name}"
        )


# API Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    opensearch_connected = False
    try:
        if opensearch_client:
            opensearch_connected = await opensearch_client.ping()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to health check: {e}")

    return HealthResponse(
        status="healthy" if opensearch_connected else "degraded",
        opensearch_connected=opensearch_connected,
    )


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """Get prediction and probability for a paper"""

    if not opensearch_client:
        raise HTTPException(status_code=503, detail="OpenSearch client not available")

    # Retrieve document
    doc = await get_paper_document(request.index_name, request.paper_id)

    # Extract prediction data
    try:
        return PredictResponse(
            paper_id=doc["paper_id"],
            pred_label_index=doc["prediction"],
            probabilities=doc["probability"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.post("/most_similar", response_model=SimilarResponse)
async def most_similar(request: SimilarRequest):
    """Get most similar papers and their scores"""

    if not opensearch_client:
        raise HTTPException(status_code=503, detail="OpenSearch client not available")

    # Retrieve document
    doc = await get_paper_document(request.index_name, request.paper_id)

    # Extract similarity data
    try:
        return SimilarResponse(
            paper_id=doc["paper_id"],
            most_similar_ids=doc["most_similar_id"][: request.top_k],
            most_similar_scores=doc["most_similar_score"][: request.top_k],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ML Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "POST /predict": "Get prediction and probability for a paper",
            "POST /most_similar": "Get most similar papers and scores",
            "GET /health": "Health check",
            "GET /docs": "API documentation",
        },
        "example_request": {
            "index_name": "pred-result-20250728084431",
            "paper_id": 31336,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
