import polars as pl

data = pl.read_csv("./assets/data/US_Accidents_March23.csv")

""" state_summary = data.group_by('State').agg([
    pl.count("ID").alias("accidents"),
    pl.mean("Severity").alias("avg_severity")
])

state_summary.write_parquet("./assets/data/state_level.parquet") """

""" severity_summary = data.group_by(["State", "Severity"]).len()

all_states = severity_summary.group_by("Severity").agg(
    pl.sum("len").alias("len")
).with_columns(
    pl.lit("All States").alias("State")
)

all_states = all_states.select(severity_summary.columns)

result = pl.concat([severity_summary, all_states])

result.write_parquet("./assets/data/severity_level.parquet") """

data = data.with_columns(
    pl.col("Start_Time")
    .str.strptime(pl.Datetime, strict=False)
    .dt.truncate("1mo")
    .alias("Month")
)

accidents_monthly = data.group_by(['State', 'Month']).agg([
    pl.count("ID").alias("accidents")
])

all_states = accidents_monthly.group_by("Month").agg(
    pl.sum("accidents").alias("accidents")
).with_columns(
    pl.lit("All States").alias("State")
)

all_states = all_states.select(accidents_monthly.columns)

result = pl.concat([accidents_monthly, all_states])
result = result.sort("Month")

result.write_parquet("./assets/data/monthly_accidents.parquet")