# seed_db.py
import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv
import psycopg

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "nlp_analytics")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

def connect():
    conn = psycopg.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    return conn

def daterange(start_date, end_date):
    d = start_date
    while d <= end_date:
        yield d
        d += timedelta(days=1)

def main():
    conn = connect()
    cur = conn.cursor()
    # fetch product ids and prices
    cur.execute("SELECT product_id, price FROM products")
    products = cur.fetchall()
    cur.execute("SELECT customer_id FROM customers")
    customers = [r[0] for r in cur.fetchall()]

    # generate ~1200 sales across 24 months
    start = date(2023,1,1)
    end = date(2024,12,31)
    rows = []
    for single_date in daterange(start, end):
        # per day generate 0..3 sales
        for _ in range(random.choices([0,1,2,3], weights=[60,25,10,5])[0]):
            cust = random.choice(customers)
            prod_id, price = random.choice(products)
            qty = random.choices([1,2,3,5,10],[70,15,8,5,2])[0]
            unit_price = float(price)
            rows.append((single_date.isoformat(), cust, prod_id, qty, unit_price))

    # bulk insert
    cur.executemany(
        "INSERT INTO sales (sale_date, customer_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s,%s)",
        rows
    )
    conn.commit()

    # generate invoices for a portion of sales
    cur.execute("SELECT sale_id FROM sales")
    sale_ids = [r[0] for r in cur.fetchall()]
    invoice_rows = []
    for s in random.sample(sale_ids, int(len(sale_ids)*0.85)):
        invoice_rows.append((date.today().isoformat(), s, True, None))
    cur.executemany("INSERT INTO invoices (invoice_date, sale_id, invoiced, amount) VALUES (%s,%s,%s,%s)", invoice_rows)
    conn.commit()

    # generate some returns (5% of sales)
    ret_rows = []
    for s in random.sample(sale_ids, int(len(sale_ids)*0.05)):
        qty_returned = random.choice([1,1,2])
        cur.execute("SELECT unit_price, quantity FROM sales WHERE sale_id=%s", (s,))
        up, orig_qty = cur.fetchone()
        refund = min(qty_returned, orig_qty) * float(up)
        ret_rows.append((s, date.today().isoformat(), qty_returned, refund))
    cur.executemany("INSERT INTO returns (sale_id, return_date, qty_returned, refund_amount) VALUES (%s,%s,%s,%s)", ret_rows)
    conn.commit()

    print("Inserted rows:", len(rows))
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
