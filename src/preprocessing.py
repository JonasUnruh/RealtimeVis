import polars as pl
import pandas as pd
import json

data = pl.read_csv("./src/assets/data/US_Accidents_March23.csv")

data = data.filter([pl.col("Severity").is_not_null(), pl.col("Weather_Condition").is_not_null()])

data = data.with_columns(
    pl.col("Start_Time").str.strptime(pl.Datetime, strict=False).dt.year().alias("Year"),
    pl.col("Start_Time").str.strptime(pl.Datetime, strict=False).dt.month().alias("Month")
)

state_summary = data.group_by(['State', 'Year', 'Month']).agg([
    pl.count("ID").alias("accidents"),
    pl.mean("Severity").alias("avg_severity")
])

state_summary_agg = state_summary.group_by(["State", "Year"]).agg([
    pl.sum("accidents").alias("tot_acc"),
    pl.mean("avg_severity").alias("tot_avg_severity")
])

state_summary = state_summary.join(state_summary_agg, on=["State", "Year"])

all_states = data.group_by(['Year', 'Month']).agg([
    pl.count("ID").alias("accidents"),
    pl.mean("Severity").alias("avg_severity")
]).with_columns(
    pl.lit("USA").alias("State")
)

all_states_agg = all_states.group_by(["Year"]).agg([
    pl.sum("accidents").alias("tot_acc"),
    pl.mean("avg_severity").alias("tot_avg_severity")
])

all_states = all_states.join(all_states_agg, on=["Year"]).select(state_summary.columns)
state_summary = pl.concat([state_summary, all_states])


severity_summary = data.group_by(["State", "Severity", 'Year', 'Month']).agg([
    pl.count("ID").alias("severity_count")
])

severity_summary_agg = severity_summary.group_by(["State", "Severity", "Year"]).agg([
    pl.sum("severity_count").alias("tot_severity")
])

severity_summary = severity_summary.join(severity_summary_agg, on=["State", "Severity", "Year"])

all_states = data.group_by(["Severity", 'Year', 'Month']).agg([
    pl.count("ID").alias("severity_count")
]).with_columns(
    pl.lit("USA").alias("State")
)

all_states_agg = all_states.group_by(["Severity", "Year"]).agg([
    pl.sum("severity_count").alias("tot_severity")
])

all_states = all_states.join(all_states_agg, on=["Severity", "Year"]).select(severity_summary.columns)
severity_summary = pl.concat([severity_summary, all_states])


weather_summary = data.group_by(["State", "Severity", "Weather_Condition", 'Year', 'Month']).agg([
    pl.count("ID").alias("weather_count")
])

weather_summary_agg = weather_summary.group_by(["State", "Severity", "Weather_Condition", "Year"]).agg([
    pl.sum("weather_count").alias("tot_weather_count")
])

weather_summary = weather_summary.join(weather_summary_agg, on=["State", "Severity", "Weather_Condition", "Year"])

all_states = data.group_by(["Severity", "Weather_Condition", 'Year', 'Month']).agg([
    pl.count("ID").alias("weather_count")
]).with_columns(
    pl.lit("USA").alias("State")
)

all_states_agg = all_states.group_by(["Severity", "Weather_Condition", "Year"]).agg([
    pl.sum("weather_count").alias("tot_weather_count")
])

all_states = all_states.join(all_states_agg, on=["Severity", "Weather_Condition", "Year"]).select(weather_summary.columns)
weather_summary = pl.concat([weather_summary, all_states])

result = (
    state_summary
    .join(severity_summary, on=["State", "Year", "Month"])
    .join(weather_summary, on=["State", "Severity", "Year", "Month"])
)

result.write_parquet("./src/assets/data/summary_data.parquet")


with open("./src/assets/data/us-states.json", "r") as f:
    geojson = json.loads(f.read())

county_fp = pd.read_excel("./src/assets/data/US_FIPS_Codes.xls", header=1, dtype={"State": str, "County Name": str, "FIPS State": str, "FIPS County": str})
state_dict = {feature["id"]: feature["properties"]["name"] for feature in geojson["features"]}

states = data.select("State").unique(subset = "State").to_dict()

for state in states["State"]:
    if state not in state_dict.keys():
        continue

    fps = county_fp[county_fp["State"] == state_dict[state]]
    fps["GEO_ID"] = fps["FIPS State"] + fps["FIPS County"]
    fps = pl.from_pandas(fps).select([pl.col("County Name"), pl.col("GEO_ID")])

    state_data = data.filter(pl.col("State") == state).select([pl.col("County"), pl.col("Year"), pl.col("Month"), pl.col("ID"), pl.col("Severity")])

    state_data = state_data.join(fps, left_on="County", right_on="County Name", how="left")

    county_summary = state_data.group_by(["GEO_ID", "County", 'Year', 'Month']).agg([
        pl.count("ID").alias("accidents"),
        pl.mean("Severity").alias("avg_severity")
    ])

    county_severity_summary = state_data.group_by(["GEO_ID", "County", "Severity", 'Year', 'Month']).agg([
        pl.count("ID").alias("severity_count")
    ])

    result = (
        county_summary
        .join(county_severity_summary, on=["GEO_ID", "County", "Year", "Month"])
    )

    result.write_parquet(f"./src/assets/data/{state}_summary_data.parquet") 
