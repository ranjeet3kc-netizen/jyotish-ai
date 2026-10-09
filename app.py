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

# Rashi Lords Mapping (0-11)
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


st.set_page_config(page_title="Jyotish AI - सम्पूर्ण भाग्यफल", page_icon="🔱", layout="wide")
st.title("🔱 Jyotish AI — सम्पूर्ण जन्मपत्री एवं विस्तृत भाग्यफल")
st.caption("Vedic Astrology | वैदिक ज्योतिष, ग्रह योग एवं विस्तृत फलादेश")

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

submitted = st.button("Calculate Full Kundli & Detailed Predictions / विस्तृत भाग्यफल देखें", type="primary")

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
        st.subheader("1. ग्रह स्थिति एवं नवमांश (Planetary Positions)")

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

        st.subheader("2. D1 एवं D9 कुंडली चक्र")
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

        # 3. DASHA SYSTEM
        st.subheader("3. विंशोत्तरी महादशा चक्र")

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
        active_mahadasha_now = ""

        now_dt = datetime.now()

        for m_idx in range(9):
            md_lord_i = (first_md_lord_idx + m_idx) % 9
            md_name = DASHA_LORDS[md_lord_i]
            md_total_years = DASHA_YEARS[md_name]

            md_duration_years = remaining_first_md_years if m_idx == 0 else md_total_years
            md_end_date = current_start_date + timedelta(days=md_duration_years * 365.25)

            if current_start_date <= now_dt <= md_end_date:
                active_mahadasha_now = md_name

            all_md_rows.append({
                "महादशा (Mahadasha)": md_name,
                "प्रारंभ तिथि": current_start_date.strftime("%Y-%m-%d"),
                "समाप्ति तिथि": md_end_date.strftime("%Y-%m-%d"),
                "स्थिति": "वर्तमान में सक्रिय" if current_start_date <= now_dt <= md_end_date else "-"
            })
            current_start_date = md_end_date

        st.dataframe(all_md_rows, use_container_width=True)

        # 4. DETAILED PREDICTIONS ENGINE
        st.subheader("4. विस्तृत ज्योतिषीय भाग्यफल (Detailed Life Predictions)")

        lagna_lord = RASH_LORDS = RASHI_LORDS[asc_sign]
        bhagya_sign = (asc_sign + 8) % 12
        bhagya_lord = RASHI_LORDS[bhagya_sign]
        karma_sign = (asc_sign + 9) % 12
        karma_lord = RASHI_LORDS[karma_sign]
        marriage_sign = (asc_sign + 6) % 12
        marriage_lord = RASHI_LORDS[marriage_sign]

        # House calculations for key planets
        lagna_lord_house = ((planet_positions_map[lagna_lord] - asc_sign) % 12) + 1
        bhagya_lord_house = ((planet_positions_map[bhagya_lord] - asc_sign) % 12) + 1

        # Section A: Personality & Lagna
        with st.expander("👤 1. व्यक्तित्व, स्वास्थ्य एवं आत्मबल (Lagna & Personality Analysis)", expanded=True):
            st.markdown(f"**आपका लग्न:** `{SIGNS[asc_sign]}` ({SIGNS_HI[asc_sign]}) | **लग्नेश:** `{lagna_lord}`")
            
            if asc_sign == 8:  # Dhanu Lagna
                st.write("• **स्वभाव व गुण:** धनु लग्न होने से आप स्पष्टवादी, दूरदर्शी, धार्मिक और उच्च ज्ञान के प्रेमी हैं। आपका दृष्टिकोण जीवन के प्रति सकारात्मक रहता है।")
                st.write("• **लग्नेश गुरु की स्थिति:** आपका लग्नेश बृहस्पति आपके जीवन में मार्गदर्शन, सही निर्णय लेने की क्षमता और समाज में मान-सम्मान देता है।")
            elif asc_sign == 0:  # Mesh
                st.write("• **स्वभाव व गुण:** मेष लग्न के कारण आपके अंदर भरपूर ऊर्जा, नेतृत्व क्षमता और किसी भी काम को पहल करके शुरू करने का साहस है।")
            else:
                st.write(f"• **स्वभाव व गुण:** {SIGNS_HI[asc_sign]} लग्न होने के कारण आप परिस्थितियों के अनुसार ढलने वाले और अपने कार्य के प्रति समर्पित रहने वाले व्यक्ति हैं।")

            st.write(f"• **लग्नेश की स्थिति:** लग्नेश `{lagna_lord}` आपकी कुंडली के `{lagna_lord_house}`वें भाव में स्थित है। यह आपके स्वास्थ्य और व्यक्तिगत पहचान पर मुख्य प्रभाव डालता है।")

        # Section B: Luck & Destiny
        with st.expander("✨ 2. भाग्योदय, धर्म एवं किस्मत (Destiny & 9th House)", expanded=True):
            st.markdown(f"**भाग्य भाव (9th House Rashi):** `{SIGNS[bhagya_sign]}` ({SIGNS_HI[bhagya_sign]}) | **भाग्येश:** `{bhagya_lord}`")
            st.write(f"• **भाग्योदय कारक ग्रह:** आपकी कुंडली में भाग्य के स्वामी `{bhagya_lord}` हैं, जो कि `{bhagya_lord_house}`वें भाव में विराजमान हैं।")
            
            if bhagya_lord_house in [1, 5, 9]:
                st.write("• **त्रिकोण भाग्य योग:** भाग्येश का त्रिकोण भाव में होना यह दर्शाता है कि आपका भाग्योदय आपकी अपनी मेहनत और ज्ञान से होगा। ईश्वर की कृपा आप पर बनी रहेगी।")
            elif bhagya_lord_house in [10, 11]:
                st.write("• **धन व कर्म से भाग्योदय:** भाग्य का स्वामी कर्म या लाभ भाव में है। आपका भाग्योदय रोजगार, व्यवसाय या 25 से 28 वर्ष की आयु के बाद तेज़ी से होगा।")
            else:
                st.write("• **भाग्योदय की राह:** आपका भाग्योदय जन्म स्थान से थोड़ा दूर जाने पर या बाहरी संपर्कों/कड़ी मेहनत के बाद अधिक प्रबल होता है।")

        # Section C: Career & Wealth
        with st.expander("💼 3. आजीविका, करियर एवं धन (Career, Work & Income)", expanded=True):
            st.markdown(f"**दशम भाव (10th House - Karma):** `{SIGNS[karma_sign]}` | **दशमेश:** `{karma_lord}`")
            st.write(f"• **करियर क्षेत्र:** आपकी कुंडली के अनुसार तकनीकी कार्य, प्रैक्टिकल स्किल्स, प्लंबिंग/इलेक्ट्रिकल, कंस्ट्रक्शन या मैनेजमेंट के क्षेत्रों में सफलता के उत्तम योग बनते हैं।")
            st.write("• **आर्थिक स्थिति:** एकादश भाव (लाभ भाव) और दशम भाव का संबंध यह दर्शाता है कि आपकी आय आपकी मेहनत पर सीधी निर्भर करेगी। व्यावहारिक हुनर से धन लाभ के योग बनते हैं।")

        # Section D: Marriage & Relationships
        with st.expander("💍 4. विवाह, दांपत्य एवं पारिवारिक जीवन (Marriage & Relationships)", expanded=False):
            st.markdown(f"**सप्तम भाव (7th House - Marriage):** `{SIGNS[marriage_sign]}` | **सप्तमेश:** `{marriage_lord}`")
            st.write(f"• **जीवनसाथी का स्वभाव:** आपका 7वां भाव `{SIGNS[marriage_sign]}` है। जीवनसाथी व्यावहारिक, समझदार और व्यावहारिक जीवन में सहयोग देने वाला/वाली होगी।")

        # Section E: Active Dasha Influence
        with st.expander("⏳ 5. वर्तमान दशा फल (Current Active Dasha Analysis)", expanded=True):
            if active_mahadasha_now:
                st.markdown(f"**आपकी वर्तमान सक्रिय महादशा:** `{active_mahadasha_now}`")
                
                dasha_meanings = {
                    "Guru": "गुरु की महादशा में ज्ञान की वृद्धि, नए हुनर सीखने का अवसर, सम्मान और धार्मिक यात्राओं के योग बनते हैं।",
                    "Shani": "शनि की महादशा में निरंतर अनुशासन, कड़ी मेहनत और व्यावहारिक कार्यों से दीर्घकालिक सफलता मिलती है।",
                    "Rahu": "राहु की महादशा में नए अवसरों की खोज, विदेश या बाहरी संपर्कों से लाभ और जीवन में अचानक बदलाव देखने को मिलते हैं।",
                    "Budh": "बुध की महादशा में बुद्धि, व्यापार, कौशल और वाणी का उपयोग करके लाभ कमाने के उत्कृष्ट योग बनते हैं।",
                    "Shukra": "शुक्र की महादशा में सुख-सुविधाओं की प्राप्ति, वाहन/मकान के योग और रचनात्मक कार्यों में सफलता मिलती है।",
                    "Surya": "सूर्य की महादशा में आत्मविश्वास, सरकारी या प्रशासनिक कार्यों में सफलता और पद-प्रतिष्ठा बढ़ती है।",
                    "Mangal": "मंगल की महादशा में ऊर्जा, भूमि/भवन से जुड़े कार्य और तकनीकी क्षेत्र में पराक्रम बढ़ता है।",
                    "Chandra": "चंद्रमा की महादशा में मानसिक शांति, यात्राएं और पारिवारिक सहयोग प्राप्त होता है।",
                    "Ketu": "केतु की महादशा में आध्यात्मिक झुकाव, अनुसंधान और गूढ़ विषयों को सीखने का अवसर मिलता है।"
                }
                
                st.write(f"• **दशा का प्रभाव:** {dasha_meanings.get(active_mahadasha_now, 'यह समय आपके लिए नए अनुभवों और सीख का रहेगा।')}")
            else:
                st.write("• महादशा की गणना सारणी ऊपर दी गई है।")

    except Exception as e:
        st.error(f"Calculation error: {e}")
        
