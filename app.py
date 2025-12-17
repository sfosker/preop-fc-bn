import streamlit as st

st.set_page_config(page_title="Pre-op Functional Capacity", layout="centered")

st.title("Pre-operative Functional Capacity (Demo)")
st.write("This is a simple prototype using questionnaire inputs to estimate functional capacity and generate personalised advice.")

with st.form("preop_form"):
    st.subheader("Activity")

    stairs = st.radio(
        "How many flights of stairs can you climb without stopping?",
        ["0", "1", "2 or more"],
    )

    walk = st.radio(
        "Can you walk briskly for 10 minutes on the flat?",
        ["No", "Yes, but need to slow/stop", "Yes, easily"],
    )

    carry = st.radio(
        "Can you carry two shopping bags for about 50 metres?",
        ["No", "Yes, with difficulty", "Yes, easily"],
    )

    st.subheader("Steps (last 7 days)")
    steps = st.selectbox(
        "Average daily steps:",
        ["< 2,000", "2,000–4,999", "5,000–7,999", "8,000+", "Not sure"],
    )

    st.subheader("Symptoms / Limiters")
    breathless = st.radio(
        "Do you get short of breath doing ordinary activities (dressing, walking around the house)?",
        ["No", "Sometimes", "Often"],
    )

    pain_limit = st.radio(
        "Does pain (hips/knees/back) limit your walking or stairs?",
        ["No", "Somewhat", "Severely"],
    )

    fatigue = st.radio(
        "How much does fatigue limit your daily activity?",
        ["Not at all", "Somewhat", "A lot"],
    )

    recent_change = st.radio(
        "Compared with 1 month ago, your activity level is:",
        ["Same or better", "A bit worse", "Much worse"],
    )

    st.subheader("Sleep")
    sleep_hours = st.selectbox(
        "Average sleep per night (last week):",
        ["< 5 hours", "5–6 hours", "6–8 hours", "> 8 hours"],
    )
    sleep_quality = st.selectbox(
        "Overall sleep quality:",
        ["Poor", "OK", "Good"],
    )

    st.subheader("Diet")
    protein = st.selectbox(
        "Most days, do you include a protein food in 2 or more meals?",
        ["Yes", "No", "Not sure"],
    )
    weight_loss = st.selectbox(
        "Unplanned weight loss in last 3 months:",
        ["No", "1–3 kg", "> 3 kg", "Not sure"],
    )

    st.subheader("Smoking, alcohol & conditions")
    smoking = st.selectbox(
        "Smoking:",
        ["Never smoked", "Ex-smoker (> 8 weeks)", "Ex-smoker (≤ 8 weeks)", "Current smoker", "Prefer not to say"],
    )

    alcohol_freq = st.selectbox(
        "How often do you drink alcohol?",
        ["Never", "Monthly or less", "2–4 times a month", "2–3 times a week", "4+ times a week"],
    )

    alcohol_binge = st.selectbox(
        "How often do you have 6+ units on one occasion?",
        ["Never", "Less than monthly", "Monthly", "Weekly", "Daily or almost daily"],
    )

    diabetes = st.selectbox(
        "Have you been diagnosed with diabetes?",
        ["No", "Yes", "Not sure"],
    )

    stroke = st.selectbox(
        "Have you ever had a stroke or TIA (mini-stroke)?",
        ["No", "Yes", "Not sure"],
    )

    hypertension = st.selectbox(
        "Have you been told you have high blood pressure?",
        ["No", "Yes", "Not sure"],
    )

    submitted = st.form_submit_button("Calculate")

