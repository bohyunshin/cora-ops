# Cora-Ops API Specification

**Version**: 1.0.0
**Base URL**: `http://localhost:8000`
**Content-Type**: `application/json`

## Overview

The Cora-Ops API provides endpoints for paper classification and similarity search using semi-supervised machine learning models trained on the Cora citation network dataset.

## Authentication

Currently, the API operates without authentication for development purposes. Production deployments should implement proper authentication mechanisms.

## Note

Before requesting api, you should identify which index name is created while setting up `Docker`. The index name created while building docker can be found in `python-app` logs.

First go to the project root directoy. Then run following command.

```bash
$ docker-compose logs python-app
...
opensearch-python-app  | 2025-07-28 08:44:40,244 - __main__ - INFO - Prediction data processing completed successfully!
opensearch-python-app  | 2025-07-28 08:44:40,244 - __main__ - INFO - View your data at: http://localhost:5601
opensearch-python-app  | 2025-07-28 08:44:40,244 - __main__ - INFO - Index name: pred-result-20250728084434  <--- Created index name
opensearch-python-app  | 2025-07-28 08:44:40,244 - __main__ - INFO - Total records: 2708
```

You can see that `pred-result-20250728084434` is created, in which predcited class and probability are stored. You can also find this data in opensearch dashboard, whose url is `http://localhost:5601`.

Be sure to use this index name when calling `/predict` or `/most_similar` !

## API Endpoints

### 1. Health Check

**GET** `/health`

Check the API server health and OpenSearch connection status.

#### Example Request

```bash
curl -X GET "http://localhost:8000/health" \
  -H "Content-Type: application/json"
```

#### Example Response

```json
{
    "status":"healthy",
    "opensearch_connected":true
}
```

---

### 2. Paper Classification Prediction

**POST** `/predict`

Classify a research paper into one of the Cora dataset categories using the trained semi-supervised model.

#### Request Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `index_name` | string | Yes | OpenSearch index name containing the prediction results |
| `paper_id` | integer | Yes | Paper ID to get prediction for (must be existing id) |

#### Example Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "pred-result-20250728084434",
    "paper_id": 31336
  }'
```

#### Response Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `paper_id` | integer | Yes | Requested paper_id |
| `pred_label_index` | integer | Yes | Predicted label for requested paper_id in **index** |
| `probabilities` | list[float] | Yes | List of predicted probability for each class |

#### Example Response

```json
{
    "paper_id":31336,
    "pred_label_index":2,
    "probabilities":
        [
            0.0006127526867203414,
            0.0006338093662634492,
            0.9886462688446045,
            0.004672002047300339,
            0.0014983013970777392,
            0.0014011797029525042,
            0.002535612089559436
        ]
}
```

**Note**: `pred_label_index` is not actual label (for example `Science`) but index for predicted label. You can notice that `probabilities[2]` has highest probability, which is approximately `0.99`.

---

### 3. Most Similar Papers

**POST** `/most_similar`

Find the most similar papers to a given paper and their associated scores.

#### Request Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `index_name` | string | Yes | OpenSearch index name containing the prediction results |
| `paper_id` | integer | Yes | Paper ID to get prediction for (must be existing id) |
| `top_k` | integer | No (default=5) | Number of papers to retrieve |


#### Example Request

```bash
curl -X POST "http://localhost:8000/most_similar" \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "pred-result-20250728084434",
    "paper_id": 31336
  }'
```

#### Response Body Parameter

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `paper_id` | string | Yes | Requested paper_id |
| `most_similar_ids` | list[integer] | Yes | List of top_k similar paper_ids |
| `most_similar_scores` | list[float] | Yes | List of scores for top_k similar paper_ids |

#### Example Response

```json
{
    "paper_id":31336,
    "most_similar_ids": [
        1125082,
        286562,
        1131748,
        1131647,
        1131420,
        763181,
        919885,
        662279,
        169279,
        7272
    ],
    "most_similar_scores":
        [
            3.530538558959961,
            3.4976706504821777,
            3.40584135055542,
            3.387244701385498,
            3.3429460525512695,
            3.3197638988494873,
            3.3191397190093994,
            3.2808330059051514,
            3.2725234031677246,
            3.264850378036499
        ]
}
```
