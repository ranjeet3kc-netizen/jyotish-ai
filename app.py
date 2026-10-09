import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date, time
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import zoneinfo

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
    "Surya": "सरकारी नौकरी, प्रशासनिक सेवा (Administrative Services), मैनेजमेंट, मेडिकल/चिकित्सा, राजनीति, या किसी संस्था में उच्च नेतृत्व पद।",
    "Chandra": "जल व तरल पदार्थों से जुड़े व्यवसाय, होटल/रेस्टोरेंट, ट्रैवल एवं टूरिज्म, नर्सिंग/स्वास्थ्य सेवा, डेयरी उद्योग, कला, साहित्य या लेखन।",
    "Mangal": "इंजीनियरिंग, तकनीकी क्षेत्र (Technical Fields), पुलिस/सेना/डिफेंस, रियल एस्टेट, भूमि-भवन विकास, इलेक्ट्रिकल कार्य या सुरक्षा सेवाएं।",
    "Budh": "व्यापार (Business), बैंकिंग, फाइनेंस, एकाउंटिंग, आईटी/सॉफ्टवेयर विकास, मीडिया, पत्रकारिता, भाषा/अनुवादक या खुदरा व थोक दुकानें।",
    "Guru": "शिक्षक/प्रोफेसर, कानून व वकालत, वित्तीय परामर्शदाता (Financial Advisor), ज्योतिष, धार्मिक संस्थान/ट्रस्ट या रिसर्च व अकादमिक कार्य।",
    "Shukra": "फैशन डिजाइनिंग, ब्यूटी व कॉस्मेटिक्स, इंटीरियर डिजाइनिंग, मीडिया, अभिनय/फिल्म, लग्जरी गुड्स, आभूषण एवं ज्वैलरी या हॉस्पिटैलिटी।",
    "Shani": "निर्माण व विकास कार्य, लेबर/मानव संसाधन मैनेजमेंट, मशीनरी व फैक्टरी, लोहा/हार्डवेयर, ट्रांसपोर्टेशन, कानून या कृषि/खेती।",
    "Rahu": "सूचना प्रौद्योगिकी (IT), डिजिटल मार्केटिंग, आयात-निर्यात (Import-Export), विदेश से जुड़े व्यापार, इलेक्ट्रॉनिक्स, या शेयर बाजार।",
    "Ketu": "सॉफ्टवेयर प्रोग्रामिंग/कोडिंग, शोध कार्य (Research), फार्मास्युटिकल/दवाइयां, वैकल्पिक चिकित्सा, या आध्यात्मिक संस्थाएं।"
}

MAHADASHA_PREDICTIONS = {
    "Surya": "सूर्य की महादशा में आत्मबल, आत्मविश्वास और सामाजिक मान-प्रतिष्ठा में वृद्धि होती है। इस समय सरकारी कार्यों, अधिकारियों से सहयोग और करियर में उच्च पद पाने के अवसर बनते हैं।",
    "Chandra": "चंद्रमा की महादशा में मन में संवेदनशीलता और नए विचार आते हैं। यात्राओं के योग बनते हैं, पारिवारिक सुख और माता का सहयोग प्राप्त होता है। व्यापार व कला क्षेत्र में सफलता मिलती है।",
    "Mangal": "मंगल की महादशा ऊर्जा, साहस, और निर्णय क्षमता बढ़ाती है। भूमि, मकान, संपत्ति और तकनीकी कार्यों में विशेष सफलता मिलती है। पराक्रम से नए अवसर प्राप्त होते हैं।",
    "Budh": "बुध की महादशा में बुद्धि, व्यापारिक सोच, और संचार कौशल का विकास होता है। वित्तीय लाभ, नए व्यावसायिक सौदे, पठन-पाठन और तकनीकी/आईटी क्षेत्र में उत्तम परिणाम मिलते हैं।",
    "Guru": "गुरु (बृहस्पति) की महादशा अत्यंत शुभ मानी जाती है। इसमें ज्ञान, धर्म, मान-सम्मान, विवाह, संतान सुख और आर्थिक समृद्धि में वृद्धि होती है। बड़ों और गुरुजनों का मार्गदर्शन प्राप्त होता है।",
    "Shukra": "शुक्र की महादशा जीवन में भौतिक सुख-सुविधाएं, वाहन, मकान और आकर्षण लाती है। कला, सौंदर्य, विवाह, और रचनात्मक क्षेत्रों में बेहतरीन सफलता मिलती है।",
    "Shani": "शनि की महादशा अनुशासन, धैर्य और कड़े परिश्रम की परीक्षा लेती है। इस दौरान निरंतर प्रयास से दीर्घकालिक और स्थायी सफलता प्राप्त होती है। व्यावहारिक अनुभवों से जीवन सुधरता है।",
    "Rahu": "राहु की महादशा में जीवन में अचानक बड़े बदलाव आते हैं। नए और आधुनिक क्षेत्रों, आईटी, विदेश यात्रा, और लीक से हटकर किए गए कार्यों में बड़ी सफलता मिलने के योग बनते हैं।",
    "Ketu": "केतु की महादशा में आध्यात्मिक झुकाव, अनुसंधान, और गूढ़ विषयों को सीखने का अवसर मिलता है। आत्म-विश्लेषण और तकनीकी/शोध कार्यों में विशेष प्रगति होती है।"
}

