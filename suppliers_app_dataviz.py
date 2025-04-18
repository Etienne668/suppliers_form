# Streamlit Supplier App with Circularity and Bubble Chart
import streamlit as st
import sqlite3
import uuid
from datetime import datetime
import pandas as pd
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

# --- SAVE TO DB ---
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

# --- INIT ---
init_db()
st.set_page_config(page_title="Supplier Tracker", layout="wide")
st.title("🌍 Supplier Cost & Emissions Tracker")

# --- SUPPLIER FORM ---
st.subheader("📋 Enter Supplier Information")
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
    deforestation_score = 3 if deforestation_risk == "High" else 2 if deforestation_risk == "Medium" else 1

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

# --- DATAFRAME + VISUAL ---
st.markdown("---")
st.subheader("📊 All Supplier Entries")
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM suppliers ORDER BY created_at DESC", conn)
conn.close()
st.dataframe(df, use_container_width=True)

# --- Bubble Chart ---
st.markdown("### 🎯 Supplier Cost vs Emissions Bubble Chart")
if not df.empty:
    def get_color(score):
        if score == 3:
            return 'red'
        elif score == 2:
            return 'orange'
        else:
            return 'green'

    df["color"] = df["deforestation_score"].apply(get_color)

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        df["total_emissions"],
        df["total_cost"],
        s=200,
        alpha=0.6,
        edgecolors='w',
        c=df["color"],
        marker='o'
    )

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
else:
    st.info("No data available to visualize yet. Please add suppliers.")
