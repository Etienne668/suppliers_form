import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import uuid

# --- CONFIG ---
db_path = "supplier_data.db"
st.set_page_config(page_title="Supplier Evaluation", layout="wide")

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

init_db()

# --- SAVE FUNCTION ---
def save_supplier(data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO suppliers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(uuid.uuid4()),
        data['name'],
        data['location_city'],
        data['location_country'],
        data['quantity_units'],
        data['price_per_unit'],
        data['unit_weight_kg'],
        data['distance_sea_km'],
        data['distance_road_km'],
        data['distance_air_km'],
        data['delivery_cost_sea'],
        data['delivery_cost_road'],
        data['end_of_life_cost_per_kg'],
        data['emission_factor_prod'],
        data['emission_factor_sea'],
        data['emission_factor_road'],
        data['emission_factor_air'],
        data['emission_factor_eol'],
        data['deforestation_risk'],
        data['deforestation_score'],
        data['reusable'],
        data['reuse_count'],
        data['return_km'],
        data['recyclability'],
        data['recycled_materials'],
        data['total_cost'],
        data['total_emissions'],
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

# --- MAIN APP ---
tabs = st.tabs(["📋 Supplier Form & Visualization", "📊 AHP & TOPSIS Supplier Ranking"])

with tabs[0]:
    st.title("📋 Supplier Form & Visualization")

    with st.form("supplier_form"):
        st.markdown("### 🧾 General Information")
        name = st.text_input("Supplier Name")
        location_city = st.text_input("City")
        location_country = st.text_input("Country")

        st.markdown("### 💰 Cost")
        quantity_units = st.number_input("Quantity (units)", min_value=0.0)
        price_per_unit = st.number_input("Price per Unit (€)", min_value=0.0)
        unit_weight_kg = st.number_input("Weight per Unit (kg)", min_value=0.0)
        delivery_cost_sea = st.number_input("Sea Delivery Cost (€/km)", min_value=0.0)
        delivery_cost_road = st.number_input("Road Delivery Cost (€/km)", min_value=0.0)
        end_of_life_cost_per_kg = st.number_input("End-of-Life Cost (€/kg)", min_value=0.0)

        st.markdown("### ♻️ Circularity Performance")
        col1, col2 = st.columns(2)
        with col1:
            reusable = st.selectbox("Reusable", ["No", "Yes"])
        with col2:
            recyclability = st.selectbox("Recyclability", ["No", "Yes"])
        recycled_materials = st.selectbox("Recycled Materials", ["No", "Yes"])

        reuse_count = 0.0
        return_km = 0.0
        if reusable == "Yes":
            reuse_count = st.number_input("Number of times used", min_value=1.0)
            return_km = st.number_input("KM to return point", min_value=0.0)

        st.markdown("### 🧭 Distances")
        distance_sea_km = st.number_input("Distance by Sea (km)", min_value=0.0)
        distance_road_km = st.number_input("Distance by Road (km)", min_value=0.0)
        distance_air_km = st.number_input("Distance by Air (km)", min_value=0.0)

        st.markdown("### 🌱 Environmental Factors")
        emission_factor_prod = st.number_input("EF Production (kg CO2/unit)", min_value=0.0)
        emission_factor_sea = st.number_input("EF Sea (kg CO2/tonne.km)", min_value=0.0)
        emission_factor_road = st.number_input("EF Road (kg CO2/tonne.km)", min_value=0.0)
        emission_factor_air = st.number_input("EF Air (kg CO2/tonne.km)", min_value=0.0)
        emission_factor_eol = st.number_input("EF End-of-Life (kg CO2/unit)", min_value=0.0)

        deforestation_risk = st.selectbox("Deforestation Risk", ["Low", "Medium", "High"])
        deforestation_score = 1 if deforestation_risk == "Low" else 2 if deforestation_risk == "Medium" else 3

        submitted = st.form_submit_button("Submit Supplier")

        if submitted:
            total_weight_kg = unit_weight_kg * quantity_units
            total_weight_tonnes = total_weight_kg / 1000.0

            adjusted_distance_road_km = distance_road_km
            adjusted_emission_factor_prod = emission_factor_prod
            if reusable == "Yes" and reuse_count and return_km:
                adjusted_distance_road_km += reuse_count * return_km
                adjusted_emission_factor_prod = emission_factor_prod / reuse_count

            total_cost = (
                quantity_units * price_per_unit +
                distance_sea_km * delivery_cost_sea +
                adjusted_distance_road_km * delivery_cost_road +
                end_of_life_cost_per_kg * total_weight_kg
            )

            total_emissions = (
                adjusted_emission_factor_prod * quantity_units +
                emission_factor_sea * total_weight_tonnes * distance_sea_km +
                emission_factor_road * total_weight_tonnes * adjusted_distance_road_km +
                emission_factor_air * total_weight_tonnes * distance_air_km +
                emission_factor_eol * quantity_units
            )

            data = {
                'name': name,
                'location_city': location_city,
                'location_country': location_country,
                'quantity_units': quantity_units,
                'price_per_unit': price_per_unit,
                'unit_weight_kg': unit_weight_kg,
                'distance_sea_km': distance_sea_km,
                'distance_road_km': adjusted_distance_road_km,
                'distance_air_km': distance_air_km,
                'delivery_cost_sea': delivery_cost_sea,
                'delivery_cost_road': delivery_cost_road,
                'end_of_life_cost_per_kg': end_of_life_cost_per_kg,
                'emission_factor_prod': adjusted_emission_factor_prod,
                'emission_factor_sea': emission_factor_sea,
                'emission_factor_road': emission_factor_road,
                'emission_factor_air': emission_factor_air,
                'emission_factor_eol': emission_factor_eol,
                'deforestation_risk': deforestation_risk,
                'deforestation_score': deforestation_score,
                'reusable': reusable,
                'reuse_count': reuse_count,
                'return_km': return_km,
                'recyclability': recyclability,
                'recycled_materials': recycled_materials,
                'total_cost': total_cost,
                'total_emissions': total_emissions
            }

            save_supplier(data)
            st.success(f"✅ Saved! Total Cost: €{total_cost:.2f} | Emissions: {total_emissions:.2f} kg CO2")

    st.markdown("---")
    st.subheader("📊 All Supplier Entries")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM suppliers ORDER BY created_at DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.markdown("### 🎯 Bubble Chart")
        color_map = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}
        fig, ax = plt.subplots()
        for i, row in df.iterrows():
            ax.scatter(row['total_emissions'], row['total_cost'],
                       s=100, color=color_map.get(row['deforestation_risk'], 'gray'))
            ax.text(row['total_emissions'], row['total_cost'], row['name'], fontsize=9)
        ax.set_xlabel("Total CO2 Emissions (kg)")
        ax.set_ylabel("Total Cost (€)")
        st.pyplot(fig)

