from loguru import logger
import pandas as pd

logger.add("logs/pipeline.log", rotation="1 MB")

def run_pipeline():
    logger.info("Start CRM ETL pipeline")
    df = pd.read_csv("data/customers.csv")
    logger.debug(f"Loaded {len(df)} records")
    df = df[df["is_active"] == True]
    df["signup_year"] = pd.to_datetime(df["signup_date"]).dt.year
    logger.info("Transform complete")
    df.to_csv("data/active_customers.csv", index=False)
    logger.success("Pipeline complete")

if __name__ == "__main__":
    run_pipeline()
