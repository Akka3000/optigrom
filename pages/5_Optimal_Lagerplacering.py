import streamlit as st
import pulp
import matplotlib.pyplot as plt
import geopandas as gpd
from geopy.geocoders import Nominatim
import numpy as np

# --- 1. SETUP & GEOLOCATOR ---
st.set_page_config(page_title="Strategisk Nätverksdesign", layout="wide")
geolocator = Nominatim(user_agent="my_logistics_app_v1")

# --- 2. DATA: MÖJLIGA LAGERPLATSER (HUBBAR) ---
# Här kan du fylla på med 100 städer om du vill. 
if 'potential_hubs' not in st.session_state:
    st.session_state.potential_hubs = {
        "Göteborg": (11.97, 57.70), "Berlin": (13.40, 52.52), "Paris": (2.35, 48.86),
        "Warszawa": (21.01, 52.23), "Madrid": (-3.70, 40.41), "Rotterdam": (4.47, 51.92),
        "Hamburg": (9.99, 53.55), "Milano": (9.18, 45.46), "Lyon": (4.83, 45.76)
    }

# --- 3. DATA: MARKNADER (KUNDER) ---
if 'markets' not in st.session_state:
    st.session_state.markets = {
        "Stockholm": {"pos": (18.06, 59.33), "demand": 10},
        "Malmö": {"pos": (13.00, 55.60), "demand": 15},
        "London": {"pos": (-0.12, 51.50), "demand": 25},
        "Oslo": {"pos": (10.75, 59.91), "demand": 20},
        "Helsingfors": {"pos": (24.94, 60.16), "demand": 12},
        "Köpenhamn": {"pos": (12.56, 55.67), "demand": 18}
    }

# --- 4. SIDEBAR: LÄGG TILL MARKNAD AUTOMATISKT ---
st.sidebar.header("➕ Lägg till ny Marknad/Kund")
new_city_name = st.sidebar.text_input("Stadens namn (t.ex. 'New Delhi' eller 'Kiruna')")

if st.sidebar.button("Hämta & Lägg till"):
    try:
        location = geolocator.geocode(new_city_name)
        if location:
            st.session_state.markets[new_city_name] = {
                "pos": (location.longitude, location.latitude), 
                "demand": 10
            }
            st.success(f"Lade till {new_city_name}!")
            st.rerun()
        else:
            st.error("Hittade inte staden. Kolla stavningen.")
    except:
        st.error("Tjänsten är upptagen, försök igen om en sekund.")

# --- 5. SIDEBAR: INSTÄLLNINGAR ---
st.sidebar.divider()
st.sidebar.header("⚙️ Inställningar")
dist_cost = st.sidebar.slider("Transportkostnad (kr/km/ton)", 0.5, 10.0, 1.0, step=0.5)

st.sidebar.divider()
st.sidebar.subheader("📦 Hantera Marknader & Efterfrågan")

# Vi loopar igenom alla städer i session_state
for city in list(st.session_state.markets.keys()):
    # Skapar en ram för varje stad för att hålla ordning
    with st.sidebar.container():
        col1, col2 = st.columns([4, 1])
        
        # Kolumn 1: Ändra efterfrågan
        with col1:
            st.session_state.markets[city]["demand"] = st.number_input(
                f"Efterfrågan {city} (ton)", 
                value=int(st.session_state.markets[city]["demand"]), 
                step=5, 
                min_value=0,
                key=f"demand_input_{city}" # Unikt ID för varje stad
            )
        
        # Kolumn 2: Radera-knapp
        with col2:
            st.write(" ") # Padding för att linjera med rutan ovanför
            if st.button("🗑️", key=f"del_{city}"):
                del st.session_state.markets[city]
                st.rerun() # Uppdaterar kartan direkt
        st.sidebar.write("---") # Liten linje mellan städerna

# Välj vilka hubbar som ska vara "aktiva" kandidater i denna körning
active_hubs = st.sidebar.multiselect(
    "Möjliga lagerplatser", 
    options=list(st.session_state.potential_hubs.keys()),
    default=list(st.session_state.potential_hubs.keys())[:5]
)

# Fasta kostnader för de aktiva hubbarna
fixed_costs = {h: st.sidebar.number_input(f"Fast kostnad {h}", value=500000, step=50000, min_value=0) for h in active_hubs}

# --- 6. OPTIMERING ---
def get_dist_km(p1, p2):
    R = 6371
    dLat, dLon = np.radians(p2[1]-p1[1]), np.radians(p2[0]-p1[0])
    a = np.sin(dLat/2)**2 + np.cos(np.radians(p1[1])) * np.cos(np.radians(p2[1])) * np.sin(dLon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))

prob = pulp.LpProblem("Network_Design", pulp.LpMinimize)
y = pulp.LpVariable.dicts("Open", active_hubs, cat=pulp.LpBinary)
x = pulp.LpVariable.dicts("Flow", (active_hubs, st.session_state.markets.keys()), cat=pulp.LpBinary)

# Målfunktion
prob += pulp.lpSum([fixed_costs[h] * y[h] for h in active_hubs]) + \
        pulp.lpSum([get_dist_km(st.session_state.potential_hubs[h], st.session_state.markets[m]["pos"]) * st.session_state.markets[m]["demand"] * dist_cost * x[h][m] 
                    for h in active_hubs for m in st.session_state.markets])

for m in st.session_state.markets:
    prob += pulp.lpSum([x[h][m] for h in active_hubs]) == 1
for h in active_hubs:
    for m in st.session_state.markets:
        prob += x[h][m] <= y[h]

prob.solve(pulp.PULP_CBC_CMD(msg=0))

# --- 7. KARTA ---
fig, ax = plt.subplots(figsize=(10, 7))
world_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
try:
    world = gpd.read_file(world_url)
    world.plot(ax=ax, color='#2c3e50', edgecolor='grey', alpha=0.1)
except:
    ax.set_facecolor('#f0f2f6')

# Rita flöden
for h in active_hubs:
    if pulp.value(y[h]) == 1:
        for m in st.session_state.markets:
            if pulp.value(x[h][m]) == 1:
                h_p = st.session_state.potential_hubs[h]
                m_p = st.session_state.markets[m]["pos"]
                ax.plot([h_p[0], m_p[0]], [h_p[1], m_p[1]], color='#e74c3c', linewidth=1.5, alpha=0.6)

# Rita noder
for m, info in st.session_state.markets.items():
    ax.scatter(info["pos"][0], info["pos"][1], c='#34495e', s=40, zorder=3)
    ax.text(info["pos"][0], info["pos"][1]-1, m, fontsize=7)

for h in active_hubs:
    if pulp.value(y[h]) == 1:
        h_pos = st.session_state.potential_hubs[h]
        ax.scatter(h_pos[0], h_pos[1], c='#e74c3c', s=150, marker='s', edgecolors='white', zorder=4)

# Dynamisk zoom: Anpassa efter alla punkter
all_lons = [p["pos"][0] for p in st.session_state.markets.values()] + [p[0] for p in st.session_state.potential_hubs.values()]
all_lats = [p["pos"][1] for p in st.session_state.markets.values()] + [p[1] for p in st.session_state.potential_hubs.values()]
ax.set_xlim(min(all_lons)-5, max(all_lons)+5)
ax.set_ylim(min(all_lats)-5, max(all_lats)+5)
ax.set_axis_off()
st.pyplot(fig)

st.metric("Total Systemkostnad", f"{int(pulp.value(prob.objective)):,} kr".replace(",", " "))