with tabs[1]:
    st.title("📊 AHP + TOPSIS Supplier Ranking")
    st.markdown("AHP-weighted TOPSIS ranking of suppliers.")

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM suppliers", conn)
    conn.close()

    if df.empty:
        st.warning("No suppliers found. Please enter supplier data first.")
    else:
        st.subheader("🔧 AHP Pairwise Comparisons")
        criteria = ["Total Cost", "Total Emissions", "Deforestation", "Recyclability"]

        matrix = []
        for i, ci in enumerate(criteria):
            row = []
            for j, cj in enumerate(criteria):
                if i == j:
                    row.append(1.0)
                elif j < i:
                    row.append(1 / matrix[j][i])
                else:
                    row.append(st.slider(f"How much more important is '{ci}' over '{cj}'?", 1/9.0, 9.0, 1.0, key=f"{ci}_{cj}"))
            matrix.append(row)

        matrix = np.array(matrix)
        ahp_weights = np.mean(matrix / matrix.sum(axis=0), axis=1)
        ahp_weights /= ahp_weights.sum()
        weights_df = pd.DataFrame({"Criterion": criteria, "Weight": ahp_weights})
        st.write("### Calculated Weights (AHP)")
        st.dataframe(weights_df)

        matrix_data = df[["total_cost", "total_emissions", "deforestation_score", "recyclability"]].copy()
        matrix_data["recyclability"] = matrix_data["recyclability"].apply(lambda x: 1 if x == "Yes" else 0)

        st.write("### Raw Decision Matrix")
        st.dataframe(matrix_data)

        norm_matrix = matrix_data / np.sqrt((matrix_data**2).sum())
        st.write("### Normalized Matrix")
        st.dataframe(norm_matrix)

        weighted_matrix = norm_matrix * ahp_weights
        st.write("### Weighted Normalized Matrix")
        st.dataframe(weighted_matrix)

        ideal = weighted_matrix.max()
        nadir = weighted_matrix.min()
        st.write("### Ideal Solutions")
        st.dataframe(pd.DataFrame({"Criterion": criteria, "Ideal": ideal.values, "Nadir": nadir.values}))

        d_pos = np.sqrt(((weighted_matrix - ideal)**2).sum(axis=1))
        d_neg = np.sqrt(((weighted_matrix - nadir)**2).sum(axis=1))
        scores = d_neg / (d_pos + d_neg)
        ranking = df[["name"]].copy()
        ranking["Score"] = scores
        ranking = ranking.sort_values("Score", ascending=False).reset_index(drop=True)

        st.success("### ✅ Supplier Ranking")
        st.dataframe(ranking)
