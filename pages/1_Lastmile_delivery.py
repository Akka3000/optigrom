import streamlit as st
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
import pulp
import numpy as np
import requests
import time

# --- SETUP & UI ---
st.set_page_config(page_title="IndustriOpt - Last Mile", layout="wide")
geolocator = Nominatim(user_agent="industri_optimizer_v2")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

st.title("🚛 IndustriOpt: Last Mile Delivery v2.0")
st.markdown("Optimering baserad på **verkliga vägavstånd** (OSRM)")

# --- INPUT SEKTION ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Konfiguration")
    depot_addr = st.text_input("Depå (Start & Slut)", "Hamngatan 1, Stockholm")
    cust_addrs = st.text_area("Kunders adresser (en per rad)", 
                             "Sveavägen 10, Stockholm\nVasagatan 1, Stockholm\nKungsgatan 5, Stockholm\nStureplan 1, Stockholm")
    
    st.info("Modellen minimerar total körsträcka längs faktiska vägar.")

# --- FUNKTIONER ---
def get_distance_matrix(df):
    """Hämtar hela vägmatrisen i ett anrop via OSRM Table API"""
    coords = ";".join([f"{lon},{lat}" for lat, lon in zip(df['lat'], df['lon'])])
    url = f"http://router.project-osrm.org/table/v1/driving/{coords}?annotations=distance"
    
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data['code'] == 'Ok':
            # Distanserna kommer i meter, vi konverterar till km
            return np.array(data['distances']) / 1000
    except Exception as e:
        st.error(f"Kunde inte hämta vägdata: {e}")
        return None

# --- EXEKVERING ---
if st.button("Kör Optimering"):
    with st.spinner("Geokodar adresser och hämtar vägdata..."):
        all_locs = []
        
        # 1. Geokodning
        loc_depot = geocode(depot_addr)
        if loc_depot:
            all_locs.append({"name": "DEPÅ", "lat": loc_depot.latitude, "lon": loc_depot.longitude})
        
        for addr in cust_addrs.split("\n"):
            if addr.strip():
                loc = geocode(addr)
                if loc:
                    all_locs.append({"name": addr.strip(), "lat": loc.latitude, "lon": loc.longitude})

        if len(all_locs) < 3:
            st.warning("Lägg till minst två kunder för att optimera.")
        else:
            df = pd.DataFrame(all_locs)
            n = len(df)
            
            # 2. Hämta riktig vägmatris
            dist_matrix = get_distance_matrix(df)
            
            if dist_matrix is not None:
                # 3. PuLP Optimering (TSP)
                prob = pulp.LpProblem("Industrial_Route", pulp.LpMinimize)
                
                # Variabler
                x = pulp.LpVariable.dicts("route", (range(n), range(n)), cat='Binary')
                u = pulp.LpVariable.dicts("u", range(n), lowBound=0, upBound=n-1)

                # Målfunktion
                prob += pulp.lpSum([dist_matrix[i,j] * x[i][j] for i in range(n) for j in range(n) if i != j])

                # Villkor
                for i in range(n):
                    prob += pulp.lpSum([x[i][j] for j in range(n) if i != j]) == 1
                    prob += pulp.lpSum([x[j][i] for j in range(n) if i != j]) == 1

                # Subtour elimination (MTZ)
                for i in range(1, n):
                    for j in range(1, n):
                        if i != j:
                            prob += u[i] - u[j] + n * x[i][j] <= n - 1

                # Lös med CBC
                prob.solve(pulp.PULP_CBC_CMD(msg=0))

                # 4. Extrahera rutten
                curr = 0
                order = [0]
                total_km = 0
                while len(order) < n:
                    for j in range(n):
                        if curr != j and pulp.value(x[curr][j]) == 1:
                            total_km += dist_matrix[curr, j]
                            order.append(j)
                            curr = j
                            break
                total_km += dist_matrix[order[-1], 0] # Tillbaka till depå
                order.append(0)

                # --- 5. PRESENTATION ---
                with col2:
                    st.header("Resultat")
                    st.metric("Total körsträcka", f"{round(total_km, 2)} km")
                    
                    # Visa ordningen snyggt
                    res_names = [df.iloc[i]['name'] for i in order]
                    st.write("### Optimal besöksordning:")
                    for idx, name in enumerate(res_names):
                        st.write(f"{idx+1}. {name}")
                    
                    # Karta
                    st.write("### Karta")
                    st.map(df)
                    
                    # Export-knapp (SaaS-känsla)
                    csv = df.iloc[order].to_csv(index=False).encode('utf-8')
                    st.download_button("Ladda ner körlista (CSV)", csv, "rutt.csv", "text/csv")
