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

def years_to_ymd(years):
    y = int(years)
    remaining = (years - y) * 12
    m = int(remaining)
    d = int((remaining - m) * 30)
    return y, m, d

# INPUT

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

# CALCULATE

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
    st.session_state.quarter_period = periods[afeta] / 4

    cycle = []
    total = 0

    start_index = next(i for i, (name, _) in enumerate(sorted_planets) if name == afeta)
    ordered = sorted_planets[start_index:] + sorted_planets[:start_index]

    for name, degree in ordered:
        duration = periods[name] / 4
        total += duration
        cycle.append((name, duration, total))

    st.session_state.cycle = cycle

# DISPLAY

if "phase" in st.session_state:

    # Lunar Phase (only value red)
    st.markdown(
        f"Lunar Phase: <span style='color:#e74c3c'>{st.session_state.phase}</span>",
        unsafe_allow_html=True
    )

    # Afeta (only planet red)
    st.markdown(
        f"Afeta: <span style='color:#e74c3c'>{st.session_state.afeta}</span>",
        unsafe_allow_html=True
    )

    # Main Period
    y, m, d = years_to_ymd(st.session_state.quarter_period)
    st.markdown(
        f"Main Period Length: "
        f"<span style='color:#2ecc71'>{y}y {m}m {d}d</span>",
        unsafe_allow_html=True
    )

    st.write("Cycle:")

    for name, duration, cumulative in st.session_state.cycle:
        y1, m1, d1 = years_to_ymd(duration)
        st.markdown(
            f"{name} - "
            f"<span style='color:#2ecc71'>{y1}y {m1}m {d1}d</span> "
            f"(cumulative: "
            f"<span style='color:#2ecc71'>{round(cumulative,3)}</span>)",
            unsafe_allow_html=True
        )

    age = st.number_input("Enter age to check active planet", 0.0, 120.0)

    cycle_length = sum(periods[p]/4 for p in periods)
    age_mod = age % cycle_length

    active_planet = None
    previous_cumulative = 0

    for name, duration, cumulative in st.session_state.cycle:
        if age_mod <= cumulative:
            active_planet = name
            time_in_main = age_mod - previous_cumulative
            st.markdown(
                f"Active planet at age {age}: "
                f"<span style='color:#e74c3c'>{name}</span>",
                unsafe_allow_html=True
            )
            break
        previous_cumulative = cumulative

    # SUBPERIODS

    if active_planet:

        st.markdown(f"### Subperiods within {active_planet}")

        fixed_days = {}
        total_days = 0

        for planet, P in periods.items():
            days = (2 * P) + (P / 2) + (P / 3)
            fixed_days[planet] = days
            total_days += days

        main_duration = periods[active_planet] / 4

        sorted_planets = st.session_state.sorted_planets
        start_index = next(i for i, (name, _) in enumerate(sorted_planets) if name == active_planet)
        ordered = sorted_planets[start_index:] + sorted_planets[:start_index]

        cumulative_sub = 0
        sub_active = None
        prev_sub_cumulative = 0

        for name, _ in ordered:
            proportion = fixed_days[name] / total_days
            sub_duration = main_duration * proportion
            cumulative_sub += sub_duration

            y2, m2, d2 = years_to_ymd(sub_duration)

            st.markdown(
                f"{name} - "
                f"<span style='color:#2ecc71'>{y2}y {m2}m {d2}d</span> "
                f"(cumulative: "
                f"<span style='color:#2ecc71'>{round(cumulative_sub,3)}</span>)",
                unsafe_allow_html=True
            )

            if sub_active is None and time_in_main <= cumulative_sub:
                sub_active = name
                time_inside_sub = time_in_main - prev_sub_cumulative

            prev_sub_cumulative = cumulative_sub

        if sub_active:
            y3, m3, d3 = years_to_ymd(time_inside_sub)

            st.markdown("### Active Subperiod:")
            st.markdown(
                f"<span style='color:#e74c3c'>{sub_active}</span>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"Elapsed inside subperiod: "
                f"<span style='color:#2ecc71'>{y3}y {m3}m {d3}d</span>",
                unsafe_allow_html=True
            )

st.markdown("---")
st.write("Feito por Joana R.")


