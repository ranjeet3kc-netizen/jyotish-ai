import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date, time
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import zoneinfo
from fpdf import FPDF

# Initialize Swiss Ephemeris Settings (Lahiri Ayanamsha)
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

GEMSTONES = {
    "Mangal": "मूँगा (Red Coral)",
    "Shukra": "हीरा / ओपल (Diamond / Opal)",
    "Budh": "पन्ना (Emerald)",
    "Chandra": "मोती (Pearl)",
    "Surya": "माणिक्य (Ruby)",
    "Guru": "पुखराज (Yellow Sapphire)",
    "Shani": "नीलम (Blue Sapphire)"
}

RUDRAKSHA = {
    "Surya": "1 मुखी या 12 मुखी रुद्राक्ष",
    "Chandra": "2 मुखी रुद्राक्ष",
    "Mangal": "3 मुखी रुद्राक्ष",
    "Budh": "4 मुखी रुद्राक्ष",
    "Guru": "5 मुखी रुद्राक्ष",
    "Shukra": "6 मुखी रुद्राक्ष",
    "Shani": "7 मुखी रुद्राक्ष",
    "Rahu": "8 मुखी रुद्राक्ष",
    "Ketu": "9 मुखी रुद्राक्ष"
}

HEALTH_MAP = {
    "Surya": "अस्थि स्वास्थ्य, नेत्र दृष्टि, हृदय प्रणाली, एवं पित्त संबंधी संतुलन पर विशेष ध्यान दें।",
    "Chandra": "मानसिक शांति, अनिद्रा, कफ/जल जनित समस्याएं, एवं श्वसन तंत्र की देखभाल आवश्यक है।",
    "Mangal": "रक्तचाप, एसिडिटी, चोट-चपेट से सावधानी, एवं पाचन अग्नि को संतुलित रखना हितकर है।",
    "Budh": "त्वचा स्वास्थ्य, स्नायु तंत्र (Nervous System), वाणी एवं गले की देखभाल पर ध्यान दें।",
    "Guru": "यकृत (Liver) स्वास्थ्य, कोलेस्ट्रॉल, शुगर/डायबिटीज प्रबंधन, एवं पाचन तंत्र पर ध्यान दें।",
    "Shukra": "वृक्क (Kidney) स्वास्थ्य, हार्मोनल संतुलन, एवं शरीर में शर्करा स्तर की नियमित जांच रखें।",
    "Shani": "अस्थि संधि (Joints), वात संतुलन, दांतों की देखभाल, एवं शारीरिक दिनचर्या में अनुशासन रखें।",
    "Rahu": "अचानक स्वास्थ्य उतार-चढ़ाव, मानसिक तनाव, एलर्जी, एवं एंग्जाइटी से बचाव के लिए योग करें।",
    "Ketu": "त्वचा संबंधी संवेदनशीलता, उदर स्वास्थ्य, एवं शारीरिक ऊर्जा स्तर को बनाए रखने के उपाय करें।"
}

MAHADASHA_PREDICTIONS = {
    "Surya": "सूर्य की महादशा आत्मबल, अधिकार, सामाजिक प्रतिष्ठा और प्रशासनिक कार्यों में सफलता प्रदान करती है। अहंकार से बचें।",
    "Chandra": "चंद्रमा की महादशा मन की संवेदनशीलता, रचनात्मकता और मानसिक सुख लाती है। माता का सहयोग मिलता है।",
    "Mangal": "मंगल की महादशा असीम ऊर्जा, साहस, पराक्रम, भूमि और तकनीकी कार्यों में बड़ी सफलता का काल है।",
    "Budh": "बुध की महादशा बुद्धि, ज्ञान, संचार, बैंकिंग, लेखन और व्यापारिक कुशाग्रता का काल मानी जाती है।",
    "Guru": "बृहस्पति की महादशा सुख, समृद्धि, उच्च शिक्षा, आध्यात्मिक ज्ञान और दांपत्य जीवन में वृद्धि लाती है।",
    "Shukra": "शुक्र की महादशा भौतिक सुख-सुविधाओं, वाहन, आभूषण, कला और विलासिता का स्वर्णिम काल होती है।",
    "Shani": "शनि की महादशा कड़े परिश्रम, अनुशासन और परिपक्वता का काल है। यह स्थायी और दीर्घकालिक फल देती है।",
    "Rahu": "राहु की महादशा अचानक बदलाव, आधुनिक तकनीक, विदेशी व्यापार और लीक से हटकर सोचने का अवसर देती है।",
    "Ketu": "केतु की महादशा आध्यात्म, गुप्त विद्याओं, शोध और आत्म-साक्षात्कार का काल है। अंतर्दृष्टि मजबूत होती है।"
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
        
        # ग्रहों के नाम ओवरलैप होने से बचाने के लिए छोटा फॉन्ट और फॉर्मेटिंग
        if len(planets_in_house) > 2:
            p_str = ", ".join(planets_in_house[:2]) + "\n" + ", ".join(planets_in_house[2:])
            font_size = 6.5
        else:
            p_str = "\n".join(planets_in_house) if planets_in_house else ""
            font_size = 7.5

        ax.text(x, y + 0.05, f"{sign_index + 1}", color="darkred", fontsize=10, weight="bold", ha="center")
        if p_str:
            ax.text(x, y - 0.06, p_str, color="navy", fontsize=font_size, ha="center")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title, fontsize=12, pad=10, color="maroon", weight="bold")
    return fig
    import io