def score_task_performance(stairs, walk, carry, pain_limit):
    # Basic scoring logic from our BN design
    stairs_s = {"0": 0, "1": 1, "2 or more": 2}[stairs]
    walk_s = {"No": 0, "Yes, but need to slow/stop": 1, "Yes, easily": 2}[walk]
    carry_s = {"No": 0, "Yes, with difficulty": 1, "Yes, easily": 2}[carry]

    base = min(stairs_s, walk_s, carry_s)
    if pain_limit == "Severely":
        base = max(0, base - 1)

    if base == 0:
        return "Poor"
    elif base == 1:
        return "Moderate"
    else:
        return "Good"

def score_steps(steps):
    if steps == "< 2,000":
        return "Low"
    elif steps in ["2,000–4,999", "5,000–7,999"]:
        return "Moderate"
    elif steps == "8,000+":
        return "High"
    else:
        return "Unknown"

def score_reserve(steps_level, fatigue, recent_change, sleep_hours, sleep_quality, protein, weight_loss):
    # Very simple rule-based “reserve” score
    score = 0

    if steps_level == "High":
        score += 1
    elif steps_level == "Low":
        score -= 1

    if fatigue == "A lot":
        score -= 1
    elif fatigue == "Not at all":
        score += 1

    if recent_change == "Much worse":
        score -= 1
    elif recent_change == "Same or better":
        score += 1

    if sleep_hours == "6–8 hours":
        score += 1
    elif sleep_hours == "< 5 hours":
        score -= 1

    if sleep_quality == "Good":
        score += 1
    elif sleep_quality == "Poor":
        score -= 1

    if protein == "Yes":
        score += 1
    elif protein == "No":
        score -= 1

    if weight_loss == "> 3 kg":
        score -= 1

    if score <= -1:
        return "Low"
    elif score <= 1:
        return "Moderate"
    else:
        return "High"

def estimate_fc(task_perf, reserve, breathless):
    # Crude deterministic-with-noise surrogate
    # Start from task performance
    fc = task_perf

    if reserve == "Low" and fc == "Good":
        fc = "Moderate"
    if reserve == "Low" and fc == "Moderate":
        fc = "Poor"
    if reserve == "High" and fc == "Poor":
        fc = "Moderate"

    if breathless == "Often" and fc == "Good":
        fc = "Moderate"
    if breathless == "Often" and fc == "Moderate":
        fc = "Poor"

    return fc

def advice_cards(smoking, alcohol_freq, alcohol_binge, diabetes, stroke, hypertension):
    adv = []

    if smoking in ["Current smoker", "Ex-smoker (≤ 8 weeks)"]:
        adv.append("• Support to stop smoking before surgery (e.g. referral to a stop-smoking service).")

    risky_alc = alcohol_freq in ["2–3 times a week", "4+ times a week"] or alcohol_binge in ["Weekly", "Daily or almost daily"]
    if risky_alc:
        adv.append("• Review alcohol intake and consider brief intervention / support to cut down.")

    if diabetes == "Yes":
        adv.append("• Check diabetes control and medication plan before surgery.")

    if hypertension == "Yes":
        adv.append("• Ensure blood pressure is checked and optimised pre-operatively.")

    if stroke == "Yes":
        adv.append("• Confirm stroke/TIA secondary prevention and peri-operative plan with the medical team.")

    return adv

if submitted:
    task_perf = score_task_performance(stairs, walk, carry, pain_limit)
    steps_level = score_steps(steps)
    reserve = score_reserve(steps_level, fatigue, recent_change, sleep_hours, sleep_quality, protein, weight_loss)
    fc = estimate_fc(task_perf, reserve, breathless)

    st.markdown("### Estimated Functional Capacity")
    st.write(f"**Task performance:** {task_perf}")
    st.write(f"**Overall reserve:** {reserve}")
    st.success(f"**Estimated functional capacity: {fc}** (prototype)")

    st.markdown("### Personalised Advice (Prototype)")
    adv = advice_cards(smoking, alcohol_freq, alcohol_binge, diabetes, stroke, hypertension)
    if adv:
        for a in adv:
            st.info(a)
    else:
        st.write("No specific risk-factor advice triggered in this prototype.")
