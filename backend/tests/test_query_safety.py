import pytest

from app.security.query_safety import QuerySafetyError, ensure_mongo_pipeline_is_safe, ensure_sql_is_safe


def test_sql_allows_select_and_adds_limit():
    assert ensure_sql_is_safe("select * from sales").lower().endswith("limit 100")


@pytest.mark.parametrize("query", ["DELETE FROM sales", "select * from sales; drop table sales", "UPDATE users SET role='Admin'"])
def test_sql_blocks_mutation(query):
    with pytest.raises(QuerySafetyError):
        ensure_sql_is_safe(query)


def test_mongo_blocks_write_stages():
    with pytest.raises(QuerySafetyError):
        ensure_mongo_pipeline_is_safe([{"$match": {}}, {"$merge": "customers"}])


def test_mongo_adds_default_limit():
    pipeline = ensure_mongo_pipeline_is_safe([{"$match": {"event": "login"}}])
    assert pipeline[-1] == {"$limit": 100}
