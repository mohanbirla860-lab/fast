

from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://root:Mohan%40123@localhost:3306/college"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("✅ Connected Successfully!")
except Exception as e:
    print("❌ Connection Failed")
    print(e)