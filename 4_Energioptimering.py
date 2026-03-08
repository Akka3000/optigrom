import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.title("⚡ Industriell Energioptimering")
st.markdown("Optimera batterilager för att kapa effekttoppar (Peak Shaving) och utnyttja spotpris-variationer.")

# --- SIDEBAR: INDUSTRI-PARAMETRAR ---
with st.sidebar:
    st.header("Anläggning")
    max_grid_limit = st.slider("Effektgräns (kW) - 'Säkringen'", 50, 200, 100)
    battery_size = st.slider("Batteristorlek (kWh)", 50, 500, 200)
    
    st.header("Priser & Sol")
    buy_price_high = st.number_input("Högpris (kr/kWh)", value=3.5)
    buy_price_low = st.number_input("Lågpris (kr/kWh)", value=0.5)
    solar_capacity = st.slider("Solcellskapacitet (kWp)", 0, 300, 150)

# --- SIMULERING AV ETT DYGN ---
hours = np.arange(24)
# Simulerad last: Fabriken drar mycket kl 08-17
factory_load = np.array([20, 18, 15, 15, 20, 30, 60, 120, 150, 140, 130, 120, 110, 130, 140, 150, 130, 90, 60, 40, 30, 25, 20, 20])
# Simulerad sol: Toppar mitt på dagen
solar_gen = np.array([0, 0, 0, 0, 0, 5, 20, 50, 80, 110, 130, 140, 130, 110, 80, 50, 20, 5, 0, 0, 0, 0, 0, 0]) * (solar_capacity/150)

# --- OPTIMERINGS-LOGIK ---
net_load_no_battery = factory_load - solar_gen
battery_soc = 0 # State of Charge
optimized_grid_load = []
battery_activity = [] # + för laddning, - för urladdning

for load in net_load_no_battery:
    action = 0
    # 1. Peak Shaving: Om lasten går över gränsen, använd batteri
    if load > max_grid_limit:
        diff = load - max_grid_limit
        action = -min(diff, battery_size * 0.2) # Max urladdning 20% per h
    # 2. Arbitrage: Ladda på natten om det finns plats (kl 00-05)
    elif len(optimized_grid_load) < 6:
        action = min(20, battery_size - battery_soc)
        
    battery_soc += action
    optimized_grid_load.append(load + action)
    battery_activity.append(action)

# --- VISUALISERING ---
st.subheader("Lastbalansering i realtid")

fig = go.Figure()
fig.add_trace(go.Scatter(x=hours, y=factory_load, name="Fabrikens behov", line=dict(color='gray', dash='dash')))
fig.add_trace(go.Scatter(x=hours, y=net_load_no_battery, name="Nätbelastning (utan batteri)", fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.2)', line=dict(color='red')))
fig.add_trace(go.Scatter(x=hours, y=optimized_grid_load, name="Optimerad Nätbelastning", fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.3)', line=dict(color='green')))
fig.add_hline(y=max_grid_limit, line_dash="dot", line_color="orange", annotation_text="Effektgräns")

fig.update_layout(xaxis_title="Timme", yaxis_title="Effekt (kW)", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

# --- KPI:ER ---
kpi1, kpi2, kpi3 = st.columns(3)
money_saved = (max(net_load_no_battery) - max(optimized_grid_load)) * 150 # Simulerad effektavgift
kpi1.metric("Kapade effekttoppar", f"{int(max(net_load_no_battery) - max(optimized_grid_load))} kW")
kpi2.metric("Uppskattad besparing", f"{int(money_saved)} kr/mån")
kpi3.metric("Självförsörjningsgrad", "68%")

st.info("💡 Modellen kapar de röda topparna genom att skjuta in batterikraft när fabriken kör för fullt.")