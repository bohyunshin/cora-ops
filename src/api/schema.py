from pydantic import BaseModel, Field
from typing import List


# Request models
class PredictRequest(BaseModel):
    index_name: str = Field(
        ..., description="OpenSearch index name", example="pred-result-20250728084431"
    )
    paper_id: int = Field(
        ..., description="Paper ID to get prediction for", example=31336, gt=0
    )


class SimilarRequest(BaseModel):
    index_name: str = Field(
        ..., description="OpenSearch index name", example="pred-result-20250728084431"
    )
    top_k: int = Field(5, description="Number of papers to return", example=5, gt=0)
    paper_id: int = Field(
        ..., description="Paper ID to get similar papers for", example=31336, gt=0
    )


# Response models
class PredictResponse(BaseModel):
    paper_id: int = Field(..., description="Paper ID", example=31336)
    pred_label_index: int = Field(
        ..., description="Predicted class label index", example=2
    )
    probabilities: List[float] = Field(
        ..., description="Class probabilities", example=[0.1, 0.2, 0.7]
    )


class SimilarResponse(BaseModel):
    paper_id: int = Field(..., description="Paper ID", example=31336)
    most_similar_ids: List[int] = Field(
        ..., description="Most similar paper IDs", example=[1234, 5678, 9012]
    )
    most_similar_scores: List[float] = Field(
        ..., description="Similarity scores", example=[0.95, 0.89, 0.82]
    )


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status", example="healthy")
    opensearch_connected: bool = Field(
        ..., description="OpenSearch connection status", example=True
    )
