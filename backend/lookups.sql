-- lookups.sql

INSERT INTO regions (name) VALUES
('North America'),('Europe'),('Asia'),('South America'),('Africa');

-- sample products
INSERT INTO products (sku, name, category, price) VALUES
('SKU-1001','Acme Widget Small','Widgets',19.99),
('SKU-1002','Acme Widget Large','Widgets',39.99),
('SKU-2001','Gizmo Standard','Gizmos',24.50),
('SKU-2002','Gizmo Pro','Gizmos',49.00),
('SKU-3001','Service Subscription Monthly','Service',9.99);

-- sample customers
INSERT INTO customers (name,email,city,region_id) VALUES
('Acme Corp','purchasing@acme.com','New York',1),
('Beta Ltd','beta@beta.com','London',2),
('Gamma Pvt','contact@gamma.in','Bangalore',3),
('Delta SAS','sales@delta.fr','Paris',2),
('Epsilon GmbH','info@epsilon.de','Berlin',2);
