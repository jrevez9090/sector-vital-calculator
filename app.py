import streamlit as st
import re
import math

st.set_page_config(page_title="Sector Vital Calculator", layout="centered")

st.title("Sector Vital Calculator (Valens Book IV)")

# ============================
# CSS – VISUAL STYLE
# ============================

st.markdown("""
<style>
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
input[type="number"] {
    border: 2px solid #555 !important;
    border-radius: 6px !important;
}

div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"] > div:focus-within,
input[type="number"]:focus {
    border: 2px solid #e74c3c !important;
    outline: none !important;
}

.green {
    color: #2ecc71;
    font-weight: 500;
}

.red {
    color: #e74c3c;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.write("Enter prenatal lunation position and zodiac position for each planet.")
st.write("⚠ Use format exactly like: 12º43'")

st.markdown("---")

# ============================
# STRUCTURE
# ============================

signs = [
    "Aries","Taurus","Gemini","Cancer",
    "Leo","Virgo","Libra","Scorpio",
    "Sagittarius","Capricorn","Aquarius","Pisces"
]

def sign_to_degree(sign, degree, minutes):
    return signs.index(sign) * 30 + degree + (minutes / 60)

def years_to_ymd(years):
    y = int(years)
    remaining = (years - y) * 12
    m = int(remaining)
    d = int((remaining - m) * 30)
    return y, m, d

# ============================
# PRENATAL LUNATION
# ============================

st.markdown("### Prenatal Lunation Position")

col1, col2 = st.columns(2)

with col1:
    lun_sign = st.selectbox("Lunation Sign", signs)

with col2:
    lun_text = st.text_input("Lunation Position (format: 12º43')")

lun_degree = None

if lun_text:
    match = re.fullmatch(r"(\d{1,2})º(\d{1,2})'", lun_text.strip())
    if match:
        deg = int(match.group(1))
        mins = int(match.group(2))
        if 0 <= deg <= 29 and 0 <= mins <= 59:
            lun_degree = sign_to_degree(lun_sign, deg, mins)

st.markdown("---")

# ============================
# PLANETS
# ============================

planets = {}
planet_names = ["Saturn","Jupiter","Mars","Venus","Mercury","Sun","Moon"]

for planet in planet_names:
    col1, col2 = st.columns(2)

    with col1:
        sign = st.selectbox(f"{planet} Sign", signs, key=f"{planet}_sign")

    with col2:
        pos_text = st.text_input(f"{planet} Position (format: 12º43')", key=f"{planet}_pos")

    degree = 0
    minutes = 0

    if pos_text:
        match = re.fullmatch(r"(\d{1,2})º(\d{1,2})'", pos_text.strip())
        if match:
            degree = int(match.group(1))
            minutes = int(match.group(2))

    planets[planet] = sign_to_degree(sign, degree, minutes)

# ============================
# PERIODS
# ============================

periods = {
    "Saturn":30,
    "Jupiter":12,
    "Mars":15,
    "Venus":8,
    "Mercury":20,
    "Sun":19,
    "Moon":25
}

# ============================
# CALCULATION
# ============================

if st.button("Calculate") and lun_degree is not None:

    sorted_planets = sorted(planets.items(), key=lambda x: x[1])

    afeta = None
    for name, degree in sorted_planets:
        if degree > lun_degree:
            afeta = name
            break
    if not afeta:
        afeta = sorted_planets[0][0]

    st.session_state.afeta = afeta

    start_index = next(i for i,(n,_) in enumerate(sorted_planets) if n == afeta)
    ordered = sorted_planets[start_index:] + sorted_planets[:start_index]

    base_cycle = []
    cumulative = 0

    for name,_ in ordered:
        duration = periods[name] / 4
        cumulative += duration
        base_cycle.append((name,duration,cumulative))

    st.session_state.base_cycle = base_cycle

# ============================
# DISPLAY
# ============================

if "base_cycle" in st.session_state:

    st.markdown(f"### Initial Afeta: <span class='red'>{st.session_state.afeta}</span>", unsafe_allow_html=True)

    cycle_length = st.session_state.base_cycle[-1][2]

        # ---------- 1st CYCLE ----------
    st.markdown("## 1st Cycle")
    cycle1 = st.session_state.base_cycle
    for name,duration,cum in cycle1:
        y,m,d = years_to_ymd(duration)
        st.markdown(
            f"{name} - <span class='green'>{y}y {m}m {d}d</span> "
            f"(cumulative: <span class='green'>{round(cum,3)}</span>)",
            unsafe_allow_html=True
        )

    # ---------- 2nd CYCLE ----------
    st.markdown("## 2nd Cycle")
    cycle2 = cycle1[1:] + cycle1[:1]
    cumulative = 0
    cycle2_display = []
    offset2 = cycle_length  # 32.25

    for name,duration,_ in cycle2:
        cumulative += duration
        absolute_cum = offset2 + cumulative
        cycle2_display.append((name,duration,absolute_cum))
        y,m,d = years_to_ymd(duration)
        st.markdown(
            f"{name} - <span class='green'>{y}y {m}m {d}d</span> "
            f"(cumulative: <span class='green'>{round(absolute_cum,3)}</span>)",
            unsafe_allow_html=True
        )

    # ---------- 3rd CYCLE ----------
    st.markdown("## 3rd Cycle")
    cycle3 = cycle2[1:] + cycle2[:1]
    cumulative = 0
    cycle3_display = []
    offset3 = cycle_length * 2  # 64.50

    for name,duration,_ in cycle3:
        cumulative += duration
        absolute_cum = offset3 + cumulative
        cycle3_display.append((name,duration,absolute_cum))
        y,m,d = years_to_ymd(duration)
        st.markdown(
            f"{name} - <span class='green'>{y}y {m}m {d}d</span> "
            f"(cumulative: <span class='green'>{round(absolute_cum,3)}</span>)",
            unsafe_allow_html=True
        )

    # ---------- ACTIVE CALCULATION ----------
    age = st.number_input("Enter age to check active planet",0.0,120.0)

    completed_cycles = int(age // cycle_length)
    age_mod = age % cycle_length

    if completed_cycles == 0:
        active_cycle = cycle1
        cycle_number = 1
    elif completed_cycles == 1:
        active_cycle = cycle2_display
        cycle_number = 2
    else:
        active_cycle = cycle3_display
        cycle_number = 3

    st.markdown(f"### Active Cycle: {cycle_number}º")
    st.markdown(f"Active Cycle Afeta: <span class='red'>{active_cycle[0][0]}</span>", unsafe_allow_html=True)

    active_planet = None
    prev_cum = 0

    for name,duration,cum in active_cycle:
        if age_mod <= cum:
            active_planet = name
            time_in_main = age_mod - prev_cum
            break
        prev_cum = cum

    st.markdown(f"Active Planet: <span class='red'>{active_planet}</span>", unsafe_allow_html=True)

    # ---------- SUBPERIODS ----------
    fixed_days = {}
    total_days = 0

    for planet,P in periods.items():
        days = (2*P)+(P/2)+(P/3)
        fixed_days[planet]=days
        total_days+=days

    main_duration = periods[active_planet]/4

    start = next(i for i,(n,_,_) in enumerate(active_cycle) if n==active_planet)
    sub_order = active_cycle[start:] + active_cycle[:start]

    cumulative_sub = 0
    sub_active = None
    prev_sub = 0

    st.markdown("### Subperiods")

    for name,_,_ in sub_order:
        proportion = fixed_days[name]/total_days
        sub_duration = main_duration*proportion
        cumulative_sub += sub_duration

        y2,m2,d2 = years_to_ymd(sub_duration)

        st.markdown(
            f"{name} - <span class='green'>{y2}y {m2}m {d2}d</span> "
            f"(cumulative: <span class='green'>{round(cumulative_sub,3)}</span>)",
            unsafe_allow_html=True
        )

        if sub_active is None and time_in_main <= cumulative_sub:
            sub_active = name
            time_inside_sub = time_in_main - prev_sub

        prev_sub = cumulative_sub

    if sub_active:
        y3,m3,d3 = years_to_ymd(time_inside_sub)
        st.markdown(f"### Active Subperiod: <span class='red'>{sub_active}</span>", unsafe_allow_html=True)
        st.markdown(
            f"Elapsed inside subperiod: "
            f"<span class='green'>{y3}y {m3}m {d3}d</span>",
            unsafe_allow_html=True
        )

st.markdown("---")
st.write("Made by Joana Revez")
st.write("Se for encontrado algum erro, reporte para joanarevez@hotmail.com")