def generate_pdf_report(name, dob_str, place_str, asc_sign_name, moon_sign_name, active_md, active_ad, yoga_list, rows_data=None, fig_chart=None, dasha_rows=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "JYOTISH AI - DETAILED HOROSCOPE REPORT", ln=True, align="C")
    pdf.ln(4)

    # Basic Info
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Personal & Birth Details:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    # Using multi_cell to prevent space errors
    pdf.multi_cell(0, 6, f"Name: {name}")
    pdf.multi_cell(0, 6, f"Date of Birth: {dob_str}")
    pdf.multi_cell(0, 6, f"Place of Birth: {place_str}")
    pdf.multi_cell(0, 6, f"Lagna Rashi (Ascendant): {asc_sign_name}")
    pdf.multi_cell(0, 6, f"Moon Rashi: {moon_sign_name}")
    pdf.multi_cell(0, 6, f"Current Active Dasha: {active_md} Mahadasha - {active_ad} Antardasha")
    pdf.ln(4)

    # Yogas Section
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Key Yogas & Horoscope Analysis:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for y in yoga_list:
        clean_y = str(y).encode('ascii', 'ignore').decode('ascii')
        pdf.multi_cell(0, 6, f"- {clean_y}")
    
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, "Generated successfully by Jyotish AI Engine.", ln=True, align="C")

    return pdf.output()
    
    # --- Page Setup ---
st.set_page_config(page_title="Jyotish AI - विस्तृत महा जन्मपत्री", page_icon="🔱", layout="wide")

