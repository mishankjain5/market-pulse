# Cloud Architecture Mapping - Market Pulse

This project runs on a laptop, but its structure is a deliberate one-person replica of a
standard cloud data platform (medallion architecture). Below: what each local piece
becomes in the cloud.

## Pipeline mapping

| Stage | This project (local) | Azure | AWS | GCP |
|-------|---------------------|-------|-----|-----|
| Ingestion / orchestration | `collect_data.py` + `&&` chaining | Data Factory | Glue | Dataflow / Composer |
| Raw storage (Bronze) | `raw/` - untouched API output | Data Lake Storage (ADLS) | S3 | Cloud Storage |
| Transform + quality gate (Silver) | `clean_data.py`, `validate.py` | Databricks / Synapse Spark | EMR / Glue jobs | Dataproc |
| Modeled serving layer (Gold) | `outputs/model/` star schema | Synapse / Fabric warehouse | Redshift | BigQuery |
| BI / consumption | `Market_Pulse.pbix` | Power BI Service | QuickSight | Looker Studio |

## Key concepts demonstrated locally

- **Medallion layers:** raw → cleaned → outputs = Bronze → Silver → Gold. Raw is never edited; each layer is rebuildable from the one before it.
- **Quality gates:** `validate.py` exits non-zero on failure, so downstream steps never run on bad data - the same dependency logic as Data Factory activity chains.
- **ELT pattern:** data lands raw first (`raw/`), transformation happens afterward in place - matching modern lake-first architecture.
- **Reproducibility:** `requirements.txt` pins the environment; every transformation is code, so any layer can be rebuilt with one command.
- **Scheduled refresh (cloud equivalent):** locally we rerun the pipeline by hand; in Power BI Service the dataset refreshes on a schedule and the dashboard is consumed in-browser.

## What would change at real scale

- CSVs become Parquet (columnar, compressed - pandas can write it with one line).
- Cron/manual runs become orchestrated DAGs with alerting on failure.
- One laptop's pandas becomes distributed Spark when data outgrows memory.
- Git stays exactly the same. Version control is scale-independent.
