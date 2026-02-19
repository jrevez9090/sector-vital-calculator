import streamlit as st
import math

st.title("Sector Vital Calculator (Valens Book IV)")

st.write("Enter zodiac positions in degrees (0–360).")
st.write("Example: 15° Aquarius = 315°")

planets = {
    "Saturn": st.number_input("Saturn (0-360)", 0.0, 360.0),
    "Jupiter": st.number_input("Jupiter (0-360)", 0.0, 360.0),
    "Mars": st.number_input("Mars (0-360)", 0.0, 360.0),
    "Venus": st.number_input("Venus (0-360)", 0.0, 360.0),
    "Mercury": st.number_input("Mercury (0-360)", 0.0, 360.0),
    "Sun": st.number_input("Sun (0-360)", 0.0, 360.0),
    "Moon": st.number_input("Moon (0-360)", 0.0, 360.0)
}

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
    st.write("Lunar Phase:", phase)

    # Order planets zodiacally
    sorted_planets = sorted(planets.items(), key=lambda x: x[1])

    # Determine Afeta
    moon_degree = planets["Moon"]
    afeta = None

    for name, degree in sorted_planets:
        if degree > moon_degree:
            afeta = name
            break

    if not afeta:
        afeta = sorted_planets[0][0]

    st.write("Afeta:", afeta)

    quarter_period = periods[afeta] / 4
    st.write("Main Period Length:", round(quarter_period, 2), "years")

    # Build cycle
    cycle = []
    total = 0

    for name, degree in sorted_planets:
        if name == afeta:
            start_index = sorted_planets.index((name, degree))
            break

    ordered = sorted_planets[start_index:] + sorted_planets[:start_index]

    for name, degree in ordered:
        duration = periods[name] / 4
        total += duration
        cycle.append((name, duration, total))

    st.write("Cycle:")
    for name, duration, cumulative in cycle:
        st.write(name, "-", round(duration,2), "years (cumulative:", round(cumulative,2), ")")

    age = st.number_input("Enter age to check active planet", 0.0, 120.0)
    cycle_length = sum(periods[p]/4 for p in periods)

    age_mod = age % cycle_length

    for name, duration, cumulative in cycle:
        if age_mod <= cumulative:
            st.write("Active planet at age", age, ":", name)
            break
