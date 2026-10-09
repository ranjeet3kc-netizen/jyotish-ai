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

SIGNS_HI = [
    "मेष", "वृषभ", "मिथुन", "कर्क",
    "सिंह", "कन्या", "तुला", "वृश्चिक",
    "धनु", "मकर", "कुंभ", "मीन"
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

RASHI_LORDS = {
    0: "Mangal", 1: "Shukra", 2: "Budh", 3: "Chandra",
    4: "Surya", 5: "Budh", 6: "Shukra", 7: "Mangal",
    8: "Guru", 9: "Shani", 10: "Shani", 11: "Guru"
}


def get_navamsha_sign(abs_degree):
    """Calculates D9 Navamsha sign index (0-11)"""
    abs_degree = abs_degree % 360
    d1_sign = int(abs_degree // 30)
    sign_degree = abs_degree % 30
    navamsha_num = int(sign_degree // (30 / 9))

    if d1_sign in [0, 4, 8]:
        start_sign = 0
    elif d1_sign in [1, 5, 9]:
        start_sign = 9
    elif d1_sign in [2, 6, 10]:
        start_sign = 6
    else:
        start_sign = 3

    return (start_sign + navamsha_num) % 12


def render_north_indian_chart(asc_sign, planet_signs, title):
    """Renders a North Indian Kundli chart using Matplotlib."""
    fig, ax = plt.subplots(figsize=(5, 5))

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

    for i, (x, y) in enumerate(positions):
        sign_index = (asc_sign + i) % 12
        planets_in_house = planet_signs.get(SIGNS[sign_index], [])
        p_str = "\n".join(planets_in_house) if planets_in_house else ""

        ax.text(x, y + 0.05, f"{sign_index + 1}", color="darkred", fontsize=10, weight="bold", ha="center")
        if p_str:
            ax.text(x, y - 0.05, p_str, color="navy", fontsize=8, ha="center")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title, fontsize=12, pad=10, color="maroon", weight="bold")
    return fig


st.set_page_config(page_title="Jyotish AI - महा भाग्यफल ग्रन्थ", page_icon="🔱", layout="wide")
st.title("🔱 Jyotish AI — महा जन्मपत्री एवं विस्तृत भाग्यफल")
st.caption("Vedic Astrology | 12 भाव, 9 ग्रह एवं विस्तृत महादशा विश्लेषण")

st.header("Birth Details / जन्म विवरण")

col_a, col_b, col_c = st.columns(3)
with col_a:
    name = st.text_input("Name / नाम", value="Rana")
    dob = st.date_input("Date of birth", value=date(2000, 4, 15), min_value=date(1900, 1, 1))
with col_b:
    bt = st.time_input("Birth time", value=time(1, 0))
    place = st.text_input("Birth place / जन्म स्थान", value="Ghorahi, Nepal")
with col_c:
    lat = st.number_input("Latitude", value=28.0300, format="%.4f")
    lon = st.number_input("Longitude", value=82.4900, format="%.4f")

submitted = st.button("Generate Full Detailed Report / विस्तृत महा-रिपोर्ट जनरेट करें", type="primary")

if submitted:
    try:
        local_dt = datetime.combine(dob, bt)
        utc_dt = local_dt - timedelta(hours=5, minutes=45)

        jd = swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        )

        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

        # 1. PLANETARY POSITIONS
        st.subheader("1. ग्रह स्थिति एवं नवमांश तालिका")

        rows = []
        d1_planet_signs = {}
        d9_planet_signs = {}
        planet_positions_map = {}
        moon_sign_idx = 0

        for planet, code in PLANETS.items():
            result, _ = swe.calc_ut(jd, code, flags)
            degree = result[0] % 360
            speed = result[3]

            is_retro = speed < 0 and planet not in ["Surya", "Chandra", "Rahu"]
            planet_display = f"{planet} (R)" if is_retro else planet

            sign_index = int(degree // 30)
            sign_degree = degree % 30
            nak_index = int(degree / (360 / 27))

            planet_positions_map[planet] = sign_index

            if planet == "Chandra":
                moon_sign_idx = sign_index

            d9_sign_index = get_navamsha_sign(degree)

            rows.append({
                "Planet": planet_display,
                "D1 Rashi": SIGNS[sign_index],
                "Degree": round(sign_degree, 2),
                "Nakshatra": NAKSHATRAS[nak_index],
                "D9 Navamsha Rashi": SIGNS[d9_sign_index],
                "Status": "Retrograde" if is_retro else "Direct"
            })

            d1_planet_signs.setdefault(SIGNS[sign_index], []).append(planet_display)
            d9_planet_signs.setdefault(SIGNS[d9_sign_index], []).append(planet_display)

        rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
        rahu_deg = rahu_res[0] % 360
        ketu_degree = (rahu_deg + 180) % 360
        ketu_sign = int(ketu_degree // 30)
        ketu_nak = int(ketu_degree / (360 / 27))
        ketu_d9_sign = get_navamsha_sign(ketu_degree)

        planet_positions_map["Ketu"] = ketu_sign

        rows.append({
            "Planet": "Ketu",
            "D1 Rashi": SIGNS[ketu_sign],
            "Degree": round(ketu_degree % 30, 2),
            "Nakshatra": NAKSHATRAS[ketu_nak],
            "D9 Navamsha Rashi": SIGNS[ketu_d9_sign],
            "Status": "Retrograde"
        })
        d1_planet_signs.setdefault(SIGNS[ketu_sign], []).append("Ketu")
        d9_planet_signs.setdefault(SIGNS[ketu_d9_sign], []).append("Ketu")

        st.dataframe(rows, use_container_width=True)

        # 2. CHARTS
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
        asc_degree = ascmc[0] % 360
        asc_sign = int(asc_degree // 30)
        d9_asc_sign = get_navamsha_sign(asc_degree)

        st.subheader("2. D1 (जन्म) एवं D9 (नवमांश) चक्र")
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**D1 लग्न राशि:** {SIGNS[asc_sign]} ({SIGNS_HI[asc_sign]}) — {round(asc_degree % 30, 2)}°")
            fig_d1 = render_north_indian_chart(asc_sign, d1_planet_signs, "D1 - जन्म कुंडली")
            st.pyplot(fig_d1)
            plt.close(fig_d1)

        with col2:
            st.write(f"**D9 नवमांश लग्न राशि:** {SIGNS[d9_asc_sign]} ({SIGNS_HI[d9_asc_sign]})")
            fig_d9 = render_north_indian_chart(d9_asc_sign, d9_planet_signs, "D9 - नवमांश कुंडली")
            st.pyplot(fig_d9)
            plt.close(fig_d9)

        # 3. DETAILED 12 HOUSES ANALYSIS
        st.subheader("3. समस्त 12 भावों का अति-विस्तृत फलादेश")

        house_details = [
            ("प्रथम भाव (तनु भाव)", "व्यक्तित्व, शारीरिक गठन, आत्मबल, विचार और स्वास्थ्य का प्रतिनिधित्व करता है।"),
            ("द्वितीय भाव (धन भाव)", "कुटुंब, वाणी, प्रारंभिक शिक्षा, संचित धन और खान-पान का भाव है।"),
            ("तृतीय भाव (सहज भाव)", "पराक्रम, छोटे भाई-बहन, साहस, संचार माध्यम और व्यावहारिक हुनर का भाव है।"),
            ("चतुर्थ भाव (सुख भाव)", "माता का सुख, भूमि, अचल संपत्ति, भवन, वाहन और मानसिक शांति का प्रतीक है।"),
            ("पंचम भाव (पुत्र/बुद्धि भाव)", "उच्च शिक्षा, बुद्धि, संतान, पूर्व जन्म के पुण्य और निर्णय लेने की क्षमता का भाव है।"),
            ("षष्ठ भाव (रिपु भाव)", "प्रतिस्पर्धा, रोग, ऋण, शत्रु और दैनिक कार्यशैली का प्रतिनिधित्व करता है।"),
            ("सप्तम भाव (जाया भाव)", "विवाह, जीवनसाथी, साझेदारी, व्यापारिक संबंध और समाज में प्रतिष्ठा का भाव है।"),
            ("अष्टम भाव (आयु भाव)", "आयु, गुप्त ज्ञान, अचानक होने वाले लाभ/हानि, शोध और गूढ़ रहस्यों का भाव है।"),
            ("नवम भाव (भाग्य भाव)", "भाग्य, धर्म, गुरुजनों का मार्गदर्शन, उच्च ज्ञान और लंबी यात्राओं का भाव है।"),
            ("दशम भाव (कर्म भाव)", "करियर, कार्यक्षेत्र, सामाजिक प्रतिष्ठा, अधिकार और आजीविका का मुख्य स्थान है।"),
            ("एकदश भाव (लाभ भाव)", "आय के स्रोत, इच्छा पूर्ति, बड़े भाई-बहन और वित्तीय लाभ का प्रतीक है।"),
            ("द्वादश भाव (व्यय भाव)", "विदेश यात्रा, व्यय, मोक्ष, अस्पताल/एकांतवास और गुप्त शत्रुओं का भाव है।")
        ]

        for house_num in range(1, 13):
            h_sign_idx = (asc_sign + house_num - 1) % 12
            h_sign_name = SIGNS[h_sign_idx]
            h_lord = RASHI_LORDS[h_sign_idx]
            planets_here = [p for p, s_idx in planet_positions_map.items() if s_idx == h_sign_idx]
            h_title, h_desc = house_details[house_num - 1]

            with st.expander(f"📍 {house_num}. {h_title} — राशि: {h_sign_name} ({SIGNS_HI[h_sign_idx]})", expanded=True):
                st.write(f"• **भाव का महत्व:** {h_desc}")
                st.write(f"• **भाव स्वामी (House Lord):** `{h_lord}`")
                st.write(f"• **स्थित ग्रह:** `{', '.join(planets_here) if planets_here else 'खाली भाव (कोई ग्रह नहीं)'}`")
                st.write(f"• **विस्तृत विश्लेषण:** इस भाव में {SIGNS_HI[h_sign_idx]} राशि स्थित होने के कारण, स्वामी `{h_lord}` की स्थिति आपके जीवन के इस क्षेत्र में महत्वपूर्ण भूमिका निभाएगी। यदि इस भाव में ग्रह विराजमान हैं, तो उनके गुणधर्म और कारकत्व इस भाव के फलों को तीव्र बनाएंगे।")

        # 4. ALL 9 PLANETS DETAILED ANALYSIS
        st.subheader("4. नवग्रहों का स्थिति अनुसार विस्तृत विश्लेषण")

        for pl_name in PLANETS.keys():
            pl_sign_i = planet_positions_map[pl_name]
            pl_house = ((pl_sign_i - asc_sign) % 12) + 1
            with st.expander(f"🔮 {pl_name} — {pl_house}वें भाव में ({SIGNS[pl_sign_i]} राशि)", expanded=True):
                st.write(f"• **ग्रह स्थिति:** {pl_name} आपकी कुंडली के {pl_house}वें भाव में {SIGNS_HI[pl_sign_i]} राशि में विराजमान हैं।")
                st.write(f"• **प्रभाव व फलादेश:** {pl_name} का {pl_house}वें भाव में होना यह दर्शाता है कि आपका ध्यान और ऊर्जा जीवन के इस क्षेत्र पर केंद्रित रहेगी। यह स्थिति आपके व्यवहार, निर्णय क्षमता और करियर के दृष्टिकोण पर सकारात्मक व महत्वपूर्ण प्रभाव डालती है।")

        # 5. DASHA TIMELINE
        st.subheader("5. विंशोत्तरी महादशा एवं अंतर्दशा विस्तृत टाइमलाइन")

        moon_result, _ = swe.calc_ut(jd, swe.MOON, flags)
        moon_degree = moon_result[0] % 360
        nak_span = 360.0 / 27.0
        moon_nak_idx = int(moon_degree / nak_span)

        deg_in_nak = moon_degree % nak_span
        balance_fraction = 1.0 - (deg_in_nak / nak_span)

        first_md_lord_idx = moon_nak_idx % 9
        first_md_lord = DASHA_LORDS[first_md_lord_idx]
        first_md_years = DASHA_YEARS[first_md_lord]
        remaining_first_md_years = first_md_years * balance_fraction

        all_md_rows = []
        current_start_date = local_dt

        for m_idx in range(9):
            md_lord_i = (first_md_lord_idx + m_idx) % 9
            md_name = DASHA_LORDS[md_lord_i]
            md_total_years = DASHA_YEARS[md_name]

            md_duration_years = remaining_first_md_years if m_idx == 0 else md_total_years
            md_end_date = current_start_date + timedelta(days=md_duration_years * 365.25)

            all_md_rows.append({
                "महादशा (Mahadasha)": md_name,
                "प्रारंभ तिथि": current_start_date.strftime("%Y-%m-%d"),
                "समाप्ति तिथि": md_end_date.strftime("%Y-%m-%d"),
                "अवधि (वर्ष)": round(md_duration_years, 2)
            })
            current_start_date = md_end_date

        st.dataframe(all_md_rows, use_container_width=True)

    except Exception as e:
        st.error(f"Calculation error: {e}")
        
