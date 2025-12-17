import streamlit as st

st.set_page_config(page_title="Pre-op Functional Capacity", layout="centered")

st.title("Pre-operative Functional Capacity (Demo)")
st.write(
    "Prototype tool using questionnaire inputs to estimate functional capacity "
    "and generate personalised advice. Not for clinical decision-making."
)

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


# --------- SCORING & EXPLANATION FUNCTIONS --------- #

def score_task_performance(stairs, walk, carry, pain_limit):
    """Return task performance category plus internal scores for explanation."""
    stairs_s = {"0": 0, "1": 1, "2 or more": 2}[stairs]
    walk_s = {"No": 0, "Yes, but need to slow/stop": 1, "Yes, easily": 2}[walk]
    carry_s = {"No": 0, "Yes, with difficulty": 1, "Yes, easily": 2}[carry]

    base = min(stairs_s, walk_s, carry_s)
    original_base = base

    if pain_limit == "Severely":
        base = max(0, base - 1)

    if base == 0:
        perf = "Poor"
    elif base == 1:
        perf = "Moderate"
    else:
        perf = "Good"

    debug = {
        "stairs_score": stairs_s,
        "walk_score": walk_s,
        "carry_score": carry_s,
        "base_min_score": original_base,
        "pain_adjusted_base": base,
    }

    return perf, debug


def score_steps(steps):
    if steps == "< 2,000":
        return "Low"
    elif steps in ["2,000–4,999", "5,000–7,999"]:
        return "Moderate"
    elif steps == "8,000+":
        return "High"
    else:
        return "Unknown"


def score_reserve(
    steps_level,
    fatigue,
    recent_change,
    sleep_hours,
    sleep_quality,
    protein,
    weight_loss,
):
    """Simple numeric aggregate → Low / Moderate / High + debug info."""
    score = 0
    components = {}

    # Steps
    if steps_level == "High":
        score += 1
        components["steps"] = "+1 (High steps)"
    elif steps_level == "Low":
        score -= 1
        components["steps"] = "-1 (Low steps)"
    else:
        components["steps"] = "0 (Moderate/Unknown steps)"

    # Fatigue
    if fatigue == "A lot":
        score -= 1
        components["fatigue"] = "-1 (Fatigue a lot)"
    elif fatigue == "Not at all":
        score += 1
        components["fatigue"] = "+1 (No fatigue)"
    else:
        components["fatigue"] = "0 (Somewhat)"

    # Recent change
    if recent_change == "Much worse":
        score -= 1
        components["recent_change"] = "-1 (Much worse)"
    elif recent_change == "Same or better":
        score += 1
        components["recent_change"] = "+1 (Same/better)"
    else:
        components["recent_change"] = "0 (A bit worse)"

    # Sleep hours
    if sleep_hours == "6–8 hours":
        score += 1
        components["sleep_hours"] = "+1 (6–8h)"
    elif sleep_hours == "< 5 hours":
        score -= 1
        components["sleep_hours"] = "-1 (<5h)"
    else:
        components["sleep_hours"] = "0 (5–6h or >8h)"

    # Sleep quality
    if sleep_quality == "Good":
        score += 1
        components["sleep_quality"] = "+1 (Good quality)"
    elif sleep_quality == "Poor":
        score -= 1
        components["sleep_quality"] = "-1 (Poor quality)"
    else:
        components["sleep_quality"] = "0 (OK)"

    # Nutrition (protein)
    if protein == "Yes":
        score += 1
        components["protein"] = "+1 (Protein most days)"
    elif protein == "No":
        score -= 1
        components["protein"] = "-1 (No protein 2+ meals)"
    else:
        components["protein"] = "0 (Not sure)"

    # Weight loss
    if weight_loss == "> 3 kg":
        score -= 1
        components["weight_loss"] = "-1 (>3 kg loss)"
    elif weight_loss == "1–3 kg":
        components["weight_loss"] = "0 (1–3kg)"
    else:
        components["weight_loss"] = "0 (No/Not sure)"

    if score <= -1:
        reserve = "Low"
    elif score <= 1:
        reserve = "Moderate"
    else:
        reserve = "High"

    debug = {
        "aggregate_score": score,
        "components": components,
    }

    return reserve, debug


