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
st.title("🔱 Jyotish AI — A1 महा जन्मपत्री एवं अति-विस्तृत भाग्यफल")
st.caption("Vedic Astrology | 12 भाव, 9 ग्रह, आयु-अनुसार फलादेश एवं वैदिक उपाय")

st.header("Birth Details / जन्म विवरण दर्ज करें")

col_a, col_b = st.columns(2)
with col_a:
    name = st.text_input("Name / नाम", value="", placeholder="अपना नाम लिखें")
    dob = st.date_input("Date of birth / जन्म तिथि", value=None, min_value=date(1900, 1, 1))
    bt = st.time_input("Birth time / जन्म समय", value=None)

with col_b:
    place = st.text_input("Birth place & Country / जन्म स्थान व देश", value="", placeholder="जैसे: Dang Nepal, Delhi India, London UK")
    utc_offset = st.number_input("Timezone Offset from UTC (Hours)", value=5.75, step=0.25, help="Nepal: +5.75, India: +5.5")

submitted = st.button("Generate Full A1 Report / सम्पूर्ण ए1 महा-रिपोर्ट देखें", type="primary")

if submitted:
    if not name or not dob or not bt or not place:
        st.warning("कृपया सभी विवरण (नाम, जन्म तिथि, समय और जन्म स्थान) भरें!")
    else:
        try:
            geolocator = Nominatim(user_agent="jyotish_app_a1")
            location = geolocator.geocode(place)

            if not location:
                st.error("जन्म स्थान नहीं मिल सका! कृपया स्थान और देश का नाम सही से लिखें।")
            else:
                lat = location.latitude
                lon = location.longitude
                st.success(f"स्थान मिला: **{location.address}**")

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

                # 3. AGE-WISE FULL LIFE PREDICTIONS
                st.subheader("3. जीवन कालखंड अनुसार अति-विस्तृत फलादेश (Age-wise Predictions)")

                with st.expander("🎓 20 से 30 वर्ष की आयु: शिक्षा, हुनर एवं करियर की शुरुआत", expanded=True):
                    st.write("""
                    • **करियर एवं कार्यक्षेत्र:** यह दशक आपके जीवन में अपनी नींव मजबूत करने का है। यदि आप प्रैक्टिकल, टेक्निकल या व्यावहारिक काम (जैसे प्लंबिंग, इलेक्ट्रिकल, कंस्ट्रक्शन, या मैनेजमेंट) से जुड़े हैं, तो इस दौरान आपकी कार्यकुशलता में जबर्दस्त सुधार आएगा।
                    • **आर्थिक प्रगति:** शुरुआत में मेहनत अधिक और फल थोड़ा धीमा मिल सकता है, लेकिन 24-25 वर्ष की आयु के बाद से आपकी आर्थिक स्थिति में स्थायित्व आने लगेगा।
                    • **सलाह:** इस समय अपने हुनर और तकनीकी ज्ञान को बढ़ाने पर ध्यान दें, यही आगे चलकर आपकी मुख्य पहचान और धन का जरिया बनेगा।
                    """)

                with st.expander("💍 25 से 35 वर्ष की आयु: विवाह, जीवनसाथी एवं पारिवारिक जीवन", expanded=True):
                    st.write("""
                    • **विवाह एवं दांपत्य सुख:** इस कालखंड में विवाह के प्रबल योग बनते हैं। आपका जीवनसाथी समझदार, व्यावहारिक विचारों वाला/वाली और परिवार का सम्मान करने वाला होगा।
                    • **पारिवारिक जिम्मेदारियां:** शादी के बाद आपके भाग्य में वृद्धि (भाग्योदय) होगी। जीवनसाथी के आने से आर्थिक फैसलों में सुधार आएगा और परिवार में आपका मान-सम्मान बढ़ेगा।
                    """)

                with st.expander("🏢 35 से 50 वर्ष की आयु: अचल संपत्ति, भवन निर्माण एवं स्थायी समृद्धि", expanded=True):
                    st.write("""
                    • **मकान व भूमि सुख:** इस अवधि में आपके पास अपनी खुद की अचल संपत्ति (मकान, जमीन या व्यावसायिक दुकान) बनाने के मजबूत योग हैं। 
                    • **स्वतंत्र व्यापार व सफलता:** इस उम्र में आप दूसरों के अधीन काम करने के बजाय स्वतंत्र रूप से अपना काम या कॉन्ट्रैक्ट संभालेंगे। यह आपकी जिंदगी का सबसे समृद्ध दौर रहेगा।
                    """)

                # 4. ALL 12 HOUSES DETAILED ANALYSIS
                st.subheader("4. समस्त 12 भावों का पूर्ण फलादेश (12 Bhav Complete Analysis)")

                house_details = [
                    ("प्रथम भाव (तनु भाव - व्यक्तित्व व स्वास्थ्य)", "आपका आत्मबल, शारीरिक बनावट, सोच और जीवन जीने की शैली का प्रतिनिधित्व करता है।"),
                    ("द्वितीय भाव (धन भाव - संपत्ति व कुटुंब)", "पारिवारिक स्थिति, संचित धन, वाणी और दैनिक खान-पान का भाव है।"),
                    ("तृतीय भाव (सहज भाव - पराक्रम व हुनर)", "आपके हाथों का हुनर, व्यावहारिक कार्यक्षमता, साहस और छोटे भाई-बहनों का स्थान है।"),
                    ("चतुर्थ भाव (सुख भाव - भूमि व भवन)", "माता का सुख, घर का माहौल, अपनी गाड़ी, भूमि और अचल संपत्ति का प्रतीक है।"),
                    ("पंचम भाव (बुद्धि भाव - निर्णय व संतान)", "आपकी सोचने की क्षमता, व्यावहारिक बुद्धि, शिक्षा और संतान का भाव है।"),
                    ("षष्ठ भाव (रिपु भाव - शत्रु व प्रतिस्पर्धा)", "कामकाज में आने वाली बाधाएं, प्रतियोगिता, ऋण और स्वास्थ्य का भाव है।"),
                    ("सप्तम भाव (जाया भाव - विवाह व साझेदारी)", "वैवाहिक जीवन, जीवनसाथी का स्वभाव, पार्टनरशिप और सामाजिक पहचान का भाव है।"),
                    ("अष्टम भाव (आयु भाव - गुप्त ज्ञान व शोध)", "आयु, अचानक होने वाले बदलाव, पैतृक धन और गुप्त विद्याओं का स्थान है।"),
                    ("नवम भाव (भाग्य भाव - धर्म व किस्मत)", "भाग्योदय का समय, धार्मिक विचार, लंबी यात्राएं और बड़ों के आशीर्वाद का भाव है।"),
                    ("दशम भाव (कर्म भाव - करियर व पहचान)", "रोजगार, आजीविका, कार्यक्षेत्र में आपका पद और समाज में आपकी प्रतिष्ठा का मुख्य केंद्र है।"),
                    ("एकदश भाव (लाभ भाव - आय व इच्छाएं)", "कमाई के स्रोत, आर्थिक लाभ, दोस्तों का सहयोग और मनोकामना पूर्ति का भाव है।"),
                    ("द्वादश भाव (व्यय भाव - खर्च व बाहरी संबंध)", "घर से दूर/विदेश में काम, खर्चे, मानसिक शांति और बचत का भाव है।")
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
                        st.write(f"• **गहन विश्लेषण:** इस भाव में {SIGNS_HI[h_sign_idx]} राशि स्थित होने से स्वामी `{h_lord}` आपके जीवन के इस पहलू को नियंत्रित करते हैं। यदि इस भाव में ग्रह मौजूद हैं, तो वे इस भाव के फलों में तेजी लाते हैं।")

                # 5. VEDIC REMEDIES & SUGGESTIONS
                st.subheader("5. वैदिक उपाय एवं सरल समाधान (Vedic Remedies)")

                with st.expander("🌿 ग्रह शांति एवं भाग्यवृद्धि के मुख्य उपाय", expanded=True):
                    st.write("""
                    1. **लग्नेश को बल दें:** प्रतिदिन सूर्य देव को जल अर्पित करें और ओम् नमः शिवाय का जाप करें। इससे आपका आत्मविश्वास और स्वास्थ्य हमेशा मजबूत रहेगा।
                    2. **कार्यक्षेत्र में सफलता हेतु:** शनिवार को हनुमान जी का दर्शन करें और पीपल के पेड़ के नीचे दिया जलाएं। इससे आपके कामों में आने वाली रुकावटें खत्म होंगी।
                    3. **धन व भाग्योदय हेतु:** अपनी मां और घर के बड़े-बुजुर्गों का आशीर्वाद लें। मंगलवार को गुड़ या चने का दान करना आपके लिए अत्यंत शुभ रहेगा।
                    """)

        except Exception as e:
            st.error(f"Calculation error: {e}")
                    
