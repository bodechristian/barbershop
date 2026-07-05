from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# configurables
MIN_FINISHES = 7
YEAR_START = 1970
YEAR_END = 2026

# constants
PATH_FOLDER = Path("top10scores")

records = []
for file in sorted(PATH_FOLDER.glob("*.tsv")):
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
results["hover_text"] = (results["place"].astype(str) + ". place")
final_counts = (
    results.groupby("quartet")["top10s"]
    .max()
    .sort_values(ascending=False)
)
keep_quartets = final_counts[final_counts >= MIN_FINISHES].index
results = results[results["quartet"].isin(keep_quartets)]

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
        line={'shape': 'hv'},
        customdata=g["hover_text"],
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{customdata}<br>"
            "Top 10s: %{y}<extra></extra>"
        ),
    ))

## Markers for Gold, Silver, Bronze medals
gold = results[results["place"] == 1].copy()
silver = results[results["place"] == 2].copy()
bronze = results[results["place"].between(3, 5)].copy()
fig.add_trace(go.Scatter(
    x=bronze["year"],
    y=bronze["top10s"],
    mode="markers+text",
    text="🎖",
    textfont=dict(size=16),
    textposition="top center",
    marker=dict(size=1, opacity=0),
    name="Bronze (3.-5.)",
    hoverinfo="skip",
    showlegend=True,
    visible="legendonly"
))
fig.add_trace(go.Scatter(
    x=silver["year"],
    y=silver["top10s"],
    mode="markers+text",
    text="🥈",
    textfont=dict(size=20),
    textposition="top center",
    marker=dict(size=1, opacity=0),
    name="Silver",
    hoverinfo="skip",
    showlegend=True,
    visible="legendonly"
))
fig.add_trace(go.Scatter(
    x=gold["year"],
    y=gold["top10s"],
    mode="markers+text",
    text="🥇",
    textfont=dict(size=24),
    textposition="top center",
    marker=dict(size=1, opacity=0),
    name="Gold",
    hoverinfo="skip",
    showlegend=True
))

fig.update_layout(
    title=f"Quartets with at least {MIN_FINISHES} top10 finishes",
    xaxis_title="Year",
    yaxis_title="Career Top 10 finishes",
    legend_title="Quartet (Top 10s)",
    hovermode="x unified"
)

fig.update_xaxes(
    range=[results["year"].min() - 1, results["year"].max() + 1]
)
fig.update_traces(line=dict(width=2))

fig.show()

## Use this to save the image
# fig.write_image(
#     "min7since1970.png",
#     width=1600,
#     height=900,
#     scale=2
# )