def estimate_fc(task_perf, reserve, breathless):
    """
    FC logic + explanation steps.
    FC starts at task performance, then is adjusted by reserve and symptoms.
    """
    explanation = []
    fc = task_perf
    explanation.append(f"Start from Task Performance = {task_perf}")

    # Reserve adjustments
    if reserve == "Low" and fc == "Good":
        explanation.append("Reserve is Low → downgrade Good → Moderate")
        fc = "Moderate"
    if reserve == "Low" and fc == "Moderate":
        explanation.append("Reserve is Low → downgrade Moderate → Poor")
        fc = "Poor"
    if reserve == "High" and fc == "Poor":
        explanation.append("Reserve is High → upgrade Poor → Moderate")
        fc = "Moderate"

    # Symptoms (breathlessness) adjustments
    if breathless == "Often" and fc == "Good":
        explanation.append("Breathlessness Often → downgrade Good → Moderate")
        fc = "Moderate"
    if breathless == "Often" and fc == "Moderate":
        explanation.append("Breathlessness Often → downgrade Moderate → Poor")
        fc = "Poor"

    explanation.append(f"Final FC = {fc}")
    return fc, explanation


def advice_cards(smoking, alcohol_freq, alcohol_binge, diabetes, stroke, hypertension):
    adv = []

    if smoking in ["Current smoker", "Ex-smoker (≤ 8 weeks)"]:
        adv.append("Support to stop smoking before surgery (e.g. referral to a stop-smoking service).")

    risky_alc = alcohol_freq in ["2–3 times a week", "4+ times a week"] or alcohol_binge in [
        "Weekly",
        "Daily or almost daily",
    ]
    if risky_alc:
        adv.append("Review alcohol intake and consider brief intervention / support to cut down.")

    if diabetes == "Yes":
        adv.append("Check diabetes control and medication plan before surgery.")

    if hypertension == "Yes":
        adv.append("Ensure blood pressure is checked and optimised pre-operatively.")

    if stroke == "Yes":
        adv.append("Confirm stroke/TIA secondary prevention and peri-operative plan with the medical team.")

    return adv


# --------- MAIN CALCULATION & EXPLANATION OUTPUT --------- #

if submitted:
    # Core scoring
    task_perf, task_debug = score_task_performance(stairs, walk, carry, pain_limit)
    steps_level = score_steps(steps)
    reserve, reserve_debug = score_reserve(
        steps_level,
        fatigue,
        recent_change,
        sleep_hours,
        sleep_quality,
        protein,
        weight_loss,
    )
    fc, fc_explanation = estimate_fc(task_perf, reserve, breathless)

    # Summary output
    st.markdown("### Estimated Functional Capacity")
    st.write(f"**Task performance:** {task_perf}")
    st.write(f"**Overall reserve:** {reserve}")
    st.write(f"**Breathlessness:** {breathless}")
    st.success(f"**Estimated functional capacity: {fc}** (prototype)")

    # High-level explanation
    st.markdown("### How this result was calculated")
    st.write(
        "The estimate starts from task-based performance (stairs, walk, carry), "
        "then adjusts for overall reserve (steps, fatigue, sleep, nutrition, recent change) "
        "and symptoms (breathlessness)."
    )

    # Detailed reasoning panels
    with st.expander("Detailed task performance calculation"):
        st.write("#### Internal scores")
        st.write(f"- Stairs score: **{task_debug['stairs_score']}** (0=unable, 2=2+ flights)")
        st.write(f"- Walk score: **{task_debug['walk_score']}** (0=no, 2=10 mins easily)")
        st.write(f"- Carry score: **{task_debug['carry_score']}** (0=no, 2=easily)")
        st.write(f"- Base minimum score (before pain): **{task_debug['base_min_score']}**")
        st.write(f"- Pain-adjusted base score: **{task_debug['pain_adjusted_base']}**")
        st.write(f"→ **Task Performance category: {task_perf}**")

    with st.expander("Detailed reserve calculation"):
        st.write("#### Component contributions")
        for name, desc in reserve_debug["components"].items():
            st.write(f"- **{name}**: {desc}")
        st.write(f"**Aggregate reserve score:** {reserve_debug['aggregate_score']}")
        st.write(f"→ **Reserve category: {reserve}**")

    with st.expander("Final FC decision path"):
        for step in fc_explanation:
            st.write("• " + step)

    # Advice
    st.markdown("### Personalised Advice (Prototype)")
    adv = advice_cards(smoking, alcohol_freq, alcohol_binge, diabetes, stroke, hypertension)
    if adv:
        for a in adv:
            st.info(a)
    else:
        st.write("No specific risk-factor advice triggered in this prototype.")
