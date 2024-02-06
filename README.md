# OpenTelemetry and Azure OpenAI Demo

This repository contains demo code for exploring a possible "anomaly detection" system using OpenAI embeddings.

You can read more about this on my [blog](https://blakewills.co.uk/otel-openai/).

## Getting Started

You can run this code locally. The protobuf files containing the traces for all four datasets are available within `/data`.

You will need an instance of Azure OpenAI deployed in Azure.

Three steps to getting started:

- Launch a local instance of `qdrant`: `docker compose up -d`
  - The UI is available at http://localhost:6333/dashboard
- Run the `1_data_loading.ipynb` notebook once per dataset
  - `baseline`
  - `live_add_brazil`
  - `live_high_uk_latency`
  - `live_unseen_exception_type`
- Analyse the data by running `2_data_analysis.ipynb`

