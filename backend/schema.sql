-- schema.sql

-- customers
CREATE TABLE IF NOT EXISTS customers (
  customer_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT,
  city TEXT,
  region_id INT,
  created_at TIMESTAMP DEFAULT now()
);

-- regions
CREATE TABLE IF NOT EXISTS regions (
  region_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

-- products
CREATE TABLE IF NOT EXISTS products (
  product_id SERIAL PRIMARY KEY,
  sku TEXT,
  name TEXT NOT NULL,
  category TEXT,
  price NUMERIC(12,2) NOT NULL
);

-- sales (time series)
CREATE TABLE IF NOT EXISTS sales (
  sale_id SERIAL PRIMARY KEY,
  sale_date DATE NOT NULL,
  customer_id INT REFERENCES customers(customer_id),
  product_id INT REFERENCES products(product_id),
  quantity INT NOT NULL,
  unit_price NUMERIC(12,2) NOT NULL,
  revenue NUMERIC(14,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- invoices
CREATE TABLE IF NOT EXISTS invoices (
  invoice_id SERIAL PRIMARY KEY,
  invoice_date DATE NOT NULL,
  sale_id INT REFERENCES sales(sale_id),
  invoiced BOOLEAN DEFAULT TRUE,
  amount NUMERIC(14,2)
);

-- returns (simple)
CREATE TABLE IF NOT EXISTS returns (
  return_id SERIAL PRIMARY KEY,
  sale_id INT REFERENCES sales(sale_id),
  return_date DATE,
  qty_returned INT,
  refund_amount NUMERIC(14,2)
);
