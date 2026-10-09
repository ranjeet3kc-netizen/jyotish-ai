import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date, time
import matplotlib.pyplot as plt

# Initialize Swiss Ephemeris Settings
swe.set_sid_mode(swe.SIDM_LAHIRI)

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

DASHA_LORDS = [
    "Ketu", "Shukra", "Surya", "Chandra",
    "Mangal", "Rahu", "Guru", "Shani", "Budh"
]

DASHA_YEARS = {
    "Ketu": 7, "Shukra": 20, "Surya": 6,
    "Chandra": 10, "Mangal": 7, "Rahu": 18,
    "Guru": 16, "Shani": 19, "Budh": 17
}

st.set_page_config(page_title="Jyotish AI", page_icon="🔱")
st.title("🔱 Jyotish AI")
st.caption("Vedic Astrology | वैदिक ज्योतिष")

lang = st.selectbox("Language / भाषा", ["English", "Hindi", "Nepali"])

headings = {
    "Hindi": "जन्म विवरण",
    "Nepali": "जन्म विवरण",
    "English": "Birth Details"
}

st.header(headings[lang])

with st.form("birth_form"):
    name = st.text_input("Name / नाम", value="User")
    dob = st.date_input("Date of birth", value=date(2000, 4, 15), min_value=date(1900, 1, 1))
    bt = st.time_input("Birth time", value=time(1, 0))
    place = st.text_input("Birth place / जन्म स्थान", value="Ghorahi, Nepal")
    lat = st.number_input("Latitude", value=28.0300, format="%.4f")
    lon = st.number_input("Longitude", value=82.4900, format="%.4f")
    submitted = st.form_submit_button("Calculate planetary positions")

