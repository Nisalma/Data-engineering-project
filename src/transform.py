import os
import duckdb
import logging

# Set up professional execution logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_pipeline():
    logging.info("Initializing Expernetic Airbnb Transformation Pipeline...")
    
    # Connect to the local database file
    db_path = "airbnb_warehouse.db"
    con = duckdb.connect(database=db_path, read_only=False)
    
    try:
        # Check if raw files exist before running to prevent crashes
        if not os.path.exists("./data/listings.csv") or not os.path.exists("./data/calendar.csv"):
            raise FileNotFoundError(" Missing raw CSV files in the './data' directory!")

        # --- Section 3.1 & 3.2: Re-verify and Map Raw Views ---
        logging.info(" Mapping raw ingestion data views...")
        con.execute("CREATE OR REPLACE VIEW raw_listings AS SELECT * FROM read_csv_auto('./data/listings.csv');")
        con.execute("CREATE OR REPLACE VIEW raw_calendar AS SELECT * FROM read_csv_auto('./data/calendar.csv');")
        con.execute("CREATE OR REPLACE VIEW raw_reviews AS SELECT * FROM read_csv_auto('./data/reviews.csv');")
        con.execute("CREATE OR REPLACE VIEW raw_neighbourhoods AS SELECT * FROM read_csv_auto('./data/neighbourhoods.csv');")

        # --- Section 3.2 & 3.3: Neighborhood Aggregations ---
        logging.info("Computing neighbourhood contextual layers...")
        con.execute("""
            CREATE OR REPLACE TABLE dim_neighbourhood_stats AS
            SELECT 
                COALESCE(neighbourhood_cleansed, 'Unknown') as neighbourhood,
                COUNT(*) as listing_density,
                ROUND(MEDIAN(CAST(REGEXP_REPLACE(price, '[$,]', '', 'g') AS FLOAT)), 2) as median_price_yen
            FROM raw_listings
            GROUP BY neighbourhood_cleansed;
        """)

        # --- Section 3.2 & 3.4: Build Cleaned Property Dimensions ---
        logging.info("Standardizing listings and applying business rule data imputation...")
        con.execute("""
            CREATE OR REPLACE TABLE dim_listings_cleaned AS
            SELECT 
                CAST(id AS BIGINT) as listing_id,
                COALESCE(name, 'Unknown Listing') as name,
                LOWER(TRIM(room_type)) as room_type,
                LOWER(TRIM(property_type)) as property_type,
                COALESCE(neighbourhood_cleansed, 'Unknown') as neighbourhood,
                CAST(accommodates AS INTEGER) as accommodates,
                COALESCE(CAST(bedrooms AS INTEGER), 1) as bedrooms,
                COALESCE(CAST(beds AS INTEGER), 1) as beds,
                ROUND(CAST(REGEXP_REPLACE(price, '[$,]', '', 'g') AS FLOAT) / 
                      COALESCE(CAST(bedrooms AS INTEGER), 1), 2) as price_per_bedroom
            FROM raw_listings
            WHERE id IS NOT NULL 
              AND CAST(REGEXP_REPLACE(price, '[$,]', '', 'g') AS FLOAT) > 0;
        """)

        # --- Section 3.2 & 3.4: Build Cleaned Host Dimensions ---
        logging.info(" Processing operator profiles and computing host tenure parameters...")
        con.execute("""
            CREATE OR REPLACE TABLE dim_hosts_cleaned AS
            SELECT DISTINCT
                CAST(host_id AS BIGINT) as host_id,
                COALESCE(host_name, 'Anonymous Host') as host_name,
                CAST(host_since AS DATE) as host_since_date,
                ROUND(DATE_DIFF('day', CAST(host_since AS DATE), CAST('2026-06-23' AS DATE)) / 365.25, 2) as host_tenure_years,
                COALESCE(host_is_superhost, 'f') as is_superhost
            FROM raw_listings
            WHERE host_id IS NOT NULL;
        """)

        # --- Section 3.3: Calculate Operational Performance Metrics ---
        logging.info(" Parsing calendar logs to calculate occupancy rate matrices...")
        con.execute("""
            CREATE OR REPLACE TABLE metrics_calendar_summary AS
            SELECT 
                CAST(listing_id AS BIGINT) as listing_id,
                ROUND(COUNT(CASE WHEN available = 'f' THEN 1 END) * 100.0 / COUNT(*), 2) as occupancy_rate_pct,
                ROUND(SUM(CASE WHEN available = 'f' THEN CAST(REGEXP_REPLACE(price, '[$,]', '', 'g') AS FLOAT) ELSE 0 END), 2) as est_revenue_window
            FROM raw_calendar
            GROUP BY listing_id;
        """)

        # --- Section 3.4: Generate Final Unified Star Schema Fact Master ---
        logging.info(" Materializing unified analytical Star Schema master data table...")
        con.execute("""
            CREATE OR REPLACE TABLE fact_enriched_master AS
            SELECT 
                l.listing_id,
                l.name,
                l.room_type,
                l.price_per_bedroom,
                h.host_name,
                h.host_tenure_years,
                h.is_superhost,
                c.occupancy_rate_pct,
                c.est_revenue_window,
                n.listing_density as neighbourhood_density,
                n.median_price_yen as neighbourhood_median_price
            FROM dim_listings_cleaned l
            LEFT JOIN raw_listings raw ON l.listing_id = CAST(raw.id AS BIGINT)
            LEFT JOIN dim_hosts_cleaned h ON CAST(raw.host_id AS BIGINT) = h.host_id
            LEFT JOIN metrics_calendar_summary c ON l.listing_id = c.listing_id
            LEFT JOIN dim_neighbourhood_stats n ON l.neighbourhood = n.neighbourhood;
        """)

        logging.info("Core Pipeline Execution Successful! All tables populated in production.")
        
    except Exception as e:
        logging.error(f" Pipeline Execution Aborted Due To Error: {e}")
    finally:
        con.close()
        logging.info(" Connection safely released.")

if __name__ == "__main__":
    run_pipeline()