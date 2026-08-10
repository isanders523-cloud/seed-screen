"""
Seed Screen: a four pillar seed stage screening engine.

Built on the House of AI framework (Bapna and Ghose, THRIVE, 2024):
descriptive, predictive, causal, prescriptive.

Run: streamlit run app.py
Requires ANTHROPIC_API_KEY in the environment or a .env file.
"""

import json
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv

from engine import screen, DEFAULT_THESIS, DEFAULT_WEIGHTS
from demo_company import HARBORLINE

load_dotenv()


# --- Result visualizations -------------------------------------------------
# Category styling pairs a distinct hue AND lightness with a pattern fill and
# an on-bar text label, so the segments stay distinguishable without color.
_COMPOSITION_SEGMENTS = (
    ("causal_share", "Causal", "#1a9850", "/"),
    ("correlational_share", "Correlational", "#fdae61", "."),
    ("confounded_share", "Confounded", "#d73027", "x"),
)

_DIMENSION_ORDER = (
    "team", "business_model", "product", "market",
    "timing", "traction", "competition",
)


def _composition_figure(comp):
    """Horizontal stacked bar of the causal-audit score composition."""
    fig = go.Figure()
    for key, label, color, pattern in _COMPOSITION_SEGMENTS:
        pct = float(comp.get(key, 0) or 0) * 100
        fig.add_bar(
            x=[pct],
            y=["composition"],
            orientation="h",
            name=label,
            marker=dict(
                color=color,
                line=dict(color="white", width=1.5),
                pattern=dict(shape=pattern, size=7, solidity=0.35),
            ),
            text=[f"{label} {pct:.0f}%"],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=13),
            hovertemplate=f"{label}: %{{x:.0f}}%<extra></extra>",
            cliponaxis=False,
        )
    fig.update_layout(
        barmode="stack",
        height=150,
        margin=dict(l=8, r=8, t=8, b=8),
        xaxis=dict(range=[0, 100], ticksuffix="%", title=None, fixedrange=True),
        yaxis=dict(showticklabels=False, fixedrange=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, x=0),
        showlegend=True,
    )
    return fig


def _dimension_radar(dimensions):
    """Radar of the seven dimension scores (0-10). Null scores are omitted."""
    labels, values = [], []
    for dim in _DIMENSION_ORDER:
        detail = dimensions.get(dim)
        if not detail:
            continue
        score = detail.get("score")
        if score is None:
            continue
        labels.append(dim.replace("_", " "))
        values.append(float(score))
    if not values:
        return None
    fig = go.Figure(
        go.Scatterpolar(
            r=values + [values[0]],       # close the polygon
            theta=labels + [labels[0]],
            fill="toself",
            mode="lines+markers",
            line=dict(color="#1f77b4", width=2),
            fillcolor="rgba(31,119,180,0.35)",
            hovertemplate="%{theta}: %{r:.0f}/10<extra></extra>",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 10], tickvals=[0, 2, 4, 6, 8, 10])),
        height=380,
        margin=dict(l=50, r=50, t=40, b=40),
        showlegend=False,
    )
    return fig


def _contribution_figure(contributions):
    """Horizontal bars of each dimension's weighted contribution, largest first."""
    # Ascending sort so the largest contribution lands at the TOP of the chart.
    items = sorted(contributions.items(), key=lambda kv: kv[1]["contribution"])
    labels = [dim.replace("_", " ") for dim, _ in items]
    values = [v["contribution"] for _, v in items]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color="#1f77b4"),
            text=[f"{v:.2f}" for v in values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=340,
        margin=dict(l=8, r=40, t=10, b=10),
        xaxis=dict(title="Weighted contribution"),
        yaxis=dict(title=None),
    )
    return fig


st.set_page_config(page_title="Seed Screen", page_icon="S", layout="wide")

st.title("Seed Screen")
st.caption(
    "A four pillar seed stage screening engine: descriptive, predictive, "
    "causal, prescriptive. Feature weights grounded in Gompers, Gornall, "
    "Kaplan, and Strebulaev (JFE 2020). The causal pillar is a literature "
    "grounded audit that classifies each score driver as causal, "
    "correlational, or confounded, which is the layer commercial screening "
    "tools skip."
)

with st.sidebar:
    st.header("Fund thesis")
    thesis = st.text_area(
        "The thesis the prescriptive pillar scores against",
        value=DEFAULT_THESIS,
        height=220,
    )
    st.header("Weights")
    st.caption(
        "Defaults grounded in Gompers et al. (2020). Adjust to your fund."
    )
    weights = {}
    for dim, w in DEFAULT_WEIGHTS.items():
        if dim == "deal_fit":
            continue
        weights[dim] = st.slider(dim, 0.0, 0.5, float(w), 0.01)

st.header("Company inputs")
st.caption(
    "Paste what you have. Founder bios matter most, since team is the "
    "heaviest weighted dimension at seed. The engine scores only what is "
    "evidenced and marks the rest as gaps."
)

# Input keys shared by the widgets below and the example loader.
_COMPANY_FIELDS = (
    "name", "url", "one_liner", "founder_bios", "market_description",
    "product_description", "traction_notes", "round_details",
)


