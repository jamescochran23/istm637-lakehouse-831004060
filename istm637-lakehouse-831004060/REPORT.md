# ISTM 637 Databricks Project Report

## Part 1 – Git and Repo Setup
- Connected Databricks workspace to GitHub repo `istm637-lakehouse-831004060`.
- Used the Git panel in Databricks to commit notebooks and SQL into `main` (at least two commits).
- Screenshots show the Git panel and commit history.

## Part 2 – Lakehouse Ingest with Lakeflow
- Used Lakeflow ingestion to load `dim_date`, `dim_well`, and `fact_production` into Unity Catalog.
- Verified tables in catalog `istm637_831004060`, schema `oilgas`.
- `ISTM637_Lakeflow_Ingest_Pipeline.sql` defines the ingest pipeline configuration.
- Screenshots show the pipeline and resulting tables.

## Part 3 – Metadata and Governance
- Added table comments and tags (e.g., data description, sensitivity/owner) to key tables like `fact_production` and `dim_well`.
- This supports governed discovery and reuse.
- Screenshot shows the Data Explorer details with comments and tags visible.

## Part 4 – Genie Space and Test Questions
- Created a Genie Space (e.g., “Oil and Gas Production Analytics”) targeting the oilgas tables.
- Generated a table of test questions, SQL queries, and answers; edited AI comments as needed.
- Saved the Genie output as `Oil and Gas Production Analytics.geniespace.json`.
- Screenshots show the Space and an example Genie-generated SQL query and result.

## Part 5 – BI Dashboard
- Built the “ISTM 637 Oil & Gas Dashboard” using the Genie-generated datasets.
- Included visualizations such as total production over time and production by basin/well.
- Dashboard definition exported to `ISTM 637 Oil & Gas Dashboard FINALvdash.json`.
- Screenshot shows the finished dashboard with at least one chart.

## Part 6 – Predictive Model and Forecast
- Used `ISTM637_Predictive_Model_Notebook.ipynb` to train a decline-curve / time-series model on daily oil production.
- Logged evaluation metrics (e.g., R value) and generated a production forecast for a selected well.
- Registered the model in the Unity Catalog Model Registry.
- Screenshots show evaluation metrics and the registered model page.

## Part 7 – Simple App for History + Forecast
- Used Genie to generate a notebook-based dashboard (“Oil Well Production & Forecast Dashboard”) that queries `fact_production`, `dim_date`, `well_forecast`, and `dim_well`.
- The app displays historical production on the left and model forecast on the right for a selected well.
- Databricks Free Edition does not expose the Apps UI, so per instructor guidance, submitted:
  - A screenshot of the Genie prompt used to create the app.
  - A screenshot of the notebook running with both charts visible.
- File: `Oil Well Production & Forecast Dashboard.ipynb`.

## Part 8 – OpenSharing Setup
- Used OpenSharing to create a share including `istm637_831004060.oilgas.dim_well`.
- Created a Databricks recipient using a classmate’s sharing identifier and added them to the share.
- Free Edition prevents mounting or viewing the share, so sharing could not be tested end-to-end; instructor approved using setup screenshots as evidence.
- Screenshots show the share configuration and the recipient being added.