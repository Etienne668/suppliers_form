# Streamlit App with AHP-Driven TOPSIS Ranking (Final Bubble Color Fix)
import streamlit as st
import sqlite3
import uuid
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIG ---
db_path = "supplier_data.db"

# --- DB SETUP ---
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id TEXT PRIMARY KEY,
            name TEXT,
            location_city TEXT,
            location_country TEXT,
            quantity_units REAL,
            price_per_unit REAL,
            unit_weight_kg REAL,
            distance_sea_km REAL,
            distance_road_km REAL,
            distance_air_km REAL,
            delivery_cost_sea REAL,
            delivery_cost_road REAL,
            end_of_life_cost_per_kg REAL,
            emission_factor_prod REAL,
            emission_factor_sea REAL,
            emission_factor_road REAL,
            emission_factor_air REAL,
            emission_factor_eol REAL,
            deforestation_risk TEXT,
            deforestation_score INTEGER,
            reusable TEXT,
            reuse_count REAL,
            return_km REAL,
            recyclability TEXT,
            recycled_materials TEXT,
            total_cost REAL,
            total_emissions REAL,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- INIT ---
init_db()
st.set_page_config(page_title="AHP & TOPSIS Supplier Ranking", layout="wide")
st.title("📈 Supplier Ranking using AHP + TOPSIS")

# --- LOAD DATA ---
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM suppliers ORDER BY created_at DESC", conn)
conn.close()

if df.empty:
    st.warning("No suppliers found. Please enter supplier data first.")
    st.stop()

# --- AHP Pairwise Input ---
st.subheader("🎛 Define AHP Pairwise Preferences")
st.markdown("Rate the importance of one criterion relative to another (1 = equal, 9 = extremely more important)")
criteria = ["Total Cost", "Total Emissions", "Deforestation", "Recyclability"]

# Create pairwise matrix input with sliders
pairwise_matrix = np.ones((4, 4))
labels = [(i, j) for i in range(4) for j in range(i+1, 4)]
for i, j in labels:
    val = st.slider(f"How important is '{criteria[i]}' vs '{criteria[j]}'?", 1, 9, 1)
    pairwise_matrix[i, j] = val
    pairwise_matrix[j, i] = 1 / val

# Compute weights from pairwise matrix using AHP
col_sum = pairwise_matrix.sum(axis=0)
norm_matrix = pairwise_matrix / col_sum
ahp_weights = norm_matrix.mean(axis=1)
st.write("### 🧠 AHP Derived Weights")
st.dataframe(pd.DataFrame({"Criteria": criteria, "Weight": ahp_weights.round(4)}))

# --- TOPSIS PREP ---
st.subheader("🔍 Step 1: Decision Matrix")
df_topsis = df[["name", "total_cost", "total_emissions", "deforestation_score", "recyclability"]].copy()
df_topsis["recyclability_score"] = df_topsis["recyclability"].apply(lambda x: 1 if x == "Yes" else 0)
reverse_map = {1: 3, 2: 2, 3: 1}
df_topsis["deforestation_score_adj"] = df_topsis["deforestation_score"].map(reverse_map)
decision_matrix = df_topsis[["total_cost", "total_emissions", "deforestation_score_adj", "recyclability_score"]].astype(float)
st.dataframe(decision_matrix.style.format("{:.2f}"))

# --- NORMALIZE ---
st.subheader("⚙️ Step 2: Normalized Matrix")
norm_matrix = decision_matrix / np.sqrt((decision_matrix**2).sum())
st.dataframe(norm_matrix.style.format("{:.4f}"))

# --- WEIGHTED MATRIX ---
st.subheader("⚖️ Step 3: Weighted Normalized Matrix (AHP Driven)")
benefit = np.array([False, False, True, True])
weighted_matrix = norm_matrix * ahp_weights.reshape(1, -1)
st.dataframe(weighted_matrix.style.format("{:.4f}"))

# --- IDEAL/NADIR ---
st.subheader("🌟 Step 4: Ideal & Negative-Ideal Solutions")
criteria_labels = ["Total Cost", "Total Emissions", "Deforestation", "Recyclability"]
v_ideal = pd.Series(np.where(benefit, weighted_matrix.max(), weighted_matrix.min()), index=criteria_labels)
v_neg = pd.Series(np.where(benefit, weighted_matrix.min(), weighted_matrix.max()), index=criteria_labels)
st.dataframe(v_ideal.rename("Ideal Value"))
st.dataframe(v_neg.rename("Negative-Ideal Value"))

# --- DISTANCES ---
st.subheader("📏 Step 5: Distance to Ideal/Nadir")
distance_pos = np.sqrt(((weighted_matrix - v_ideal.values) ** 2).sum(axis=1))
distance_neg = np.sqrt(((weighted_matrix - v_neg.values) ** 2).sum(axis=1))
st.dataframe(pd.DataFrame({"Supplier": df_topsis["name"], "Distance to Ideal": distance_pos, "Distance to Nadir": distance_neg}))

# --- CLOSENESS ---
st.subheader("📊 Step 6: Closeness Score and Ranking")
closeness = distance_neg / (distance_pos + distance_neg)
df_topsis["TOPSIS Score"] = closeness
df_topsis["Rank"] = df_topsis["TOPSIS Score"].rank(ascending=False).astype(int)
df_topsis_sorted = df_topsis.sort_values("Rank")
st.dataframe(df_topsis_sorted[["name", "TOPSIS Score", "Rank"]])

# --- BUBBLE CHART ---
st.subheader("🎯 Visualization: Cost vs Emissions Bubble Chart")

def get_color(score):
    if score == 3:
        return 'red'       # High Risk
    elif score == 2:
        return 'orange'    # Medium Risk
    else:
        return 'green'     # Low Risk

colors = df["deforestation_score"].apply(get_color)
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df["total_emissions"], df["total_cost"], s=200, alpha=0.6, edgecolors='w', c=colors, marker='o')
for _, row in df.iterrows():
    ax.text(row["total_emissions"] + 0.05, row["total_cost"], row["name"], fontsize=9)

legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', label='High Deforestation Risk', markerfacecolor='red', markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='Medium Deforestation Risk', markerfacecolor='orange', markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='Low Deforestation Risk', markerfacecolor='green', markersize=10)
]
ax.legend(handles=legend_elements, title="Deforestation Risk")
ax.set_xlabel("Total Emissions (kg CO₂)")
ax.set_ylabel("Total Cost (€)")
ax.set_title("Supplier Cost vs Emissions (Bubble Color = Deforestation Risk)")
ax.grid(True)
st.pyplot(fig)