def _load_example_company():
    """Pre-fill every input with the Harborline demo, editable before running."""
    for field in _COMPANY_FIELDS:
        st.session_state[field] = HARBORLINE[field]


st.button("Load example company", on_click=_load_example_company)

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Company name", key="name")
    url = st.text_input("URL (optional)", key="url")
    one_liner = st.text_input("One liner (what the company does)", key="one_liner")
    founder_bios = st.text_area(
        "Founder bios (paste LinkedIn About sections or your own notes)",
        height=180,
        key="founder_bios",
    )
with col2:
    market_description = st.text_area(
        "Market description", height=90, key="market_description"
    )
    product_description = st.text_area(
        "Product description", height=90, key="product_description"
    )
    traction_notes = st.text_area(
        "Traction notes (revenue, pilots, LOIs, waitlist, prior investors)",
        height=90,
        key="traction_notes",
    )
    round_details = st.text_input(
        "Round details (size, valuation, lead) (optional)",
        key="round_details",
    )

if st.button("Run screening", type="primary"):
    if not name or not founder_bios:
        st.error("Company name and founder bios are required.")
        st.stop()
    company = {
        "name": name,
        "url": url,
        "one_liner": one_liner,
        "founder_bios": founder_bios,
        "market_description": market_description,
        "product_description": product_description,
        "traction_notes": traction_notes,
        "round_details": round_details,
    }
    with st.spinner("Running four pillars..."):
        try:
            result = screen(company, thesis=thesis, weights=weights)
        except Exception as e:
            st.error(f"Screening failed: {e}")
            st.stop()

    d = result["descriptive"]
    p = result["predictive"]
    c = result["causal_audit"]
    r = result["prescriptive"]

    st.divider()
    top1, top2, top3 = st.columns(3)
    top1.metric("Screening score", f"{p['screening_score']}/100")
    top2.metric(
        "Thesis fit", f"{r.get('thesis_fit', {}).get('score', 'n/a')}/100"
    )
    top3.metric(
        "Recommendation", r.get("recommendation", "n/a").upper()
    )

    comp = c.get("score_composition", {})
    if comp:
        st.caption(
            f"Score composition: causal {comp.get('causal_share', 0):.0%}, "
            f"correlational {comp.get('correlational_share', 0):.0%}, "
            f"confounded {comp.get('confounded_share', 0):.0%}"
        )
        st.plotly_chart(
            _composition_figure(comp),
            use_container_width=True,
            key="composition_chart",
        )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["1. Descriptive", "2. Predictive", "3. Causal audit", "4. Prescriptive"]
    )

    with tab1:
        radar = _dimension_radar(d.get("dimensions", {}))
        if radar is not None:
            st.plotly_chart(
                radar, use_container_width=True, key="dimension_radar"
            )
        else:
            st.info("No dimensions were scored, so there is nothing to chart.")
        st.subheader(d.get("one_liner", ""))
        for dim, detail in d.get("dimensions", {}).items():
            score = detail.get("score")
            label = f"{dim}: {score}/10" if score is not None else f"{dim}: no evidence"
            with st.expander(label):
                st.write(detail.get("rationale", ""))
                if detail.get("evidence"):
                    st.write("Evidence: " + "; ".join(detail["evidence"]))
                if detail.get("gaps"):
                    st.write("Gaps: " + "; ".join(detail["gaps"]))
        if d.get("red_flags"):
            st.warning("Red flags: " + "; ".join(d["red_flags"]))
        if d.get("open_questions"):
            st.info("Open questions: " + "; ".join(d["open_questions"]))

    with tab2:
        st.metric("Screening score", f"{p['screening_score']}/100")
        st.caption(p.get("note", ""))
        contributions = p.get("contributions", {})
        if contributions:
            st.plotly_chart(
                _contribution_figure(contributions),
                use_container_width=True,
                key="contribution_chart",
            )
        else:
            st.info("No scored dimensions contributed to the score.")

    with tab3:
        st.caption(c.get("summary", ""))
        for audit in c.get("audits", []):
            cls = audit.get("classification", "")
            with st.expander(f"{audit.get('dimension', '')}: {cls}"):
                st.write("Mechanism: " + audit.get("mechanism", ""))
                st.write("Literature: " + audit.get("literature", ""))
                st.write(
                    "Diligence that would move it: "
                    + audit.get("diligence_that_would_move_it", "")
                )

    with tab4:
        st.subheader(r.get("recommendation", "").upper())
        st.write(r.get("reasoning", ""))
        if r.get("key_questions"):
            st.write("Key questions:")
            for q in r["key_questions"]:
                st.write("- " + q)
        if r.get("evidence_that_changes_this"):
            st.write("Evidence that changes this:")
            for e in r["evidence_that_changes_this"]:
                st.write("- " + e)
        st.success("Next step: " + r.get("suggested_next_step", ""))

    st.divider()
    st.download_button(
        "Download full memo (JSON)",
        data=json.dumps(result, indent=2),
        file_name=f"{name.lower().replace(' ', '-')}-screening.json",
        mime="application/json",
    )
