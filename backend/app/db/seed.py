from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import DatabaseConnection, User, Workspace, WorkspaceMember
from app.models.entities import ConnectionKind, Role
from app.security.passwords import hash_password
from app.services.workspace_resources import seed_demo_documents


def seed_application(db: Session) -> None:
    admin = db.query(User).filter(User.email == "admin@insightai.ai").first()
    if not admin:
        admin = User(
            email="admin@insightai.ai",
            full_name="InsightAI Admin",
            hashed_password=hash_password("InsightAI123"),
            role=Role.super_admin,
        )
        db.add(admin)
        db.flush()

    workspace = db.query(Workspace).filter(Workspace.slug == "acme-revenue").first()
    if not workspace:
        workspace = Workspace(name="Acme Revenue Analytics", slug="acme-revenue", owner_id=admin.id)
        db.add(workspace)
        db.flush()
        db.add(WorkspaceMember(workspace_id=workspace.id, user_id=admin.id, role=Role.super_admin))

    demo_uri = "sqlite:///./insightai.db"
    connection = db.query(DatabaseConnection).filter(DatabaseConnection.name == "Acme Analytics Warehouse").first()
    if not connection:
        db.add(
            DatabaseConnection(
                workspace_id=workspace.id,
                name="Acme Analytics Warehouse",
                kind=ConnectionKind.sqlite,
                uri=demo_uri,
                is_read_only=True,
                selected_assets=["sales", "customers", "products", "orders", "employees", "regions", "expenses", "inventory"],
                created_by=admin.id,
            )
        )
    else:
        connection.selected_assets = ["sales", "customers", "products", "orders", "employees", "regions", "expenses", "inventory"]
    db.commit()
    seed_business_tables(db)
    seed_demo_documents(workspace.id)


