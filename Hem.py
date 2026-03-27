import streamlit as st

# 1. Inställningar för premium-känsla
st.set_page_config(
    page_title="Optigrom | Industriell Optimering",
    page_icon="🎯",
    layout="wide"
)


st.title("OptiGrom Solutions")
st.subheader("Avancerade beslutsstöd för framtidens industri")

st.markdown("---")

col1, col2, col3, col4, col5, col6 = st.columns(6)

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
    st.header("🌐 Strategisk Nätverksdesign")
    st.write("Optimera lagerplacering.")
    with st.container(border=True):
        st.page_link("pages/5_Optimal_Lagerplacering.py", label="Testa lagerplacering demo", icon="🌐", use_container_width=True)

with col6:
    st.header("⚙️ Eget case")
    st.write("Skräddar sy er egna modell för eran verksamhet.")
    with st.container(border=True):
        st.page_link("pages/6_Skräddarsy_egen_modell.py", label="Kontakt", icon="🛠️", use_container_width=True)



st.markdown("---")
st.write("### Varför välja matematisk programmering?")
st.write("""
Traditionell planering och heuristik lämnar ofta stora besparingsmöjligheter på bordet. 
Genom **matematisk programmering** modellerar vi er verksamhets unika begränsningar 
och mål för att identifiera den objektivt bästa lösningen. 

**Resultatet?** Maximal effektivitet, minskat slöseri och ett datadrivet beslutsstöd 
som tar bort gissningsarbetet från er dagliga drift.
""")
