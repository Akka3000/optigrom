import streamlit as st

st.set_page_config(page_title="OptiFlow Solutions", layout="wide")

st.title("🚀 OptiFlow: Matematisk Optimering för Industrin")
st.subheader("Vi förvandlar komplexa logistikproblem till rena vinster.")

st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.header("🚚 Logistik")
    st.write("Minimera körsträcka och CO2-utsläpp.")
    # Här skapar vi ramen bara runt länken
    with st.container(border=True):
        st.page_link("pages/1_Lastmile_delivery.py", label="Testa Logistik demo", icon="🚀", use_container_width=True)

with col2:
    st.header("📦 Lager")
    st.write("Optimera inköp och lagernivåer.")
    with st.container(border=True):
        st.page_link("pages/2_Lagerhållning.py", label="Testa Lager demo", icon="📊", use_container_width=True)

with col3:
    st.header("⚙️ Produktion")
    st.write("Maximera maskinutnyttjande och minimera ställtider.")
    with st.container(border=True):
        st.page_link("pages/3_Produktionsoptimering.py", label="Testa Produktions-demo", icon="🔧", use_container_width=True)

with col4:
    st.header("⚙️ Energi")
    st.write("Maximera maskinutnyttjande och minimera ställtider.")
    with st.container(border=True):
        st.page_link("pages/4_Energioptimering.py", label="Testa Produktions-demo", icon="🔧", use_container_width=True)

with col5:
    st.header("⚙️ Eget case")
    st.write("Skräddar sy er egna modell för eran verksamhet.")
    with st.container(border=True):
        st.page_link("pages/5_Skräddarsy_egen_modell.py", label="Kontakt", icon="🛠️", use_container_width=True)

st.markdown("---")
st.write("### Varför välja matematisk optimering?")
st.write("Traditionell planering bygger på gissningar. Vi använder **Mixed-Integer Linear Programming (MILP)** för att garantera den absolut bästa lösningen givet era förutsättningar.")