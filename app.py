import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date, time
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

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

CAREER_MAP = {
    "Surya": "Sarkari naukri, Prashashanik seva (Administration), Management, Medical, Neta ya Uccha pad.",
    "Chandra": "Jal se jude karya, Hotel/Restaurant, Travel, Nursing, Dairy, Kavi ya Sahitya.",
    "Mangal": "Engineering, Technical karya, Police/Fauj, Defense, Real Estate, Property, Electrical ya Fire safety.",
    "Budh": "Vyapar (Business), Banking, Finance, Accounting, IT/Software, Bhasha/Writing, Media ya Dukandari.",
    "Guru": "Shikshak (Teacher), Professor, Vakeel/Kanoon, Jyotish, Financial Advisor, Temple/Trust ya Research.",
    "Shukra": "Fashion, Beauty Products, Interior Designing, Media, Acting, Hotel Management, Luxury goods ya Gold/Jewelry.",
    "Shani": "Vikas karya, Labor management, Machine/Factory, Iron/Hardware, Transport, Law ya Kheti/Krishi.",
    "Rahu": "IT, Digital Marketing, Import-Export, Foreign Business, Media, Electronics ya Stock Market.",
    "Ketu": "Software Programming, Research, Medical/Pharmacy, Healing, Spiritual karya ya Coding."
}

def section_heading(title, icon="✨"):
    """Custom HTML Header Component"""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #8E0E00 0%, #1F1C1C 100%);
            padding: 12px 20px;
            border-radius: 10px;
            margin-top: 25px;
            margin-bottom: 15px;
            border-left: 6px solid #FFD700;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        ">
            <h3 style="color: #FFD700; margin:0; padding:0; font-family: sans-serif; font-weight: 700;">
                {icon} {title}
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

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


st.set_page_config(page_title="Jyotish AI - A1 महा जन्मपत्री", page_icon="🔱", layout="wide")

