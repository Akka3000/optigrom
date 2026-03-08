import streamlit as st

st.set_page_config(page_title="Skräddarsy", layout="wide")

st.title("🛠️ Skräddarsy din egen modell")
st.write("Berätta om din utmaning så återkommer jag med ett lösningsförslag.")

# DIN MAIL HÄR
MY_EMAIL = "optigrom.labs@gmail.com"

# Ett helt vanligt Streamlit-formulär (som på din första bild)
with st.form("kontakt_form", clear_on_submit=True):
    name = st.text_input("Namn")
    email = st.text_input("E-post")
    industry = st.selectbox("Bransch", ["Logistik", "Industri", "Lager", "Energi", "Annat"])
    description = st.text_area("Beskriv din utmaning")
    
    submitted = st.form_submit_button("Skicka förfrågan 🚀")

if submitted:
        if name and email and description:
            # Vi använder en guld-gul ruta för att visa att vi inte är klara än
            st.warning("⚠️ ETT STEG KVAR: För att förfrågan ska nå fram måste du klicka på knappen nedan.")
            
            subject = f"Optimering: {industry}"
            body = f"Namn: {name}\nE-post: {email}\n\nBeskrivning:\n{description}"
            
            import urllib.parse
            mail_url = f"mailto:{MY_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            
# Denna lilla rad ändrar färgen på "Primary"-knappar till blå just på denna sida
            st.markdown("""
                <style>
                div.stButton > button:first-child, div.stLinkButton > a:first-child {
                    background-color: #007bff !important;
                    color: white !important;
                    border: none !important;
                }
                </style>
            """, unsafe_allow_html=True)

            # Nu kan vi använda standard Streamlit-kod, och den kommer vara blå!
            st.link_button(
                "KLICKA HÄR FÖR ATT SKICKA MEJLET", 
                mail_url, 
                use_container_width=True,
                type="primary"
            )
            
           
        else:
            st.error("Fyll i alla fält först.")

st.divider()
st.info("💡 Genom att använda knappen ovan garanterar vi att ingen känslig data fastnar i spam-filter.")