def seed_business_tables(db: Session) -> None:
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                order_month TEXT,
                region TEXT,
                customer TEXT,
                product TEXT,
                revenue REAL,
                units INTEGER
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                customer TEXT,
                segment TEXT,
                region TEXT,
                lifetime_value REAL,
                last_active TEXT
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                product TEXT,
                category TEXT,
                margin REAL,
                inventory INTEGER
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS regions (
                id INTEGER PRIMARY KEY,
                region TEXT UNIQUE,
                manager TEXT,
                country TEXT,
                quota REAL
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                employee TEXT,
                role TEXT,
                region TEXT,
                start_date TEXT,
                quota REAL
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                order_date TEXT,
                customer TEXT,
                product TEXT,
                region TEXT,
                order_value REAL,
                status TEXT
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                expense_month TEXT,
                region TEXT,
                department TEXT,
                expense_amount REAL,
                category TEXT
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY,
                product TEXT,
                warehouse TEXT,
                region TEXT,
                on_hand INTEGER,
                reorder_point INTEGER,
                last_sync TEXT
            )
            """
        )
    )
    count = db.execute(text("SELECT COUNT(*) FROM sales")).scalar_one()
    if not count:
        rows = [
            ("2026-01", "North", "Nimbus Co", "Insight Pro", 124000, 310),
            ("2026-01", "West", "Atlas Retail", "Pipeline AI", 98000, 220),
            ("2026-02", "North", "Nimbus Co", "Insight Pro", 132000, 330),
            ("2026-02", "South", "Delta Foods", "Forecast Hub", 86000, 140),
            ("2026-03", "East", "Vertex Health", "Insight Pro", 156000, 360),
            ("2026-03", "West", "Atlas Retail", "Pipeline AI", 117000, 260),
            ("2026-04", "North", "Nimbus Co", "Retention Lens", 101000, 180),
            ("2026-04", "South", "Delta Foods", "Forecast Hub", 91000, 150),
            ("2026-05", "East", "Vertex Health", "Insight Pro", 172000, 390),
            ("2026-05", "West", "Atlas Retail", "Pipeline AI", 121000, 275),
            ("2026-06", "South", "Delta Foods", "Forecast Hub", 74000, 121),
            ("2026-06", "North", "Nimbus Co", "Retention Lens", 109000, 191),
        ]
        db.execute(
            text("INSERT INTO sales (order_month, region, customer, product, revenue, units) VALUES (:m, :r, :c, :p, :rev, :u)"),
            [{"m": m, "r": r, "c": c, "p": p, "rev": rev, "u": u} for m, r, c, p, rev, u in rows],
        )
    if not db.execute(text("SELECT COUNT(*) FROM customers")).scalar_one():
        db.execute(
            text("INSERT INTO customers (customer, segment, region, lifetime_value, last_active) VALUES (:c, :s, :r, :l, :a)"),
            [
                {"c": "Nimbus Co", "s": "Enterprise", "r": "North", "l": 880000, "a": "2026-06-22"},
                {"c": "Atlas Retail", "s": "Mid-market", "r": "West", "l": 620000, "a": "2026-06-19"},
                {"c": "Delta Foods", "s": "Mid-market", "r": "South", "l": 410000, "a": "2026-06-11"},
                {"c": "Vertex Health", "s": "Enterprise", "r": "East", "l": 730000, "a": "2026-06-25"},
            ],
        )
    if not db.execute(text("SELECT COUNT(*) FROM products")).scalar_one():
        db.execute(
            text("INSERT INTO products (product, category, margin, inventory) VALUES (:p, :c, :m, :i)"),
            [
                {"p": "Insight Pro", "c": "Analytics", "m": 0.72, "i": 1200},
                {"p": "Pipeline AI", "c": "Automation", "m": 0.63, "i": 820},
                {"p": "Forecast Hub", "c": "Planning", "m": 0.58, "i": 310},
                {"p": "Retention Lens", "c": "Customer", "m": 0.66, "i": 270},
            ],
        )
    if not db.execute(text("SELECT COUNT(*) FROM regions")).scalar_one():
        db.execute(
            text("INSERT INTO regions (region, manager, country, quota) VALUES (:r, :m, :c, :q)"),
            [
                {"r": "North", "m": "Ava Patel", "c": "USA", "q": 760000},
                {"r": "South", "m": "Noah Singh", "c": "USA", "q": 520000},
                {"r": "East", "m": "Mia Chen", "c": "USA", "q": 690000},
                {"r": "West", "m": "Leo Brooks", "c": "USA", "q": 640000},
            ],
        )
    if not db.execute(text("SELECT COUNT(*) FROM employees")).scalar_one():
        db.execute(
            text("INSERT INTO employees (employee, role, region, start_date, quota) VALUES (:e, :role, :r, :s, :q)"),
            [
                {"e": "Ava Patel", "role": "Regional Director", "r": "North", "s": "2023-02-01", "q": 760000},
                {"e": "Noah Singh", "role": "Regional Director", "r": "South", "s": "2022-11-15", "q": 520000},
                {"e": "Mia Chen", "role": "Regional Director", "r": "East", "s": "2021-07-20", "q": 690000},
                {"e": "Leo Brooks", "role": "Regional Director", "r": "West", "s": "2024-01-08", "q": 640000},
            ],
        )
    if not db.execute(text("SELECT COUNT(*) FROM orders")).scalar_one():
        db.execute(
            text("INSERT INTO orders (order_date, customer, product, region, order_value, status) VALUES (:d, :c, :p, :r, :v, :s)"),
            [
                {"d": "2026-06-02", "c": "Nimbus Co", "p": "Retention Lens", "r": "North", "v": 54000, "s": "closed"},
                {"d": "2026-06-04", "c": "Delta Foods", "p": "Forecast Hub", "r": "South", "v": 31000, "s": "closed"},
                {"d": "2026-06-12", "c": "Vertex Health", "p": "Insight Pro", "r": "East", "v": 88000, "s": "processing"},
                {"d": "2026-06-18", "c": "Atlas Retail", "p": "Pipeline AI", "r": "West", "v": 61000, "s": "closed"},
            ],
        )
    if not db.execute(text("SELECT COUNT(*) FROM expenses")).scalar_one():
        db.execute(
            text("INSERT INTO expenses (expense_month, region, department, expense_amount, category) VALUES (:m, :r, :d, :a, :c)"),
            [
                {"m": "2026-06", "r": "North", "d": "Sales", "a": 24000, "c": "travel"},
                {"m": "2026-06", "r": "South", "d": "Marketing", "a": 18000, "c": "campaigns"},
                {"m": "2026-06", "r": "East", "d": "Support", "a": 21000, "c": "operations"},
                {"m": "2026-06", "r": "West", "d": "Sales", "a": 26000, "c": "events"},
            ],
        )
    if not db.execute(text("SELECT COUNT(*) FROM inventory")).scalar_one():
        db.execute(
            text("INSERT INTO inventory (product, warehouse, region, on_hand, reorder_point, last_sync) VALUES (:p, :w, :r, :o, :rp, :s)"),
            [
                {"p": "Insight Pro", "w": "North Hub", "r": "North", "o": 1200, "rp": 300, "s": "2026-06-27"},
                {"p": "Pipeline AI", "w": "West Hub", "r": "West", "o": 820, "rp": 250, "s": "2026-06-27"},
                {"p": "Forecast Hub", "w": "South Hub", "r": "South", "o": 310, "rp": 300, "s": "2026-06-26"},
                {"p": "Retention Lens", "w": "North Hub", "r": "North", "o": 270, "rp": 320, "s": "2026-06-26"},
            ],
        )
    db.commit()


def write_seed_files() -> None:
    postgres = Path("../data/postgres/business_dataset.sql")
    mongo = Path("../data/mongo/example_collections.json")
    postgres.parent.mkdir(parents=True, exist_ok=True)
    mongo.parent.mkdir(parents=True, exist_ok=True)