# Main Title Styling
st.markdown(
    """
    <div style="text-align: center; background: linear-gradient(90deg, #4b1248 0%, #F0C27B 100%); padding: 20px; border-radius: 12px; margin-bottom: 25px;">
        <h1 style="color: #FFFFFF; font-size: 32px; font-weight: 800; margin:0;">🔱 JYOTISH AI — सम्पूर्ण महा जन्मपत्री</h1>
        <p style="color: #FFF8DC; font-size: 16px; margin-top: 5px;">Vedic Astrology Engine | सटीक कुंडली, ग्रह विश्लेषण एवं विस्तृत फलादेश</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.subheader("📋 Birth Details / जन्म विवरण दर्ज करें")

col_a, col_b = st.columns(2)
with col_a:
    name = st.text_input("Name / नाम", value="", placeholder="अपना नाम लिखें")
    gender = st.selectbox("Gender / लिंग", ["Male (पुरुष)", "Female (महिला)", "Other (अन्य)"])
    dob = st.date_input("Date of birth / जन्म तिथि", value=None, min_value=date(1900, 1, 1))
    bt = st.time_input("Birth time / जन्म समय", value=None)

with col_b:
    place = st.text_input("Birth place & Country / जन्म स्थान व देश", value="", placeholder="जैसे: Kathmandu Nepal, Delhi India, London UK")
    utc_offset = st.number_input("Timezone Offset from UTC (Hours)", value=5.75, step=0.25, help="Nepal: +5.75, India: +5.5")

submitted = st.button("🚀 Generate Full A1 Report / सम्पूर्ण महा-रिपोर्ट देखें", type="primary")

if submitted:
    if not name or not dob or not bt or not place:
        st.warning("कृपया सभी विवरण (नाम, लिंग, जन्म तिथि, समय और जन्म स्थान) भरें!")
    else:
        try:
            geolocator = Nominatim(user_agent="jyotish_app_v4")
            location = geolocator.geocode(place)

            if not location:
                st.error("जन्म स्थान नहीं मिल सका! कृपया स्थान और देश का नाम सही से लिखें।")
            else:
                lat = location.latitude
                lon = location.longitude
                st.success(f"📍 स्थान मिला: **{location.address}**")

                local_dt = datetime.combine(dob, bt)
                
                offset_hours = int(utc_offset)
                offset_minutes = int((utc_offset - offset_hours) * 60)
                utc_dt = local_dt - timedelta(hours=offset_hours, minutes=offset_minutes)

                jd = swe.julday(
                    utc_dt.year,
                    utc_dt.month,
                    utc_dt.day,
                    utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
                )

                flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

                # 1. PLANETARY POSITIONS
                section_heading("1. ग्रह स्थिति एवं नवमांश विवरण", "🪐")

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

                section_heading("2. D1 (जन्म) एवं D9 (नवमांश) चक्र", "📊")
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

                # 3. DYNAMIC CAREER PREDICTIONS
                section_heading("3. ग्रहों के अनुसार उपयुक्त करियर एवं बिज़नेस दिशा", "💼")

                karma_sign_idx = (asc_sign + 9) % 12
                karma_lord = RASHI_LORDS[karma_sign_idx]
                planets_in_10th = [p for p, s_idx in planet_positions_map.items() if s_idx == karma_sign_idx]

                with st.expander("💼 आपके लिए कौन-सा काम/बिज़नेस सबसे उत्तम रहेगा?", expanded=True):
                    st.write(f"• **दशम भाव (कर्म स्थान) राशि:** `{SIGNS[karma_sign_idx]}` ({SIGNS_HI[karma_sign_idx]})")
                    st.write(f"• **कर्मेश (10th Lord):** `{karma_lord}`")
                    st.write(f"• **मुख्य स्वामी ग्रह के अनुसार उपयुक्त क्षेत्र:** {CAREER_MAP.get(karma_lord, 'व्यापार व स्वतंत्र रोजगार')}")

                    if planets_in_10th:
                        st.write("• **दशम भाव में स्थित ग्रहों के आधार पर अतिरिक्त लाभप्रद कार्य:**")
                        for p in planets_in_10th:
                            st.write(f"  - **{p}:** {CAREER_MAP.get(p, 'स्वतंत्र व्यवसाय')}")

                # 4. GENDER SPECIFIC MARRIAGE PREDICTIONS
                section_heading("4. लिंग अनुसार विवाह एवं जीवनसाथी विश्लेषण", "💍")

                partner_label = "पत्नी (Wife)" if "Male" in gender else "पति (Husband)"
                marriage_sign_idx = (asc_sign + 6) % 12
                marriage_lord = RASHI_LORDS[marriage_sign_idx]

                with st.expander(f"💍 {gender} विशेष — विवाह एवं {partner_label} का स्वभाव", expanded=True):
                    st.write(f"• **सप्तम भाव (विवाह स्थान) राशि:** `{SIGNS[marriage_sign_idx]}` ({SIGNS_HI[marriage_sign_idx]}) | **सप्तमेश:** `{marriage_lord}`")
                    
                    if "Female" in gender:
                        st.write("• **पति का स्वभाव व कारकत्व (Guru & 7th House):** महिला जातकों के लिए बृहस्पति (Guru) और सप्तम भाव पति के सुख का मुख्य कारक होता है। आपका पति समझदार, जिम्मेदार और परिवार का ध्यान रखने वाला होगा।")
                    else:
                        st.write("• **पत्नी का स्वभाव व कारकत्व (Shukra & 7th House):** पुरुष जातकों के लिए शुक्र (Shukra) और सप्तम भाव पत्नी के सुख का मुख्य कारक होता है। आपकी पत्नी सुलझी हुई, व्यावहारिक और भाग्य में वृद्धि करने वाली होगी।")

                # 5. ALL 12 HOUSES ANALYSIS
                section_heading("5. समस्त 12 भावों का गहन फलादेश", "🏛️")

                house_details = [
                    ("प्रथम भाव (तनु भाव)", "व्यक्तित्व, शारीरिक सौष्ठव, आत्मबल, विचार और स्वास्थ्य का प्रतिनिधित्व करता है।"),
                    ("द्वितीय भाव (धन भाव)", "कुटुंब, वाणी, प्रारंभिक शिक्षा, संचित धन और संपत्ति का भाव है।"),
                    ("तृतीय भाव (सहज भाव)", "पराक्रम, कार्यक्षमता, साहस, संचार और भाई-बहनों का स्थान है।"),
                    ("चतुर्थ भाव (सुख भाव)", "माता का सुख, घर का वातावरण, वाहन, भूमि और अचल संपत्ति का प्रतीक है।"),
                    ("पंचम भाव (बुद्धि भाव)", "सोचने की क्षमता, बौद्धिक ज्ञान, निर्णय शक्ति और संतान का भाव है।"),
                    ("षष्ठ भाव (रिपु भाव)", "प्रतिस्पर्धा, दैनिक कार्यशैली, ऋण और बाधाओं से निपटने का भाव है।"),
                    ("सप्तम भाव (जाया भाव)", "वैवाहिक जीवन, जीवनसाथी का स्वभाव, साझेदारी और सामाजिक संबंध का भाव है।"),
                    ("अष्टम भाव (आयु भाव)", "आयु, अचानक होने वाले परिवर्तन, शोध और गुप्त विद्याओं का स्थान है।"),
                    ("नवम भाव (भाग्य भाव)", "भाग्योदय, धार्मिक आस्था, उच्च विचार और बड़ों के मार्गदर्शन का भाव है।"),
                    ("दशम भाव (कर्म भाव)", "करियर, आजीविका, सामाजिक पद-प्रतिष्ठा और अधिकारों का मुख्य केंद्र है।"),
                    ("एकदश भाव (लाभ भाव)", "आय के स्रोत, वित्तीय लाभ, मित्रों का सहयोग और मनोकामना पूर्ति का भाव है।"),
                    ("द्वादश भाव (व्यय भाव)", "विदेश/दूरस्थ स्थानों से संबंध, खर्चे, आत्म-साक्षात्कार और बचत का भाव है।")
                ]

                for house_num in range(1, 13):
                    h_sign_idx = (asc_sign + house_num - 1) % 12
                    h_sign_name = SIGNS[h_sign_idx]
                    h_lord = RASHI_LORDS[h_sign_idx]
                    planets_here = [p for p, s_idx in planet_positions_map.items() if s_idx == h_sign_idx]
                    h_title, h_desc = house_details[house_num - 1]

                    with st.expander(f"📍 {house_num}. {h_title} — राशि: {h_sign_name} ({SIGNS_HI[h_sign_idx]})", expanded=False):
                        st.write(f"• **भाव का महत्व:** {h_desc}")
                        st.write(f"• **भाव स्वामी (House Lord):** `{h_lord}`")
                        st.write(f"• **स्थित ग्रह:** `{', '.join(planets_here) if planets_here else 'खाली भाव (कोई ग्रह नहीं)'}`")

        except Exception as e:
            st.error(f"Calculation error: {e}")
    
