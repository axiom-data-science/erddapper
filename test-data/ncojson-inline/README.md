# Test data demonstrating ncojson-inline

Set .env variables (adjust accordingly):

```
ERDDAPPER_ENABLED_SOURCES=inline:NcoJsonInlineSource
ERDDAPPER_ERDDAP_BASE_URL=http://localhost:8080
ERDDAPPER_ERDDAP_FLAG_KEY_URL=https://localhost:8443
ERDDAPPER_ERDDAP_FLAG_KEY_KEY=some_random_flag_key
ERDDAPPER_DATASET_DATA_DIR=None
```

Run erddapper:

```
uv run uvicorn erddapper.main:app
```

Start up docker compose stack:

```
docker compose up -d
```

POST ncojson to erddapper to create the test dataset:

```
curl -sS -X POST -H "Content-type: application/json" \
  --data-binary @test-data/ncojson-inline/fernandina-beach.ncojson \
  http://localhost:8000/datasets/test
```
