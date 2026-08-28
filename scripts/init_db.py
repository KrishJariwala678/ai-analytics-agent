import duckdb
with open("sql/schema.sql") as f:
    schema_sql = f.read()
con = duckdb.connect("data/analytics.duckdb")
con.sql(schema_sql)
print("Schema created successfully.")