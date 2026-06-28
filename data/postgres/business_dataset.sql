CREATE TABLE IF NOT EXISTS sales (
  id SERIAL PRIMARY KEY,
  order_month TEXT NOT NULL,
  region TEXT NOT NULL,
  customer TEXT NOT NULL,
  product TEXT NOT NULL,
  revenue NUMERIC(12, 2) NOT NULL,
  units INTEGER NOT NULL
);

INSERT INTO sales (order_month, region, customer, product, revenue, units) VALUES
('2026-01','North','Nimbus Co','Insight Pro',124000,310),
('2026-02','North','Nimbus Co','Insight Pro',132000,330),
('2026-03','East','Vertex Health','Insight Pro',156000,360),
('2026-04','South','Delta Foods','Forecast Hub',91000,150),
('2026-05','West','Atlas Retail','Pipeline AI',121000,275),
('2026-06','North','Nimbus Co','Retention Lens',109000,191);