st.markdown(
    """
    <div style="text-align: center; background: linear-gradient(90deg, #3A0007 0%, #8A1C1C 50%, #3A0007 100%); padding: 25px; border-radius: 12px; border-bottom: 4px solid #FFD700; margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);">
        <h1 style="color: #FFD700; font-size: 34px; font-weight: 800; margin:0;">🔱 JYOTISH AI — अति-विस्तृत महा जन्मपत्री</h1>
        <p style="color: #FFF8DC; font-size: 16px; margin-top: 8px;">Comprehensive Vedic Astrology Engine | गहन विश्लेषण एवं सम्पूर्ण जीवन फलादेश</p>
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
        hour12 = st.number_input("Hour (घंटा)", min_value=1, max_value=12, value=12)
    with t_col2:
        minute = st.number_input("Minute (मिनट)", min_value=0, max_value=59, value=0)
    with t_col3:
        ampm = st.selectbox("AM / PM", ["PM (दोपहर/शाम)", "AM (सुबह/रात)"])

with col_b:
    place = st.text_input("Birth place & Country / जन्म स्थान व देश", value="", placeholder="जैसे: Ghorahi Nepal, Delhi India, London UK")

submitted = st.button("🚀 Generate Full Detailed Report / संपूर्ण विस्तृत महा-रिपोर्ट देखें", type="primary")

if submitted:
    if not name or not dob or not place:
        st.warning("कृपया सभी विवरण (नाम, जन्म तिथि, समय और जन्म स्थान) भरें!")
    else:
        try:
            hour24 = hour12 % 12
            if "PM" in ampm:
                hour24 += 12
            bt = time(hour24, minute)

            geolocator = Nominatim(user_agent="jyotish_app_v14")
            location = geolocator.geocode(place)

            if not location:
                st.error("जन्म स्थान नहीं मिल सका! कृपया स्थान और देश का नाम सही से लिखें।")
            else:
                lat = location.latitude
                lon = location.longitude

                tf = TimezoneFinder()
                tz_str = tf.timezone_at(lng=lon, lat=lat)
                
                # सही टाइमज़ोन कन्वर्जन
                local_dt_naive = datetime.combine(dob, bt)
                if tz_str:
                    tz_obj = zoneinfo.ZoneInfo(tz_str)
                    local_dt_aware = datetime.combine(dob, bt, tzinfo=tz_obj)
                    utc_dt = local_dt_aware.astimezone(zoneinfo.ZoneInfo("UTC"))
                    utc_offset_hours = local_dt_aware.utcoffset().total_seconds() / 3600.0
                else:
                    tz_str = "UTC Offset (+5.75 Default)"
                    utc_offset_hours = 5.75
                    utc_dt = local_dt_naive - timedelta(hours=5, minutes=45)

                st.success(f"📍 स्थान मिला: **{location.address}** | टाइमज़ोन: **{tz_str} (UTC {utc_offset_hours:+.2f} hrs)** | समय: **{hour12}:{minute:02d} {ampm[:2]}**")

                jd = swe.julday(
                    utc_dt.year,
                    utc_dt.month,
                    utc_dt.day,
                    utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
                )

                flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

                # 1. PLANETARY POSITIONS
                section_heading("1. ग्रह स्थिति एवं नवमांश विवरण (Planetary Positions)", "🪐")

                rows = []
                d1_planet_signs = {}
                d9_planet_signs = {}
                planet_positions_map = {}
                moon_sign_idx = 0

                for planet, code in PLANETS.items():
                    res = swe.calc_ut(jd, code, flags)
                    degree = res[0][0] % 360
                    speed = res[0][3]

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

                # Ketu Calculation (180 degrees from Rahu)
                rahu_res = swe.calc_ut(jd, swe.MEAN_NODE, flags)
                rahu_deg = rahu_res[0][0] % 360
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

                # 2. CHARTS & LAGNA (Accurate Sidereal Ayanamsha)
                ayanamsha = swe.get_ayanamsa_ut(jd)
                res_houses = swe.houses(jd, lat, lon, b'P')
                asc_tropical = res_houses[1][0]
                asc_degree = (asc_tropical - ayanamsha) % 360
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

                # 3. DASHA & ANTARDASHA (Full 120-Year Life Cycle)
                section_heading("3. महादशा एवं अंतर्दशा का विस्तृत फलादेश (Dasha Analysis)", "⏳")

                moon_res = swe.calc_ut(jd, swe.MOON, flags)
                moon_degree = moon_res[0][0] % 360
                nak_span = 360.0 / 27.0
                moon_nak_idx = int(moon_degree / nak_span)

                deg_in_nak = moon_degree % nak_span
                balance_fraction = 1.0 - (deg_in_nak / nak_span)

                first_md_lord_idx = moon_nak_idx % 9
                first_md_lord = DASHA_LORDS[first_md_lord_idx]
                first_md_years = DASHA_YEARS[first_md_lord]
                remaining_first_md_years = first_md_years * balance_fraction

                now_dt = datetime.now()
                current_start_date = local_dt_naive
                active_md = ""
                active_ad = ""
                all_md_rows = []

                # कुल 14 चक्र लूप ताकि 100+ वर्ष के जातक की दशा कभी अधूरी न छूटे
                for m_idx in range(14):
                    md_lord_i = (first_md_lord_idx + m_idx) % 9
                    md_name = DASHA_LORDS[md_lord_i]
                    md_total_years = DASHA_YEARS[md_name]

                    md_duration_years = remaining_first_md_years if m_idx == 0 else md_total_years
                    md_end_date = current_start_date + timedelta(days=md_duration_years * 365.25)

                    is_active_md = current_start_date <= now_dt <= md_end_date
                    if is_active_md:
                        active_md = md_name
                        ad_start = current_start_date
                        for a_idx in range(9):
                            ad_lord_i = (md_lord_i + a_idx) % 9
                            ad_name = DASHA_LORDS[ad_lord_i]
                            ad_years = (md_total_years * DASHA_YEARS[ad_name]) / 120.0
                            ad_end = ad_start + timedelta(days=ad_years * 365.25)
                            if ad_start <= now_dt <= ad_end:
                                active_ad = ad_name
                                break
                            ad_start = ad_end

                    all_md_rows.append({
                        "महादशा (Mahadasha)": md_name,
                        "प्रारंभ तिथि": current_start_date.strftime("%Y-%m-%d"),
                        "समाप्ति तिथि": md_end_date.strftime("%Y-%m-%d"),
                        "अवधि (वर्ष)": round(md_duration_years, 2),
                        "स्थिति": "🔥 वर्तमान में सक्रिय" if is_active_md else "-"
                    })
                    current_start_date = md_end_date

                    # यदि जातक की आयु 100 वर्ष पार हो जाए तो लूप रोकें
                    if (current_start_date - local_dt_naive).days > 365.25 * 105:
                        break

                st.dataframe(all_md_rows, use_container_width=True)

                if active_md:
                    with st.expander(f"🌟 वर्तमान सक्रिय महादशा ({active_md}) {f'एवं अंतर्दशा ({active_ad})' if active_ad else ''} का प्रभाव", expanded=True):
                        st.write(f"• **महादशापति ({active_md}) का प्रभाव:** {MAHADASHA_PREDICTIONS.get(active_md, 'यह कालखंड आपके जीवन में नए अवसर लाएगा।')}")
                        if active_ad:
                            st.write(f"• **अंतर्दशापति ({active_ad}) का प्रभाव:** वर्तमान समय में आपके दैनिक निर्णयों और परिणामों पर **{active_ad}** का मुख्य प्रभाव है।")

                # 4. HEALTH REPORT
                section_heading("4. स्वास्थ्य एवं शारीरिक आरोग्य (Health Report)", "🏥")
                sixth_sign_idx = (asc_sign + 5) % 12
                sixth_lord = RASHI_LORDS[sixth_sign_idx]

                with st.expander("🏥 रोग प्रतिरोधक क्षमता एवं स्वास्थ्य सावधानियां", expanded=True):
                    st.write(f"• **षष्ठ भाव (रोग स्थान):** इस भाव में **{SIGNS[sixth_sign_idx]} ({SIGNS_HI[sixth_sign_idx]})** राशि है, जिसके स्वामी **{sixth_lord}** हैं।")
                    st.write(f"• **स्वास्थ्य निर्देश:** {HEALTH_MAP.get(sixth_lord, 'सामान्य स्वास्थ्य उत्तम रहेगा। नियमित दिनचर्या रखें।')}")

                # 5. LOVE & RELATIONSHIPS
                section_heading("5. प्रेम, संबंध एवं वैवाहिक जीवन", "❤️")
                fifth_sign_idx = (asc_sign + 4) % 12
                fifth_lord = RASHI_LORDS[fifth_sign_idx]
                seventh_sign_idx = (asc_sign + 6) % 12
                seventh_lord = RASHI_LORDS[seventh_sign_idx]

                with st.expander("❤️ प्रेम संबंध एवं वैवाहिक विश्लेषण", expanded=True):
                    st.write(f"• **पंचमेश (बुद्धि व प्रेम):** {fifth_lord} — भावनात्मक समझ और संबंधों में ईमानदारी सहायक होगी।")
                    st.write(f"• **सप्तमेश (दांपत्य जीवन):** {seventh_lord} — जीवनसाथी के साथ तालमेल बनाए रखने से गृहस्थ जीवन सुखद रहेगा।")

                # 6. YOGAS & RAJYOGA ANALYSIS
                section_heading("6. कुंडली में स्थित प्रमुख राजयोग एवं धनयोग", "👑")
                detected_yogas = []

                if planet_positions_map.get("Surya") == planet_positions_map.get("Budh"):
                    detected_yogas.append("बुधादित्य योग (Budhaditya Yoga): सूर्य और बुध की युति से कुशाग्र बुद्धि, नेतृत्व क्षमता और मान-सम्मान प्राप्त होता है।")

                guru_p = planet_positions_map.get("Guru")
                chandra_p = planet_positions_map.get("Chandra")
                if guru_p is not None and chandra_p is not None:
                    # गजकेसरी योग: चंद्रमा से गुरु 1, 4, 7 या 10वें भाव में हो
                    diff = (guru_p - chandra_p) % 12
                    if diff in [0, 3, 6, 9]:
                        detected_yogas.append("गजकेसरी योग (Gajakesari Yoga): गुरु और चंद्रमा का केंद्र संबंध असीम ज्ञान, प्रतिष्ठा और स्थायी समृद्धि प्रदान करता है।")

                if not detected_yogas:
                    detected_yogas.append("लग्न और केंद्र भावों का संबंध आपके जीवन को सतत प्रगतिशील बनाता है।")

                for y in detected_yogas:
                    st.success(f"• {y}")

                # 7. REMEDIES & PDF DOWNLOAD
                section_heading("7. शुभ रत्न, रुद्राक्ष एवं उपाय (Remedies)", "💎")
                lagna_lord = RASHI_LORDS[asc_sign]
                st.write(f"• **जीवनरत्न (Lagna Gemstone):** `{GEMSTONES.get(lagna_lord, 'नेचुरल ओपल')}`")
                st.write(f"• **शुभ रुद्राक्ष:** **{RUDRAKSHA.get(lagna_lord, '5 मुखी रुद्राक्ष')}**")

                st.markdown("---")
                pdf_bytes = generate_pdf_report(
                    name, dob.strftime("%Y-%m-%d"), location.address,
                    SIGNS[asc_sign], SIGNS[moon_sign_idx],
                    active_md, active_ad, detected_yogas
                )
                st.download_button(
                    label="📄 Download Complete Kundli PDF Report",
                    data=bytes(pdf_bytes),
                    file_name=f"{name}_Jyotish_Report.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"Calculation error: {e}")
