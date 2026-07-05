from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

MIN_FINISHES = 7
PATH_FOLDER = Path("top10scores")

YEAR_START = 1970
YEAR_END = 2026

records = []

for file in sorted(PATH_FOLDER.glob("*.txt")):
    year = int(file.stem)

    if not (YEAR_START <= year <= YEAR_END):
        continue

    df = pd.read_csv(file, sep="\t", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    # Keep only top 10
    df = df[df["Place"] <= 10]

    for _, row in df.iterrows():
        records.append({
            "year": year,
            "quartet": row["Quartet"],
            "place": row["Place"]
        })

results = pd.DataFrame(records)

## Get Quartets to display
results = results.sort_values("year")
results["top10s"] = results.groupby("quartet").cumcount() + 1
results["hover_text"] = (results["year"].astype(str) + " — " + results["place"].astype(str) + ". place")
final_counts = (
    results.groupby("quartet")["top10s"]
    .max()
    .sort_values(ascending=False)
)
keep_quartets = final_counts[final_counts >= MIN_FINISHES].index
results = results[results["quartet"].isin(keep_quartets)]

## Get Winners for event markers
last_rows = results.sort_values("year").groupby("quartet").tail(1)
winners = last_rows[last_rows["place"] == 1]

# ---- PLOTLY ----
fig = go.Figure()

## Display quartets
# iterate in sorted order (IMPORTANT for legend order)
for quartet in final_counts.loc[keep_quartets].index:
    g = results[results["quartet"] == quartet]

    fig.add_trace(go.Scatter(
        x=g["year"],
        y=g["top10s"],
        mode="lines",
        name=f"{quartet} ({final_counts[quartet]})",
        line_shape="hv",
        customdata=g["hover_text"],
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{customdata}<br>"
            "Career Top 10s: %{y}<extra></extra>"
        ),
    ))

## Event markers for winning years
fig.add_trace(go.Scatter(
    x=winners["year"],
    y=winners["top10s"],
    mode="markers",
    name="Championship finish",
    marker=dict(
        symbol="star",
        size=14,
        color="gold",
        line=dict(width=1, color="black")
    ),
    hovertemplate=(
        "🏆 %{customdata}<br>"
        "Year: %{x}<br>"
        "Final Top 10 #: %{y}<extra></extra>"
    ),
    customdata=winners["quartet"]
))

fig.update_layout(
    title=f"Quartets with at least {MIN_FINISHES} top10 finishes",
    xaxis_title="Year",
    yaxis_title="Career Top 10 finishes",
    legend_title="Quartet (Top 10s)",
)

fig.update_xaxes(
    range=[results["year"].min() - 1, results["year"].max() + 1]
)
fig.update_traces(line=dict(width=2))

fig.show()
