# Cora-Ops Opensearch Database

A Python application for storing and managing machine learning prediction results using OpenSearch with k-NN vector search capabilities.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENSEARCH_HOST` | `localhost` | OpenSearch server host |
| `OPENSEARCH_PORT` | `9200` | OpenSearch server port |

## Usage

### Basic Usage

```bash
$ uv run python3 save_prediction.py
```

After running above command, the predictions will be generated using `pretrained_weight/*.pt` result.

### Example Output

```
2025-07-28 10:30:00 - __main__ - INFO - Connecting to OpenSearch at localhost:9200
2025-07-28 10:30:01 - opensearch - INFO - OpenSearch is ready!
2025-07-28 10:30:01 - opensearch - INFO - Deleted existing index: pred-result-20250728103001
2025-07-28 10:30:02 - opensearch - INFO - Created index: pred-result-20250728103001 with k-NN support
2025-07-28 10:30:02 - opensearch - INFO - Saving 2708 predictions to OpenSearch...
2025-07-28 10:30:05 - opensearch - INFO - Successfully indexed 2708 documents in 2.34s
2025-07-28 10:30:05 - __main__ - INFO - Index name: pred-result-20250728103001
2025-07-28 10:30:05 - __main__ - INFO - Total records: 2708 / Target records: 2708
```

## Note

You do not have to run above sciprt manually. Just let `Docker` do everything through `docker-compose`!
