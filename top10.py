from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


folder = Path("top10scores")

records = []

for file in sorted(folder.glob("*.txt")):
    year = int(file.stem)

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

# Sort chronologically
results = results.sort_values("year")

# cumulative top-10 count per quartet
results["top10s"] = results.groupby("quartet").cumcount() + 1

# final counts per quartet
final_counts = (
    results.groupby("quartet")["top10s"]
    .max()
    .sort_values(ascending=False)
)

min_finishes = 7
keep_quartets = final_counts[final_counts >= min_finishes].index

results = results[results["quartet"].isin(keep_quartets)]

# ---- PLOTLY ----
fig = go.Figure()

# iterate in sorted order (IMPORTANT for legend order)
for quartet in final_counts.loc[keep_quartets].index:
    g = results[results["quartet"] == quartet]

    fig.add_trace(go.Scatter(
        x=g["year"],
        y=g["top10s"],
        mode="lines",
        name=f"{quartet} ({final_counts[quartet]})",
        hovertemplate=(
            f"{quartet}<br>"
            "Year: %{x}<br>"
            "Top 10s: %{y}<extra></extra>"
        ),
        line_shape="hv"
    ))

fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Career Top 10 finishes",
    legend_title="Quartet (Top 10s)",
)

fig.update_xaxes(
    range=[results["year"].min() - 1, results["year"].max() + 1]
)

fig.show()
