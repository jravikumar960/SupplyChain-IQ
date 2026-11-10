from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.models import ForecastDemand, PurchaseOrder, Shortage, Inventory

def inspect_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    print("=" * 60)
    print("DATABASE INDEX INSPECTION & QUERY PLAN AUDIT")
    print("=" * 60)

    # 1. List all indexes in SQLite
    result = db.execute(text("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index';"))
    indexes = result.fetchall()
    for idx in indexes:
        print(f"Table: {idx[1]} | Index Name: {idx[0]}")
        if idx[2]:
            print(f"  SQL: {idx[2]}")

    print("-" * 60)
    print("EXPLAIN QUERY PLAN EXAMPLES:")
    print("-" * 60)

    # Query 1: ForecastDemand filtered by sku_id and location_id
    q1 = text("EXPLAIN QUERY PLAN SELECT * FROM forecast_demands WHERE sku_id = 'SKU-1' AND location_id = 'LOC-1';")
    plan1 = db.execute(q1).fetchall()
    print("Query 1 (ForecastDemand by SKU & Location):")
    for row in plan1:
        print(f"  {row}")

    # Query 2: PurchaseOrder filtered by is_duplicate and status
    q2 = text("EXPLAIN QUERY PLAN SELECT * FROM purchase_orders WHERE is_duplicate = 0 AND status != 'Cancelled';")
    plan2 = db.execute(q2).fetchall()
    print("Query 2 (PurchaseOrders active & non-duplicate):")
    for row in plan2:
        print(f"  {row}")

    # Query 3: Shortage filtered by severity and status
    q3 = text("EXPLAIN QUERY PLAN SELECT * FROM shortages WHERE severity = 'Critical' AND status = 'Open';")
    plan3 = db.execute(q3).fetchall()
    print("Query 3 (Shortages by severity & status):")
    for row in plan3:
        print(f"  {row}")

    print("=" * 60)
    db.close()

if __name__ == "__main__":
    inspect_db()
