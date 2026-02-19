import streamlit as st

st.title("Sector Vital Calculator (Valens Book IV)")
st.write("Enter zodiac position for each planet.")
st.write("Choose sign, degree (0–29) and minutes (0–59).")

st.markdown("---")

signs = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def sign_to_degree(sign, degree, minutes):
    decimal_degree = degree + (minutes / 60)
    return signs.index(sign) * 30 + decimal_degree

planets = {}
planet_names = ["Saturn", "Jupiter", "Mars", "Venus", "Mercury", "Sun", "Moon"]

for planet in planet_names:
    col1, col2, col3 = st.columns(3)
    with col1:
        sign = st.selectbox(f"{planet} Sign", signs, key=f"{planet}_sign")
    with col2:
        degree = st.number_input(f"{planet} Degree (0-29)", 0, 29, key=f"{planet}_degree")
    with col3:
        minutes = st.number_input(f"{planet} Minutes (0-59)", 0, 59, key=f"{planet}_minutes")
    planets[planet] = sign_to_degree(sign, degree, minutes)

periods = {
    "Saturn": 30,
    "Jupiter": 12,
    "Mars": 15,
    "Venus": 8,
    "Mercury": 20,
    "Sun": 19,
    "Moon": 25
}

def lunar_phase(sun, moon):
    diff = abs(sun - moon)
    if diff > 180:
        diff = 360 - diff
    return "New Moon" if diff < 90 else "Full Moon"

if st.button("Calculate"):

    phase = lunar_phase(planets["Sun"], planets["Moon"])
    st.session_state.phase = phase

    sorted_planets = sorted(planets.items(), key=lambda x: x[1])
    moon_degree = planets["Moon"]

    afeta = None
    for name, degree in sorted_planets:
        if degree > moon_degree:
            afeta = name
            break
    if not afeta:
        afeta = sorted_planets[0][0]

    st.session_state.afeta = afeta
    st.session_state.sorted_planets = sorted_planets

    quarter_period = periods[afeta] / 4
    st.session_state.quarter_period = quarter_period

    cycle = []
    total = 0

    start_index = next(i for i, (name, _) in enumerate(sorted_planets) if name == afeta)
    ordered = sorted_planets[start_index:] + sorted_planets[:start_index]

    for name, degree in ordered:
        duration = periods[name] / 4
        total += duration
        cycle.append((name, duration, total))

    st.session_state.cycle = cycle

if "phase" in st.session_state:

    st.write("Lunar Phase:", st.session_state.phase)
    st.write("Afeta:", st.session_state.afeta)
    st.write("Main Period Length:", round(st.session_state.quarter_period, 2), "years")

    st.write("Cycle:")
    for name, duration, cumulative in st.session_state.cycle:
        st.write(name, "-", round(duration,2), "years (cumulative:", round(cumulative,2), ")")

    age = st.number_input("Enter age to check active planet", 0.0, 120.0)

    cycle_length = sum(periods[p]/4 for p in periods)
    age_mod = age % cycle_length

    for name, duration, cumulative in st.session_state.cycle:
        if age_mod <= cumulative:
            st.write("Active planet at age", age, ":", name)
            break

st.markdown("---")
st.write("Feito por Joana R.")
