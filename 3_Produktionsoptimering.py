import streamlit as st
import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, value
import plotly.express as px

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.title("⚙️ Avancerad Produktmix-Optimering")
st.markdown("Hitta den mest lönsamma mixen av 5 produkter med hänsyn till kapacitet och minimikrav.")

# --- INPUTS I SIDEBAR ---
with st.sidebar:
    st.header("Total Kapacitet")
    total_hours = st.number_input("Tillgängliga arbetstimmar", value=500, step=50)
    
    # Setup för 5 produkter
    prod_data = {
        "Mobil": {"vinst": 1200, "tid": 2.0, "min": 10},
        "Laptop": {"vinst": 3500, "tid": 5.0, "min": 5},
        "Läsplatta": {"vinst": 800, "tid": 1.5, "min": 0},
        "Klocka": {"vinst": 1500, "tid": 3.0, "min": 0},
        "Hörlurar": {"vinst": 400, "tid": 0.5, "min": 20}
    }
    
    user_inputs = {}
    for name, defaults in prod_data.items():
        st.subheader(f"📦 {name}")
        p = st.number_input(f"Vinst ({name})", value=defaults["vinst"], key=f"p_{name}")
        t = st.number_input(f"Tid per enhet (h)", value=defaults["tid"], key=f"t_{name}")
        m = st.number_input(f"Minsta antal att producera", value=defaults["min"], key=f"m_{name}")
        user_inputs[name] = {"vinst": p, "tid": t, "min": m}

# --- OPTIMERING ---
model = LpProblem(name="Product-Mix", sense=LpMaximize)

# Skapa variabler (x_Mobil, x_Laptop, etc)
vars = {name: LpVariable(name=f"x_{name}", lowBound=user_inputs[name]["min"], cat="Integer") 
        for name in user_inputs}

# Målfunktion: Maximera total vinst
model += sum(vars[name] * user_inputs[name]["vinst"] for name in user_inputs)

# Bivillkor: Total tid får inte överskrida kapaciteten
model += sum(vars[name] * user_inputs[name]["tid"] for name in user_inputs) <= total_hours

# Lös
model.solve()

# --- RESULTAT ---
if model.status == 1: # 1 betyder "Optimal"
    results = []
    for name in user_inputs:
        qty = int(vars[name].varValue)
        results.append({
            "Produkt": name,
            "Antal": qty,
            "Vinstbidrag": qty * user_inputs[name]["vinst"],
            "Tidsåtgång": qty * user_inputs[name]["tid"]
        })
    
    df_res = pd.DataFrame(results)
    total_profit = value(model.objective)
    total_used_hours = df_res["Tidsåtgång"].sum()

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Vinst", f"{int(total_profit):,} kr")
    c2.metric("Tid utnyttjad", f"{total_used_hours} / {total_hours} h")
    c3.metric("Mest lönsam", df_res.loc[df_res['Vinstbidrag'].idxmax(), 'Produkt'])

    # Grafer
    col_left, col_right = st.columns(2)
    
    with col_left:
        fig_qty = px.bar(df_res, x="Produkt", y="Antal", title="Antal per produkt", color="Produkt")
        st.plotly_chart(fig_qty, use_container_width=True)
        
    with col_right:
        fig_profit = px.pie(df_res, values="Vinstbidrag", names="Produkt", title="Vinstfördelning")
        st.plotly_chart(fig_profit, use_container_width=True)

    st.success(f"✅ Optimeringen klar! Du har uppfyllt alla minimikrav och maximerat resterande tid för de mest lönsamma produkterna.")
else:
    st.error("❌ Det går inte att lösa! Du har förmodligen satt för höga minimikrav för den tid du har tillgänglig.")