def section_heading(title, icon="✨"):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #4A0000 0%, #1A0000 100%);
            padding: 14px 22px;
            border-radius: 10px;
            margin-top: 28px;
            margin-bottom: 18px;
            border-left: 6px solid #FFD700;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
        ">
            <h3 style="color: #FFD700; margin:0; padding:0; font-family: 'Segoe UI', sans-serif; font-weight: 700; font-size: 20px;">
                {icon} {title}
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

def get_navamsha_sign(abs_degree):
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

st.markdown(
    """
    <div style="text-align: center; background: linear-gradient(90deg, #3A0007 0%, #8A1C1C 50%, #3A0007 100%); padding: 25px; border-radius: 12px; border-bottom: 4px solid #FFD700; margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);">
        <h1 style="color: #FFD700; font-size: 34px; font-weight: 800; margin:0;">🔱 JYOTISH AI — सम्पूर्ण महा जन्मपत्री</h1>
        <p style="color: #FFF8DC; font-size: 16px; margin-top: 8px;">Vedic Astrology Engine | ऑटो-टाइमज़ोन, सटीक कुंडली व सम्पूर्ण भाग्यफल</p>
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
    
    st.write("**Birth Time / जन्म समय (AM / PM के साथ):**")
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        hour12 = st.number_input("Hour (घंटा)", min_value=1, max_value=12, value=1)
    with t_col2:
        minute = st.number_input("Minute (मिनट)", min_value=0, max_value=59, value=0)
    with t_col3:
        ampm = st.selectbox("AM / PM", ["AM (सुबह/रात)", "PM (दोपहर/शाम)"])

with col_b:
    place = st.text_input("Birth place & Country / जन्म स्थान व देश", value="", placeholder="जैसे: Dang Nepal, Delhi India, London UK, New York USA")

submitted = st.button("🚀 Generate Full A1 Detailed Report / सम्पूर्ण महा-रिपोर्ट देखें", type="primary")

if submitted:
    if not name or not dob or not place:
        st.warning("कृपया सभी विवरण (नाम, लिंग, जन्म तिथि, समय और जन्म स्थान) भरें!")
    else:
        try:
            # Convert 12-hour AM/PM to 24-hour time
            hour24 = hour12 % 12
            if "PM" in ampm:
                hour24 += 12
            bt = time(hour24, minute)

            geolocator = Nominatim(user_agent="jyotish_app_v8")
            location = geolocator.geocode(place)

            if not location:
                st.error("जन्म स्थान नहीं मिल सका! कृपया स्थान और देश का नाम सही से लिखें।")
            else:
                lat = location.latitude
                lon = location.longitude

                # Automatically detect Timezone and UTC Offset from location
                tf = TimezoneFinder()
                tz_str = tf.timezone_at(lng=lon, lat=lat)
                
                if tz_str:
                    tz_obj = zoneinfo.ZoneInfo(tz_str)
                    local_dt_naive = datetime.combine(dob, bt)
                    local_dt_aware = local_dt_naive.replace(tzinfo=tz_obj)
                    utc_offset_hours = local_dt_aware.utcoffset().total_seconds() / 3600.0
                    utc_dt = local_dt_aware.astimezone(zoneinfo.ZoneInfo("UTC"))
                else:
                    tz_str = "UTC Offset (+5.75 Default)"
                    utc_offset_hours = 5.75
                    local_dt_naive = datetime.combine(dob, bt)
                    utc_dt = local_dt_naive - timedelta(hours=5, minutes=45)

                st.success(f"📍 स्थान मिला: **{location.address}** | ऑटो टाइमज़ोन: **{tz_str} (UTC {utc_offset_hours:+.2f} hrs)** | दर्ज समय: **{hour12}:{minute:02d} {ampm[:2]}**")

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

                # 3. DASHA TIMELINE & PREDICTIONS
                section_heading("3. महादशा एवं अंतर्दशा का विस्तृत फलादेश (Dasha Predictions)", "⏳")

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

                now_dt = datetime.now()
                all_md_rows = []
                current_start_date = local_dt_naive
                active_md = ""

                for m_idx in range(9):
                    md_lord_i = (first_md_lord_idx + m_idx) % 9
                    md_name = DASHA_LORDS[md_lord_i]
                    md_total_years = DASHA_YEARS[md_name]

                    md_duration_years = remaining_first_md_years if m_idx == 0 else md_total_years
                    md_end_date = current_start_date + timedelta(days=md_duration_years * 365.25)

                    is_active = current_start_date <= now_dt <= md_end_date
                    if is_active:
                        active_md = md_name

                    all_md_rows.append({
                        "महादशा (Mahadasha)": md_name,
                        "प्रारंभ तिथि": current_start_date.strftime("%Y-%m-%d"),
                        "समाप्ति तिथि": md_end_date.strftime("%Y-%m-%d"),
                        "अवधि (वर्ष)": round(md_duration_years, 2),
                        "स्थिति": "🔥 वर्तमान में सक्रिय" if is_active else "-"
                    })
                    current_start_date = md_end_date

                st.dataframe(all_md_rows, use_container_width=True)

                if active_md:
                    with st.expander(f"🌟 वर्तमान सक्रिय महादशा: {active_md} का विस्तृत फलादेश", expanded=True):
                        st.write(f"• **महादशा प्रभाव:** {MAHADASHA_PREDICTIONS.get(active_md, 'यह कालखंड आपके जीवन में नए बदलाव लेकर आएगा।')}")

                # 4. AGE-WISE PREDICTIONS
                section_heading("4. जीवन कालखंड अनुसार अति-विस्तृत महा-फलादेश", "🔮")

                with st.expander("🎓 20 से 30 वर्ष की आयु: शिक्षा, कौशल विकास एवं आजीविका का निर्माण", expanded=True):
                    st.write("""
                    • **करियर एवं कार्यक्षेत्र का निर्माण:** जीवन का यह दशक आपके भविष्य की सबसे मजबूत नींव रखता है। 23 से 26 वर्ष की आयु के बीच करियर में पहला बड़ा और सकारात्मक अवसर प्राप्त होता है।
                    • **आर्थिक स्थिति:** शुरुआती वर्षों में कड़ी मेहनत के बाद 26 वर्ष की आयु से आर्थिक स्थिति में स्पष्ट स्थिरता आने लगेगी।
                    """)

                with st.expander("💍 25 से 35 वर्ष की आयु: विवाह, दांपत्य जीवन एवं पारिवारिक जिम्मेदारियां", expanded=True):
                    st.write("""
                    • **विवाह एवं दांपत्य सुख:** इस कालखंड में विवाह के अत्यंत सुंदर और मजबूत योग बनते हैं। जीवनसाथी समझदार और व्यावहारिक मिलता है।
                    • **भाग्योदय:** विवाह के पश्चात् आपके जीवन में भाग्योदय की गति तेज़ होगी और सामाजिक प्रतिष्ठा में वृद्धि होगी।
                    """)

                with st.expander("🏢 35 से 50 वर्ष की आयु: स्व-अर्जित संपत्ति, अचल संपत्ति एवं स्थायी सफलता", expanded=True):
                    st.write("""
                    • **भूमि, भवन एवं संपत्ति योग:** अपनी मेहनत और अनुभव के बल पर स्वयं का मकान, जमीन या संपत्ति बनाने के प्रबल योग बनते हैं।
                    • **व्यापारिक स्थायित्व:** 35 वर्ष की आयु के बाद स्वतंत्र रूप से कार्य संभालने में अधिक सफलता मिलेगी।
                    """)

                # 5. CAREER & MARRIAGE
                section_heading("5. ग्रहों के अनुसार उपयुक्त करियर एवं विवाह फलादेश", "💼")

                karma_sign_idx = (asc_sign + 9) % 12
                karma_lord = RASHI_LORDS[karma_sign_idx]

                with st.expander("💼 आपके लिए उपयुक्त काम/बिज़नेस", expanded=True):
                    st.write(f"• **कर्मेश ({karma_lord}) के अनुसार उपयुक्त क्षेत्र:** {CAREER_MAP.get(karma_lord, 'व्यापार व स्वतंत्र रोजगार')}")

                partner_label = "पत्नी (Wife)" if "Male" in gender else "पति (Husband)"
                marriage_sign_idx = (asc_sign + 6) % 12
                marriage_lord = RASHI_LORDS[marriage_sign_idx]

                with st.expander(f"💍 {gender} विशेष — विवाह एवं {partner_label} का स्वभाव", expanded=True):
                    st.write(f"• **सप्तमेश ({marriage_lord}) का प्रभाव:** जीवनसाथी समझदार, व्यावहारिक और परिवार की जिम्मेदारी उठाने वाला/वाली होगा/होगी।")

                # 6. ALL 12 HOUSES ANALYSIS
                section_heading("6. समस्त 12 भावों का अति-विस्तृत फलादेश", "🏛️")

                house_details = [
                    ("प्रथम भाव (तनु भाव)", "व्यक्तित्व, शारीरिक सौष्ठव, आत्मबल, विचार और स्वास्थ्य का प्रतिनिधित्व करता है।"),
                    ("द्वितीय भाव (धन भाव)", "कुटुंब, वाणी, प्रारंभिक शिक्षा, संचित धन और संपत्ति का भाव है।"),
                    ("तृतीय भाव (सहज भाव)", "पराक्रम, कार्यक्षमता, साहस, संचार और भाई-बहनों का स्थान है।"),
                    ("चतुर्थ भाव (सुख भाव)", "माता का सुख, घर का वातावरण, वाहन, भूमि और अचल संपत्ति का प्रतीक है।"),
                    ("पंचम भाव (बुद्धि भाव)", "सोचने की क्षमता, बौद्धिक ज्ञान, निर्णय शक्ति और संतान का भाव है।"),
                    ("षष्ठ भाव (रिपु भाव)", "प्रतिस्पर्धा, दैनिक कार्यशैली, ऋण और बाधाओं से निपटने का भाव है।"),
                    ("सप्तम भाव (जाया भाव)", "वैवाहिक जीवन, जीवनसाथी का स्वभाव, साझेदारी और सामाजिक संबंध का भाव है।"),
                    ("अष्टम भाव (आयु भाव)", "आयु, अचानक होने वाले परिवर्तन, शोध और गुप्त विद्याओं का स्थान है।"),
                    ("नवम भाव (भाग्य भाव)",
