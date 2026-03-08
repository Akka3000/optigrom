import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.set_page_config(page_title="Lageroptimering", page_icon="📦")

st.title("📦 Lageroptimering: EOQ-analys")
st.markdown("""
Denna modell räknar ut **Economic Order Quantity (EOQ)**. 
Målet är att hitta den orderkvantitet som minimerar de totala kostnaderna för inköp och lagerhållning.
""")

# --- INPUTS ---
st.sidebar.header("Parametrar")
demand = st.sidebar.number_input("Årlig efterfrågan (st)", value=5000, step=100)
order_cost = st.sidebar.number_input("Kostnad per order (kr)", value=200, step=10)
holding_cost = st.sidebar.number_input("Lagerkostnad per styck/år (kr)", value=5.0, step=0.5)

# --- MATEMATIK ---
# Formel: sqrt((2 * efterfrågan * orderkostnad) / lagerkostnad)
if holding_cost > 0:
    eoq = np.sqrt((2 * demand * order_cost) / holding_cost)
    total_cost = (demand / eoq * order_cost) + (eoq / 2 * holding_cost)
    
    # --- RESULTAT ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Optimal orderkvantitet", f"{int(eoq)} st")
    col2.metric("Antal ordrar per år", f"{round(demand/eoq, 1)}")
    col3.metric("Total årlig kostnad", f"{int(total_cost)} kr")

    # --- GRAF ---
    # Skapa data för att rita kurvorna
    q_range = np.linspace(max(1, int(eoq*0.2)), int(eoq*2), 100)
    df_plot = pd.DataFrame({
        'Orderstorlek': q_range,
        'Orderkostnader': (demand / q_range) * order_cost,
        'Lagerhållningskostnader': (q_range / 2) * holding_cost
    })
    df_plot['Total kostnad'] = df_plot['Orderkostnader'] + df_plot['Lagerhållningskostnader']

    st.subheader("Kostnadsanalys")
    fig = px.line(df_plot, x='Orderstorlek', y=['Orderkostnader', 'Lagerhållningskostnader', 'Total kostnad'],
                  labels={'value': 'Kostnad (kr)', 'variable': 'Typ'},
                  title="Hitta lägsta punkten på totalkostnadskurvan")
    
    # Lägg till en punkt för EOQ
    fig.add_vline(x=eoq, line_dash="dash", line_color="green", annotation_text="Optimalt")
    
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"💡 Genom att beställa **{int(eoq)} enheter** åt gången minimerar du krocken mellan dyra orderavgifter och dyra lagerhyllor.")

else:
    st.error("Lagerkostnaden måste vara högre än 0.")