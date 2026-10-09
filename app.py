
import streamlit as st
from datetime import date, time

st.set_page_config(
    page_title="Jyotish AI",
    page_icon="🔱"
)

st.title("🔱 Jyotish AI")
st.caption("Vedic Astrology | वैदिक ज्योतिष")

language = st.selectbox(
    "Choose Language / भाषा",
    ["Hindi", "Nepali", "English"]
)

titles = {
    "Hindi": "अपनी जन्म कुंडली बनाएं",
    "Nepali": "आफ्नो जन्म कुण्डली बनाउनुहोस्",
    "English": "Create Your Birth Chart"
}

st.header(titles[language])

with st.form("birth_form"):
    name = st.text_input("Name / नाम")
    dob = st.date_input(
        "Date of Birth",
        value=date(2000, 1, 1)
    )
    birth_time = st.time_input(
        "Birth Time",
        value=time(1, 0)
    )
    place = st.text_input("Birth Place / जन्म स्थान")

    submit = st.form_submit_button("Generate Kundli")

if submit:
    if not place.strip():
        st.error("Please enter your birth place.")
    else:
        st.subheader("Birth Details")
        st.write("Name:", name)
        st.write("Date:", dob)
        st.write("Time:", birth_time)
        st.write("Place:", place)
        st.info(
            "This is the first version. "
            "Kundli calculation and AI predictions "
            "will be added next."
        )
      
