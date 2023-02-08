# trustyai-service-python

## Running

### Locally

Build the container image with

```shell
DOCKER_BUILDKIT=1 docker build -t trustyai/trustyai-service .
```
and run the container using (either `docker`, `podman`):

```shell
docker run -p 8000:8000 -t trustyai/trustyai-service:latest
```

There is also a `compose` configuration which install the service, Prometheus and Grafana.
To run it, use:

```shell
docker-compose compose.yaml up -d # or podman-compose
```

## Endpoints

The OpenAPI schema can be displayed using

```shell
curl -X GET --location "http://localhost:8000/docs"
```

### Metrics

Each of the metrics default bounds can be overriden with
the corresponding environment variable, e.g.

- `SPD_THRESHOLD_LOWER`
- `SPD_THRESHOLD_UPPER`
- _etc_

#### Statistical Parity Difference

Get statistical parity difference at `/metrics/spd`

```shell
curl -X POST --location "http://localhost:8080/metrics/spd" \
    -H "Content-Type: application/json" \
    -d "{
          \"protectedAttribute\": \"gender\",
          \"favorableOutcome\": 1,
          \"outcomeName\": \"income\",
          \"privilegedValue\": 1,
          \"unprivilegedValue\": 0
        }"
```

Returns:

```http request
HTTP/1.1 200 OK
date: Thu, 09 Feb 2023 11:24:22 GMT
server: uvicorn
content-length: 215
content-type: application/json

{
  "type": "metric",
  "name": "SPD",
  "value": -0.14392612184358755,
  "id": "07ef87ec-4d0d-4ca9-b5fd-4803139acac6",
  "timestamp": "2023-02-09T11:24:24.232325",
  "thresholds": {
    "lowerBound": -0.1,
    "upperBound": 0.1,
    "outsideBounds": true
  }
}
```

#### Disparate Impact Ratio

```shell
curl -X POST --location "http://localhost:8080/metrics/dir" \
    -H "Content-Type: application/json" \
    -d "{
          \"protectedAttribute\": \"gender\",
          \"favorableOutcome\": 1,
          \"outcomeName\": \"income\",
          \"privilegedValue\": 1,
          \"unprivilegedValue\": 0
        }"
```

```http request
HTTP/1.1 200 OK
date: Thu, 09 Feb 2023 11:24:51 GMT
server: uvicorn
content-length: 213
content-type: application/json

{
  "type": "metric",
  "name": "DIR",
  "value": 0.47641233184842996,
  "id": "0b42117c-f929-4cf8-b0a1-da8a409d0727",
  "timestamp": "2023-02-09T11:24:52.864581",
  "thresholds": {
    "lowerBound": 0.8,
    "upperBound": 1.2,
    "outsideBounds": true
  }
}
```

### Prometheus

Whenever a metric endpoint is called with a HTTP request, the service also updates
the corresponding Prometheus metric.

The metrics are published at `/metrics` and can be consumed directly with Prometheus.
The examples also include a Grafana dashboard to visualize them.

![](docs/grafana.jpg)

Each Prometheus metric is scoped to a specific `model` and attributes using tags.
For instance, for the SPD metric request above we would have a metric:

```
trustyai_spd{instance="trustyai:8080", 
    job="trustyai-service", 
    model="example", 
    outcome="income", 
    protected="gender"}
```

# Data sources

## Metrics

Data source extend the base `AbstractDataReader` which has the responsibility
of converting any type of data source (flat file on PVC, S3, database, _etc_) into a TrustyAI `Dataframe`.

The type of datasource is passed with the environment variable `STORAGE_FORMAT`.

For demo purposes we abstract the data source to `STORAGE_FORMAT=RANDOM_TEST`
which generates in memory new data points for each request.

## Explainers

An explainer can be linked to the service using the enviroment
variables `KSERVE_TARGET` and `MODEL_NAME`.
These will be used by the service's gRPC client which can natively
query KServe and ModelMesh using that endpoint.

# Deployment

To deploy in Kubernetes or OpenShift, the connection information
can be passed in the manifest as enviroment variables:

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - env:
            - name: KUBERNETES_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: KSERVE_TARGET
              value: localhost
            - name: STORAGE_FORMAT
              value: RANDOM_TEST
            - name: MODEL_NAME
              value: example
          image: trustyai/trustyai-service:1.0.0-SNAPSHOT
          name: trustyai-service
          ports:
            - containerPort: 8080
              name: http
              protocol: TCP
```

