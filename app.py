"""
Seed Screen: a four pillar seed stage screening engine.

Built on the House of AI framework (Bapna and Ghose, THRIVE, 2024):
descriptive, predictive, causal, prescriptive.

Run: streamlit run app.py
Requires ANTHROPIC_API_KEY in the environment or a .env file.
"""

import json
import streamlit as st
from dotenv import load_dotenv

from engine import screen, DEFAULT_THESIS, DEFAULT_WEIGHTS
from demo_company import HARBORLINE

load_dotenv()

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

    tab1, tab2, tab3, tab4 = st.tabs(
        ["1. Descriptive", "2. Predictive", "3. Causal audit", "4. Prescriptive"]
    )

    with tab1:
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
        rows = [
            {
                "dimension": dim,
                "score /10": v["score"],
                "weight": v["weight"],
                "contribution": v["contribution"],
            }
            for dim, v in p.get("contributions", {}).items()
        ]
        st.dataframe(rows, use_container_width=True)

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
