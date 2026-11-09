from pathlib import Path
import sys
import textwrap
import re

import pandas as pd
import streamlit as st


# ============================================================
# PATH SETUP
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from prioritization import RICEFramework, create_sample_features

DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = ROOT / "outputs" / "reports"
FIGURES_DIR = ROOT / "outputs" / "figures"
PRDS_DIR = ROOT / "prds"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PrioritiQ — AI Product Decision Copilot",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =========================================================
       GLOBAL APP
       ========================================================= */

    .stApp {
        background: #F7F8FC;
        color: #111827;
    }

    [data-testid="stAppViewContainer"] {
        background: #F7F8FC;
    }

    [data-testid="stMain"] {
        background: #F7F8FC;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 5rem !important;
        padding-bottom: 4rem !important;
    }


    /* =========================================================
       STREAMLIT TEXT OVERRIDES
       ========================================================= */

    .stMarkdown,
    .stMarkdown p,
    .stMarkdown span,
    .stMarkdown li {
        color: #111827;
    }

    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4,
    .stMarkdown h5,
    .stMarkdown h6 {
        color: #111827 !important;
    }

    label,
    [data-testid="stWidgetLabel"] p {
        color: #374151 !important;
    }

    .small-muted {
        color: #667085 !important;
    }


    /* =========================================================
       BRAND
       ========================================================= */

    .brand {
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #111827 !important;
        margin-bottom: 2rem;
    }

    .brand span {
        color: #6D5DFC !important;
    }


    /* =========================================================
       HERO
       ========================================================= */

    .eyebrow {
        color: #6D5DFC !important;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }

    .hero-title {
        font-size: 3.4rem;
        line-height: 1.03;
        letter-spacing: -0.055em;
        font-weight: 850;
        color: #111827 !important;
        margin-bottom: 1rem;
    }

    .hero-subtitle {
        font-size: 1.12rem;
        line-height: 1.65;
        color: #596275 !important;
        max-width: 720px;
        margin-bottom: 1.5rem;
    }


    /* =========================================================
       CARDS
       ========================================================= */

    .card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 1.35rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
    }

    .soft-card {
        background: #F1EFFF;
        border: 1px solid #DDD8FF;
        border-radius: 18px;
        padding: 1.35rem;
        margin-bottom: 1rem;
    }

    .result-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 1.5rem;
        height: 100%;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
    }


    /* =========================================================
       CARD TEXT
       ========================================================= */

    .metric-label {
        font-size: 0.78rem;
        color: #667085 !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 850;
        color: #111827 !important;
        margin-top: 0.2rem;
    }

    .small-muted {
        color: #667085 !important;
        font-size: 0.9rem;
        line-height: 1.55;
    }

    .agent-name {
        font-size: 1.05rem;
        font-weight: 800;
        color: #111827 !important;
    }

    .agent-role {
        color: #667085 !important;
        font-size: 0.88rem;
        margin-top: 0.2rem;
    }

    .feature-name {
        font-size: 1.05rem;
        font-weight: 800;
        color: #111827 !important;
    }

    .rank-number {
        font-size: 1.8rem;
        font-weight: 850;
        color: #6D5DFC !important;
    }


    /* =========================================================
       STEP PILLS
       ========================================================= */

    .step {
        display: inline-block;
        color: #5B4BD8 !important;
        background: #EFEDFF;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 800;
        margin-bottom: 0.6rem;
    }


    /* =========================================================
       TEXT AREA
       ========================================================= */

    [data-testid="stTextArea"] textarea {
        background: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D0D5DD !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: #6D5DFC !important;
        box-shadow: 0 0 0 1px #6D5DFC !important;
    }

    [data-testid="stTextArea"] textarea::placeholder {
        color: #98A2B3 !important;
    }


    /* =========================================================
       BUTTONS
       ========================================================= */

    .stButton > button {
        background: #6D5DFC !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.55rem 1.1rem !important;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: #5948E8 !important;
        color: #FFFFFF !important;
        border: none !important;
    }


    /* =========================================================
       DATAFRAME
       ========================================================= */

    [data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        overflow: hidden;
    }


    /* =========================================================
       METRICS
       ========================================================= */

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 1rem;
    }

    [data-testid="stMetricLabel"] {
        color: #667085 !important;
    }

    [data-testid="stMetricValue"] {
        color: #111827 !important;
    }


    /* =========================================================
       ALERTS
       ========================================================= */

    [data-testid="stAlert"] {
        border-radius: 12px;
    }


    /* =========================================================
       FOOTER
       ========================================================= */

    .footer {
        text-align: center;
        color: #98A2B3 !important;
        font-size: 0.82rem;
        padding-top: 3rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def generate_hypothesis(feature_name):

    hypotheses = {

        "Smart Reorder":
            "Adding a one-click reorder experience will "
            "increase repeat-order conversion among returning customers.",

        "Instant Checkout":
            "Reducing the number of checkout steps will "
            "increase completed-order conversion among users "
            "who initiate checkout.",

        "Schedule Orders":
            "Allowing customers to schedule orders for later "
            "will increase conversion among users with planned-order intent.",

        "Personalized Homepage":
            "Personalizing the homepage around user preferences "
            "will increase engagement and downstream conversion.",

        "Dynamic Pricing":
            "Introducing dynamic pricing based on demand and "
            "availability will improve conversion while maintaining margin.",

    }

    return hypotheses.get(
        feature_name,
        f"Introducing {feature_name} will improve the target "
        "product outcome for the affected customer segment."
    )


def load_csv(filename: str):
    """
    Safely load a CSV from data/processed/.
    Returns None if the file does not exist.
    """
    path = PROCESSED_DIR / filename

    if not path.exists():
        return None

    try:
        return pd.read_csv(path)
    except Exception:
        return None


def find_column(df, possible_names):
    """
    Find a column using flexible name matching.
    """
    if df is None:
        return None

    normalized = {
        str(col).strip().lower().replace(" ", "_"): col
        for col in df.columns
    }

    for name in possible_names:
        key = name.strip().lower().replace(" ", "_")

        if key in normalized:
            return normalized[key]

    return None


def load_rice_results():
    """
    Load the existing RICE results generated by your project.
    """
    return load_csv("rice_scores.csv")


def load_ab_results():
    """
    Load the existing A/B test results generated by your project.
    """
    return load_csv("ab_test_results.csv")


def get_top_features(df, n=5):
    """
    Try to identify the feature and RICE score columns
    without assuming exact column names.
    """
    if df is None or df.empty:
        return None

    feature_col = find_column(
        df,
        [
            "feature",
            "feature_name",
            "name",
            "idea",
            "feature_idea",
        ],
    )

    rice_col = find_column(
        df,
        [
            "rice_score",
            "rice",
            "score",
        ],
    )

    if feature_col is None:
        return None

    result = df.copy()

    if rice_col is not None:
        result[rice_col] = pd.to_numeric(
            result[rice_col],
            errors="coerce",
        )

        result = result.sort_values(
            rice_col,
            ascending=False,
        )

    return result.head(n)


def clean_feedback(text):
    """
    Split pasted customer feedback into individual statements.
    """
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return lines


def demo_themes(feedback):
    """
    Lightweight deterministic demo analysis.

    IMPORTANT:
    This is intentionally not presented as an AI result.
    Replace this function with your LLM Research Agent later.
    """

    combined = " ".join(feedback).lower()

    themes = []

    if any(
        word in combined
        for word in [
            "reorder",
            "again",
            "previous",
            "same order",
            "repeat",
        ]
    ):
        themes.append(
            {
                "theme": "Repeat-order friction",
                "description": (
                    "Customers appear to experience friction "
                    "when repeating previous purchases."
                ),
            }
        )

    if any(
        word in combined
        for word in [
            "checkout",
            "payment",
            "steps",
            "slow",
        ]
    ):
        themes.append(
            {
                "theme": "Checkout friction",
                "description": (
                    "Customers report unnecessary effort "
                    "during checkout."
                ),
            }
        )

    if any(
        word in combined
        for word in [
            "schedule",
            "later",
            "future",
        ]
    ):
        themes.append(
            {
                "theme": "Order scheduling demand",
                "description": (
                    "Customers want greater control over "
                    "when an order is placed or delivered."
                ),
            }
        )

    if not themes:
        themes.append(
            {
                "theme": "General product friction",
                "description": (
                    "The feedback contains potential usability "
                    "or workflow problems requiring deeper research."
                ),
            }
        )

    return themes


def generate_demo_opportunities(themes):
    """
    Convert themes into product opportunities for the prototype.
    """

    opportunities = []

    for theme in themes:

        if theme["theme"] == "Repeat-order friction":
            opportunities.append(
                {
                    "feature": "Smart Reorder",
                    "problem": (
                        "Returning customers need too much effort "
                        "to recreate previous orders."
                    ),
                    "priority": "High",
                }
            )

        elif theme["theme"] == "Checkout friction":
            opportunities.append(
                {
                    "feature": "Instant Checkout",
                    "problem": (
                        "Customers experience unnecessary steps "
                        "during checkout."
                    ),
                    "priority": "High",
                }
            )

        elif theme["theme"] == "Order scheduling demand":
            opportunities.append(
                {
                    "feature": "Schedule Orders",
                    "problem": (
                        "Customers want to plan orders for a "
                        "later time."
                    ),
                    "priority": "Medium",
                }
            )

        else:
            opportunities.append(
                {
                    "feature": "Usability Improvement",
                    "problem": theme["description"],
                    "priority": "Medium",
                }
            )

    return opportunities


def get_demo_experiment():
    """
    Uses the documented Smart Reorder simulation values
    from the existing project as fallback display data.

    These are SYNTHETIC results and must remain labelled as such.
    """

    return {
        "feature": "Smart Reorder",
        "control": 12.00,
        "treatment": 14.16,
        "lift": 18.0,
        "p_value": 0.00001,
        "result": "Statistically Significant",
        "recommendation": "SHIP IT",
    }


def get_existing_experiment():
    """
    Try to read actual generated A/B results first.
    Falls back to the documented project values.
    """

    df = load_ab_results()

    if df is None or df.empty:
        return get_demo_experiment()

    result = get_demo_experiment()

    # Flexible extraction.
    mapping = {
        "control": [
            "control_conversion_rate",
            "control_rate",
            "control_conversion",
        ],
        "treatment": [
            "treatment_conversion_rate",
            "treatment_rate",
            "treatment_conversion",
        ],
        "lift": [
            "relative_lift",
            "lift",
            "relative_lift_percent",
        ],
        "p_value": [
            "p_value",
            "pvalue",
            "p",
        ],
    }

    for key, candidates in mapping.items():
        col = find_column(df, candidates)

        if col is not None and not df.empty:
            try:
                result[key] = float(df.iloc[0][col])
            except Exception:
                pass

    return result


def load_prd(feature_name):
    """
    Load an existing PRD from the repository.

    Currently the repository contains one PRD:
    prds/smart_reorder_prd.md
    """

    if feature_name == "Smart Reorder":

        path = PRDS_DIR / "smart_reorder_prd.md"

        if path.exists():
            return path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

    return None


def generate_prd(feature_name, hypothesis, experiment):
    """
    Generate a lightweight PRD for the selected feature.

    This is the deterministic MVP version.
    Later this will be replaced by the AI PM Documentation Agent.
    """

    prd = f"""
# Product Requirements Document

## Feature

{feature_name}

---

## Problem

Customers are experiencing friction related to {feature_name.lower()}.

The product opportunity was identified through customer feedback
analysis and subsequently prioritized using the RICE framework.

---

## Product Hypothesis

{hypothesis}

---

## Objective

Improve the relevant customer experience and increase the
target product outcome associated with this feature.

---

## User Story

As a customer,
I want an improved {feature_name.lower()} experience,
so that I can complete my intended task with less friction.

---

## Proposed Solution

Design and implement a focused {feature_name.lower()} experience
that reduces unnecessary customer effort while maintaining the
existing product workflow.

---

## Experiment

The feature should first be evaluated through a controlled
A/B experiment.

### Control

Existing product experience.

### Treatment

New {feature_name} experience.

### Experiment Result

Control conversion: {experiment["control"]:.2f}%

Treatment conversion: {experiment["treatment"]:.2f}%

Relative lift: +{experiment["lift"]:.1f}%

P-value: {experiment["p_value"]:.5f}

---

## Success Metrics

### Primary Metric

Conversion rate associated with the target customer action.

### Secondary Metrics

- Completion rate
- Customer engagement
- Drop-off rate
- Repeat usage

---

## Acceptance Criteria

1. The new experience can be accessed by the intended user segment.
2. The existing customer workflow remains functional.
3. The primary conversion event is correctly tracked.
4. Control and treatment experiences can be compared.
5. Experiment results can be evaluated statistically.

---

## Risks

- The feature may not improve the target metric.
- The new workflow may introduce unintended friction.
- Increased conversion may negatively affect another product metric.

---

## Product Decision

The final build decision remains human-owned.

The prioritization score and experiment results provide
decision support rather than automatically making the decision.

---

## Status

Portfolio MVP / Prototype

Synthetic experiment data is used for demonstration.
"""

    return prd


def run_rice_engine():
    """
    Run the project's actual RICE prioritization engine.
    """

    features_df = create_sample_features()

    rice = RICEFramework(features_df)

    results = rice.prioritize_features()

    return results


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "feedback": "",
    "feedback_items": [],
    "themes": [],
    "opportunities": [],
    "analysis_complete": False,
    "prioritization_complete": False,
    "experiment_complete": False,
    "selected_feature": "Smart Reorder",
    "rice_results": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="brand">Prioriti<span>Q</span></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="height: 1.5rem;"></div>',
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    '<div class="eyebrow">AI PRODUCT DECISION COPILOT</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-title">
        Turn customer feedback into<br>
        better product decisions.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-subtitle">
        PrioritiQ transforms unstructured customer feedback into
        product opportunities, evidence-backed prioritization,
        experiment recommendations and actionable PRDs.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Portfolio prototype • Synthetic data • Human-in-the-loop"
)


