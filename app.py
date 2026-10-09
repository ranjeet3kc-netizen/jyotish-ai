import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date, time
SIGNS = [
    "Mesh", "Vrishabh", "Mithun", "Kark",
    "Singh", "Kanya", "Tula", "Vrishchik",
    "Dhanu", "Makar", "Kumbh", "Meen"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini",
    "Mrigashira", "Ardra", "Punarvasu", "Pushya",
    "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]
PLANETS = {
    "Surya": swe.SUN,
    "Chandra": swe.MOON,
    "Mangal": swe.MARS,
    "Budh": swe.MERCURY,
    "Guru": swe.JUPITER,
    "Shukra": swe.VENUS,
    "Shani": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}

st.title("🔱 Jyotish AI")
st.caption("Vedic Astrology | वैदिक ज्योतिष")

lang = st.selectbox(
    "Language / भाषा",
    ["Hindi", "Nepali", "English"]
)

headings = {
    "Hindi": "जन्म विवरण",
    "Nepali": "जन्म विवरण",
    "English": "Birth Details"
}

st.header(headings[lang])

with st.form("birth_form"):
    name = st.text_input("Name / नाम")
    dob = st.date_input(
        "Date of birth",
        value=date(2000, 4, 15),
        min_value=date(1900, 1, 1)
    )
    bt = st.time_input(
        "Birth time",
        value=time(1, 0)
    )
    place = st.text_input(
        "Birth place / जन्म स्थान",
        value="Ghorahi, Nepal"
    )
    lat = st.number_input(
        "Latitude",
        value=28.03,
        format="%.4f"
    )
    lon = st.number_input(
        "Longitude",
        value=82.49,
        format="%.4f"
    )
    submitted = st.form_submit_button(
        "Calculate planetary positions"
    )

if submitted:
    try:
        local_dt = datetime.combine(dob, bt)
        utc_dt = local_dt - timedelta(hours=5, minutes=45)

        jd = swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60)

        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

        st.subheader("Planetary Positions")

        rows = []
        for planet, code in PLANETS.items():
            result, retflags = swe.calc_ut(
                jd, code, flags
            )
            degree = result[0] % 360
            sign_index = int(degree // 30)
            sign_degree = degree % 30
            nak_index = int(degree / (360 / 27))

            rows.append({
                "Planet": planet,
                "Rashi": SIGNS[sign_index],
                "Degree": round(sign_degree, 2),
                "Nakshatra": NAKSHATRAS[nak_index]
            })

        # Ketu is opposite Rahu
        rahu = swe.calc_ut(
            jd, swe.MEAN_NODE, flags
        )[0][0] % 360
        ketu_degree = (rahu + 180) % 360
        ketu_sign = int(ketu_degree // 30)
        ketu_nak = int(ketu_degree / (360 / 27))

        rows.append({
            "Planet": "Ketu",
            "Rashi": SIGNS[ketu_sign],
            "Degree": round(ketu_degree % 30, 2),
            "Nakshatra": NAKSHATRAS[ketu_nak]
        })

        st.dataframe(rows, use_container_width=True)
        # Calculate Vedic Ascendant
        cusps, ascmc = swe.houses_ex(
            jd, lat, lon, b'P', swe.FLG_SIDEREAL
        )

        asc_degree = ascmc[0] % 360
        asc_sign = int(asc_degree // 30)

        st.subheader("Lagna")
        st.write("Lagna Rashi:", SIGNS[asc_sign])
        st.write("Lagna Degree:", round(asc_degree % 30, 2))

        st.subheader("12 Bhav")
        house_rows = []
        for i, cusp in enumerate(cusps):
            degree = cusp % 360
            house_rows.append({
                "Bhav": i + 1,
                "Rashi": SIGNS[int(degree // 30)],
                "Degree": round(degree % 30, 2)
            })

        st.dataframe(house_rows, use_container_width=True)
        
                # Vimshottari Dasha - basic starting point
        st.subheader("Vimshottari Mahadasha")

        moon_result, _ = swe.calc_ut(jd, swe.MOON, flags)
        moon_degree = moon_result[0] % 360
        moon_nak = int(moon_degree / (360 / 27))

        dasha_lords = [
            "Ketu", "Shukra", "Surya", "Chandra",
            "Mangal", "Rahu", "Guru", "Shani", "Budh"
        ]

        dasha_years = {
            "Ketu": 7, "Shukra": 20, "Surya": 6,
            "Chandra": 10, "Mangal": 7, "Rahu": 18,
            "Guru": 16, "Shani": 19, "Budh": 17
        }

        first_lord = dasha_lords[moon_nak % 9]
        st.write("Janma Nakshatra:", NAKSHATRAS[moon_nak])
        st.write("Janma Mahadasha:", first_lord)
        st.write("Mahadasha Duration:", dasha_years[first_lord], "years")

    except Exception as e:
        st.error(f"Calculation error: {e}")

