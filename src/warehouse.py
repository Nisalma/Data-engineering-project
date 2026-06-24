import duckdb
import os

# Connect to a local database storage file
con = duckdb.connect(database="airbnb_warehouse.db", read_only=False)

print("📂 Scanning your data folder...")
# Let's check exactly what Windows named these files under the hood
data_files = os.listdir('./data') if os.path.exists('./data') else []
print(f"   Found files: {data_files}")

print("\n📦 Connecting database views...")

try:
    # We will try the most likely name (listings.csv) since they are unzipped
    con.execute("CREATE OR REPLACE VIEW raw_listings AS SELECT * FROM read_csv_auto('./data/listings.csv');")
    con.execute("CREATE OR REPLACE VIEW raw_calendar AS SELECT * FROM read_csv_auto('./data/calendar.csv');")
    con.execute("CREATE OR REPLACE VIEW raw_reviews AS SELECT * FROM read_csv_auto('./data/reviews.csv');")
    con.execute("CREATE OR REPLACE VIEW raw_neighbourhoods AS SELECT * FROM read_csv_auto('./data/neighbourhoods.csv');")
    
    listing_count = con.execute("SELECT COUNT(*) FROM raw_listings;").fetchone()[0]
    print(f"🎉 Database Active! Found {listing_count:,} properties.")
    
except Exception as e:
    print(f"❌ Standard .csv path failed. Trying fallback name matching...")
    try:
        # Fallback: Just look for files starting with the name
        con.execute("CREATE OR REPLACE VIEW raw_listings AS SELECT * FROM read_csv_auto('./data/listings*');")
        con.execute("CREATE OR REPLACE VIEW raw_calendar AS SELECT * FROM read_csv_auto('./data/calendar*');")
        con.execute("CREATE OR REPLACE VIEW raw_reviews AS SELECT * FROM read_csv_auto('./data/reviews*');")
        con.execute("CREATE OR REPLACE VIEW raw_neighbourhoods AS SELECT * FROM read_csv_auto('./data/neighbourhoods*');")
        
        listing_count = con.execute("SELECT COUNT(*) FROM raw_listings;").fetchone()[0]
        print(f"🎉 Database Active via fallback! Found {listing_count:,} properties.")
    except Exception as fallback_error:
        print(f"💥 Critical error: Both regular and fallback paths failed. Details: {fallback_error}")

con.close()