# ============================================================
# HOW IT WORKS
# ============================================================

st.markdown("## How it works")

cols = st.columns(5)

steps = [
    ("01", "Research", "Find recurring customer problems."),
    ("02", "Analyze", "Turn problems into opportunities."),
    ("03", "Prioritize", "Rank what should be built next."),
    ("04", "Validate", "Simulate the experiment."),
    ("05", "Document", "Generate an actionable PRD."),
]

for col, (number, title, description) in zip(cols, steps):
    with col:
        st.markdown(
            f"""
            <div class="card">
                <div class="step">{number}</div>
                <div class="agent-name">{title}</div>
                <div class="small-muted">
                    {description}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# INPUT
# ============================================================

st.markdown("## 1. Bring your customer feedback")

st.markdown(
    """
    <div class="small-muted">
        Paste customer feedback, reviews, interview notes or support
        tickets. One statement per line works best.
    </div>
    """,
    unsafe_allow_html=True,
)

feedback = st.text_area(
    "Customer feedback",
    value=st.session_state.feedback,
    height=220,
    placeholder="""I wish I could reorder my previous order.
Checkout takes too many steps.
I want to schedule my order for later.
I order the same food every week.
I don't want to search for the same restaurant again.""",
    label_visibility="collapsed",
)

if st.button(
    "Analyze Feedback →",
    type="primary",
    use_container_width=False,
):

    items = clean_feedback(feedback)

    if not items:
        st.warning("Please enter at least one customer statement.")
    else:

        st.session_state.feedback = feedback
        st.session_state.feedback_items = items

        with st.spinner(
            "Research Agent is analyzing customer feedback..."
        ):
            themes = demo_themes(items)
            opportunities = generate_demo_opportunities(themes)

        st.session_state.themes = themes
        st.session_state.opportunities = opportunities
        st.session_state.analysis_complete = True
        st.session_state.prioritization_complete = False
        st.session_state.experiment_complete = False

        st.success(
            f"Analyzed {len(items)} customer statements."
        )