if submitted:
    try:
        # Timezone offset conversion (Nepal = GMT + 5:45)
        local_dt = datetime.combine(dob, bt)
        utc_dt = local_dt - timedelta(hours=5, minutes=45)

        jd = swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        )

        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

        st.subheader("Planetary Positions")

        rows = []
        planet_signs = {}

        for planet, code in PLANETS.items():
            result, _ = swe.calc_ut(jd, code, flags)
            degree = result[0] % 360
            speed = result[3]  # Planet speed (negative = Retrograde)
            
            is_retro = speed < 0 and planet not in ["Surya", "Chandra", "Rahu"]
            planet_display = f"{planet} (R)" if is_retro else planet

            sign_index = int(degree // 30)
            sign_degree = degree % 30
            nak_index = int(degree / (360 / 27))

            rows.append({
                "Planet": planet_display,
                "Rashi": SIGNS[sign_index],
                "Degree": round(sign_degree, 2),
                "Nakshatra": NAKSHATRAS[nak_index],
                "Status": "Retrograde" if is_retro else "Direct"
            })
            planet_signs.setdefault(SIGNS[sign_index], []).append(planet_display)

        # Ketu calculation (Rahu + 180 degrees)
        rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
        rahu_deg = rahu_res[0] % 360
        ketu_degree = (rahu_deg + 180) % 360
        ketu_sign = int(ketu_degree // 30)
        ketu_nak = int(ketu_degree / (360 / 27))

        rows.append({
            "Planet": "Ketu",
            "Rashi": SIGNS[ketu_sign],
            "Degree": round(ketu_degree % 30, 2),
            "Nakshatra": NAKSHATRAS[ketu_nak],
            "Status": "Retrograde"
        })
        planet_signs.setdefault(SIGNS[ketu_sign], []).append("Ketu")

        st.dataframe(rows, use_container_width=True)

        # Calculate Lagna (Ascendant)
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
        asc_degree = ascmc[0] % 360
        asc_sign = int(asc_degree // 30)

        st.subheader("Lagna")
        st.write(f"**Lagna Rashi:** {SIGNS[asc_sign]}")
        st.write(f"**Lagna Degree:** {round(asc_degree % 30, 2)}°")

        # 12 Bhav Table
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

        # Plotting North Indian D1 Kundli
        st.subheader("D1 जन्म कुंडली — उत्तर भारतीय शैली")

        fig, ax = plt.subplots(figsize=(6, 6))
        
        # Draw Kundli Grid
        ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="maroon", lw=2)
        ax.plot([0, 0.5, 1, 0.5, 0], [0.5, 1, 0.5, 0, 0.5], color="maroon", lw=1.5)
        ax.plot([0, 1], [0, 1], color="maroon", lw=1.5)
        ax.plot([0, 1], [1, 0], color="maroon", lw=1.5)

        positions = [
            (0.50, 0.75), (0.25, 0.88), (0.12, 0.70),
            (0.25, 0.50), (0.12, 0.30), (0.25, 0.12),
            (0.50, 0.25), (0.75, 0.12), (0.88, 0.30),
            (0.75, 0.50), (0.88, 0.70), (0.75, 0.88)
        ]

        chart_rows = []
        for i, (x, y) in enumerate(positions):
            sign_index = (asc_sign + i) % 12
            sign_name = SIGNS[sign_index]
            
            planets_in_house = planet_signs.get(sign_name, [])
            p_str = "\n".join(planets_in_house) if planets_in_house else ""
            
            ax.text(x, y + 0.05, f"{sign_index + 1}", color="darkred", fontsize=10, weight="bold", ha="center")
            if p_str:
                ax.text(x, y - 0.05, p_str, color="navy", fontsize=8, ha="center")

            chart_rows.append({
                "Bhav": i + 1,
                "Rashi": sign_name,
                "Grah": ", ".join(planets_in_house) if planets_in_house else "-"
            })

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        st.pyplot(fig)
        plt.close(fig)

        st.dataframe(chart_rows, use_container_width=True)

        # Vimshottari Mahadasha & Antardasha Calculations
        st.subheader("Vimshottari Mahadasha & Antardasha")

        moon_result, _ = swe.calc_ut(jd, swe.MOON, flags)
        moon_degree = moon_result[0] % 360
        nak_span = 360.0 / 27.0  # 13.3333 degrees per nakshatra
        moon_nak_idx = int(moon_degree / nak_span)

        # Calculate exact degree position within the current Nakshatra
        deg_in_nak = moon_degree % nak_span
        balance_fraction = 1.0 - (deg_in_nak / nak_span)  # Remaining fraction of first dasha

        md_lord_idx = moon_nak_idx % 9
        first_md_lord = DASHA_LORDS[md_lord_idx]
        first_md_years = DASHA_YEARS[first_md_lord]
        remaining_first_md_years = first_md_years * balance_fraction

        st.write(f"**Janma Nakshatra:** {NAKSHATRAS[moon_nak_idx]}")
        st.write(f"**Janma Mahadasha Lord:** {first_md_lord}")
        st.write(f"**Balance Mahadasha at Birth:** {round(remaining_first_md_years, 2)} years")

        # Antardasha Breakdown for Current Mahadasha
        st.markdown("### Antardasha Sequence")
        
        current_date = local_dt
        ad_rows = []
        
        # Calculate Antardashas within the Mahadasha
        for j in range(9):
            ad_lord_idx = (md_lord_idx + j) % 9
            ad_lord = DASHA_LORDS[ad_lord_idx]
            
            # Antardasha duration = (MD Years * AD Years) / 120 (in years)
            ad_years = (first_md_years * DASHA_YEARS[ad_lord]) / 120.0
            ad_days = ad_years * 365.25
            
            end_date = current_date + timedelta(days=ad_days)
            
            ad_rows.append({
                "Mahadasha": first_md_lord,
                "Antardasha": ad_lord,
                "Start Date": current_date.strftime("%Y-%m-%d"),
                "End Date": end_date.strftime("%Y-%m-%d")
            })
            current_date = end_date

        st.dataframe(ad_rows, use_container_width=True)

    except Exception as e:
        st.error(f"Calculation error: {e}")

