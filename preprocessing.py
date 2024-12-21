import polars as pl

data = pl.read_csv("./assets/data/US_Accidents_March23.csv")

state_summary = data.group_by('State').agg([
    pl.count("ID").alias("accidents"),
    pl.mean("Severity").alias("avg_severity")
])

state_summary.write_parquet("./assets/data/state_level.parquet")