# ============================================================
# RESEARCH RESULTS
# ============================================================

if st.session_state.analysis_complete:

    st.divider()

    st.markdown("## 2. Research Agent")

    st.markdown(
        """
        <div class="soft-card">
            <div class="agent-name">
                Customer Research Agent
            </div>
            <div class="small-muted">
                Identifying recurring themes and customer problems
                from unstructured feedback.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    theme_cols = st.columns(
        min(3, len(st.session_state.themes))
    )

    for col, theme in zip(
        theme_cols,
        st.session_state.themes,
    ):
        with col:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="metric-label">Theme</div>
                    <div class="feature-name">
                        {theme["theme"]}
                    </div>
                    <div class="small-muted">
                        {theme["description"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# OPPORTUNITIES
# ============================================================

if st.session_state.analysis_complete:

    st.markdown("## 3. Product opportunities")

    opp_df = pd.DataFrame(
        st.session_state.opportunities
    )

    if not opp_df.empty:
        st.dataframe(
            opp_df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown(
        """
        <div class="small-muted">
            These opportunities are generated from the diagnostic
            workflow. In the next iteration, this step can be
            connected to an LLM-powered Product Analyst Agent.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RICE PRIORITIZATION
# ============================================================

if st.session_state.analysis_complete:

    st.divider()

    st.markdown("## 4. Prioritization")

    st.markdown(
        """
        <div class="soft-card">
            <div class="agent-name">
                Prioritization Engine
            </div>
            <div class="small-muted">
                The product evaluates candidate features using the
                RICE framework: Reach × Impact × Confidence ÷ Effort.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Run Prioritization →",
        type="primary",
    ):

        with st.spinner(
            "Running RICE prioritization engine..."
        ):

            rice_results = run_rice_engine()

        st.session_state.rice_results = rice_results
        st.session_state.prioritization_complete = True

    if st.session_state.prioritization_complete:

        rice_results = st.session_state.rice_results

        display_columns = [
            "rank",
            "feature_name",
            "rice_score",
            "impact_level",
            "confidence_level",
            "effort_months",
        ]

        available_columns = [
            column
            for column in display_columns
            if column in rice_results.columns
        ]

        display_df = rice_results[
            available_columns
        ].copy()

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        top_feature = rice_results.iloc[0]

        st.session_state.selected_feature = (
            top_feature["feature_name"]
        )

        recommended_feature_html = f"""
<div class="card">
    <div class="metric-label">
        Recommended next feature
    </div>

    <div class="metric-value">
        {top_feature["feature_name"]}
    </div>

    <div class="small-muted">
        RICE Score:
        <strong>{top_feature["rice_score"]:,.0f}</strong>
        &nbsp; • &nbsp;

        Reach:
        {top_feature["reach_percentage"]:.0f}%
        &nbsp; • &nbsp;

        Impact:
        {top_feature["impact_level"]}
        &nbsp; • &nbsp;

        Effort:
        {top_feature["effort_months"]}
        person-months
    </div>
</div>
"""

st.markdown(
    textwrap.dedent(recommended_feature_html),
    unsafe_allow_html=True,
)


# ============================================================
# EXPERIMENT
# ============================================================

if st.session_state.analysis_complete:

    st.divider()

    st.markdown("## 5. Validate the recommendation")

    st.markdown(
        """
        <div class="soft-card">
            <div class="agent-name">
                Experiment Agent
            </div>
            <div class="small-muted">
                Design and inspect an A/B test for the selected
                product opportunity.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected = st.session_state.selected_feature

    st.markdown(
        f"### Recommended experiment: **{selected}**"
    )

    hypothesis = generate_hypothesis(
    st.session_state.selected_feature
)
    st.markdown("**Hypothesis**")
    st.info(hypothesis)

    experiment = get_existing_experiment()

    if st.button(
        "Run Experiment Simulation →",
        type="primary",
    ):

        st.session_state.experiment_complete = True

    if st.session_state.experiment_complete:

        st.warning(
            "Synthetic simulation — these are not production "
            "user results."
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Control",
                f'{experiment["control"]:.2f}%',
            )

        with c2:
            st.metric(
                "Treatment",
                f'{experiment["treatment"]:.2f}%',
            )

        with c3:
            st.metric(
                "Relative Lift",
                f'+{experiment["lift"]:.1f}%',
            )

        with c4:
            st.metric(
                "P-value",
                f'{experiment["p_value"]:.5f}',
            )

        if experiment["p_value"] < 0.05:

            st.success(
                "Statistically significant in the synthetic simulation."
            )

        else:

            st.info(
                "Not statistically significant in the simulation."
            )


# ============================================================
# PM DECISION
# ============================================================

if st.session_state.experiment_complete:

    st.divider()

    st.markdown("## 6. PM Decision")

    pm_decision_html = f"""
<div class="card">
    <div class="metric-label">
        Recommended decision
    </div>

    <div class="metric-value">
        Build {st.session_state.selected_feature}
    </div>

    <div class="small-muted">
        The recommendation combines prioritization evidence
        with the simulated experiment. The final product
        decision remains human-owned.
    </div>
</div>
"""

st.markdown(
    textwrap.dedent(pm_decision_html),
    unsafe_allow_html=True,
)


# ============================================================
# PRD
# ============================================================

if st.session_state.experiment_complete:

    st.divider()

    st.markdown("## 7. Product Requirements")

    selected_feature = st.session_state.selected_feature

    st.markdown(
        """
        <div class="soft-card">
            <div class="agent-name">
                PM Documentation Agent
            </div>

            <div class="small-muted">
                Converting the product decision into an
                actionable Product Requirements Document.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    experiment = get_existing_experiment()

    hypothesis = generate_hypothesis(
        selected_feature
    )

    # First try to load an existing PRD.
    existing_prd = load_prd(
        selected_feature
    )

    # If no existing PRD exists, generate one.
    if existing_prd:

        st.success(
            f"Existing PRD found for {selected_feature}."
        )

        with st.expander(
            "View Product Requirements Document",
            expanded=True,
        ):
            st.markdown(existing_prd)

    else:

        st.info(
            f"No existing PRD was found for "
            f"**{selected_feature}**. "
            f"The MVP documentation workflow generated "
            f"a draft PRD instead."
        )

        generated_prd = generate_prd(
            selected_feature,
            hypothesis,
            experiment,
        )

        with st.expander(
            "View Generated PRD",
            expanded=True,
        ):
            st.markdown(generated_prd)

        st.download_button(
            label="Download PRD",
            data=generated_prd,
            file_name=(
                selected_feature
                .lower()
                .replace(" ", "_")
                + "_prd.md"
            ),
            mime="text/markdown",
        )


# ============================================================
# ARCHITECTURE
# ============================================================

st.divider()

st.markdown("## The one-person product organization")

st.markdown(
    """
    <div class="card">

    <div style="text-align:center;">

    <div class="agent-name">
        AYUSH — Founder / Product Manager
    </div>

    <div class="small-muted">
        Product strategy • Customer understanding •
        Trade-offs • Final decisions
    </div>

    <div style="font-size:2rem; margin:1rem;">
        ↓
    </div>

    <div class="agent-name">
        AI Product Workflow
    </div>

    <div style="margin-top:1rem;">

    Research Agent
    &nbsp; → &nbsp;
    Product Analyst
    &nbsp; → &nbsp;
    Prioritization
    &nbsp; → &nbsp;
    Experiment
    &nbsp; → &nbsp;
    PRD

    </div>

    <div style="font-size:2rem; margin:1rem;">
        ↓
    </div>

    <div class="agent-name">
        Deterministic Product Analytics Engine
    </div>

    <div class="small-muted">
        RICE scoring • A/B simulation • Statistical analysis
    </div>

    </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()

st.caption(
    """
    Portfolio prototype. The current demonstration uses the project's
    existing analytical engine and synthetic data. AI-agent steps are
    represented as modular product workflows; connect them to an LLM
    API when moving from prototype to AI-enabled production.
    """
)

st.markdown(
    '<div class="footer">PrioritiQ · AI Product Decision Copilot · Built by Ayush Saxena</div>',
    unsafe_allow_html=True,
)