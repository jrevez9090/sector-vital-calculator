import streamlit as st
import re
import math

st.set_page_config(page_title="Sector Vital Calculator", layout="centered")

st.title("Sector Vital Calculator (Valens Book IV)")

# ============================
# CUSTOM STYLING (BORDERS)
# ============================

st.markdown("""
<style>

/* Selectbox */
div[data-baseweb="select"] > div {
    border: 2px solid #555 !important;
    border-radius: 6px !important;
}

/* Text input */
div[data-baseweb="input"] > div {
    border: 2px solid #555 !important;
    border-radius: 6px !important;
}

/* Number input */
input[type="number"] {
    border: 2px solid #555 !important;
    border-radius: 6px !important;
}

/* Focus state */
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"] > div:focus-within,
input[type="number"]:focus {
    border: 2px solid #e74c3c !important;
    outline: none !important;
}

</style>
""", unsafe_allow_html=True)

st.write("Enter prenatal lunation position and zodiac position for each planet.")
st.write("⚠ Use format exactly like: 12º43'")

st.markdown("---")

# ============================
# BASIC STRUCTURE
# ============================

signs = [
    "Aries","Taurus","Gemini","Cancer",
    "Leo","Virgo","Libra","Scorpio",
    "Sagittarius","Capricorn","Aquarius","Pisces"
]

def sign_to_degree(sign, degree, minutes):
    decimal_degree = degree + (minutes / 60)
    return signs.index(sign) * 30 + decimal_degree

def years_to_ymd(years):
    y = int(years)
    remaining = (years - y) * 12
    m = int(remaining)
    d = int((remaining - m) * 30)
    return y, m, d

# ============================
# PRENATAL LUNATION INPUT
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
        else:
            st.error("Invalid lunation degree.")
    else:
        st.error("Invalid lunation format.")

st.markdown("---")

# ============================
# PLANET INPUT
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
            if not (0 <= degree <= 29 and 0 <= minutes <= 59):
                st.error(f"{planet}: invalid degree.")
        else:
            st.error(f"{planet}: invalid format.")

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

    # Primeiro afeta
    afeta = None
    for name, degree in sorted_planets:
        if degree > lun_degree:
            afeta = name
            break

    if not afeta:
        afeta = sorted_planets[0][0]

    # Construir ciclo base
    start_index = next(i for i,(n,_) in enumerate(sorted_planets) if n == afeta)
    ordered = sorted_planets[start_index:] + sorted_planets[:start_index]

    base_cycle = []
    cumulative = 0

    for name,_ in ordered:
        duration = periods[name] / 4
        cumulative += duration
        base_cycle.append((name,duration,cumulative))

    st.session_state.base_cycle = base_cycle
    st.session_state.afeta = afeta

# ============================
# DISPLAY
# ============================

if "base_cycle" in st.session_state:

    st.markdown(f"Afeta inicial: **{st.session_state.afeta}**")

    age = st.number_input("Enter age",0.0,120.0)

    cycle_length = st.session_state.base_cycle[-1][2]  # 32.25

    # Número de ciclos completos
    completed_cycles = int(age // cycle_length)

    # Rodar ciclo
    rotated_cycle = st.session_state.base_cycle.copy()
    for _ in range(completed_cycles):
        first = rotated_cycle.pop(0)
        rotated_cycle.append(first)

    # Recalcular cumulativos no ciclo rodado
    cumulative = 0
    new_cycle = []
    for name,duration,_ in rotated_cycle:
        cumulative += duration
        new_cycle.append((name,duration,cumulative))

    age_mod = age % cycle_length

    active_planet = None
    prev_cum = 0

    for name,duration,cum in new_cycle:
        if age_mod <= cum:
            active_planet = name
            time_in_main = age_mod - prev_cum
            break
        prev_cum = cum

    st.markdown(f"Active planet: **{active_planet}**")

    # ============================
    # SUBPERIODS
    # ============================

    if active_planet:

        st.markdown("### Subperiods")

        fixed_days = {}
        total_days = 0

        for planet,P in periods.items():
            days = (2*P)+(P/2)+(P/3)
            fixed_days[planet]=days
            total_days+=days

        main_duration = periods[active_planet]/4

        # subordem começa no planeta ativo
        sub_order = new_cycle.copy()
        start = next(i for i,(n,_,_) in enumerate(sub_order) if n==active_planet)
        sub_order = sub_order[start:] + sub_order[:start]

        cumulative_sub = 0
        sub_active = None
        prev_sub = 0

        for name,_,_ in sub_order:
            proportion = fixed_days[name]/total_days
            sub_duration = main_duration*proportion
            cumulative_sub+=sub_duration

            if sub_active is None and time_in_main<=cumulative_sub:
                sub_active=name
                break

            prev_sub=cumulative_sub

        st.markdown(f"Active subperiod: **{sub_active}**")

st.markdown("---")
st.write("Feito por Joana Revez")
st.write("Se for encontrado algum erro, reporte para joanarevez@hotmail.com")
