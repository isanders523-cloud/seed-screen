"""
Seed Screen: four pillar screening engine.

Architecture follows the House of AI framework (Bapna and Ghose, THRIVE, 2024):
descriptive, predictive, causal, prescriptive, on a data engineering foundation.

Pillar weights in the predictive layer are grounded in Gompers, Gornall,
Kaplan, and Strebulaev, "How Do Venture Capitalists Make Decisions?"
(Journal of Financial Economics, 2020): survey of 885 institutional VCs.
Team named most important factor by 47 percent of firms; business model,
product, market, industry follow.

The causal pillar in v1 is a causal audit, not econometric estimation.
It classifies each score driver as causal, correlational, or confounded,
citing the relevant literature (Sorensen 2007 on selection effects,
Gompers et al. 2010 on serial founders, Colombo and Grilli on treatment
versus selection). True identification requires panel data and is v2.
"""

import os
import json
import anthropic

MODEL = "claude-sonnet-4-6"

# Feature weights, grounded in Gompers et al. (2020).
# Percent of firms naming each factor important, normalized.
# Team is deliberately the heaviest weight at seed.
DEFAULT_WEIGHTS = {
    "team": 0.35,           # 95% important, 47% most important
    "business_model": 0.15, # 83% important
    "product": 0.13,        # 74% important
    "market": 0.12,         # 68% important
    "timing": 0.10,         # stage literature, regulatory asymmetry
    "traction": 0.08,       # weak signals still count at seed
    "competition": 0.07,
    "deal_fit": 0.10,       # thesis and portfolio fit, prescriptive input
}

DEFAULT_THESIS = (
    "Seed stage, sector agnostic. Bias toward founders who combine technical "
    "depth in their domain with commercial fluency, in markets where "
    "regulatory or infrastructure tailwinds create timing asymmetry. "
    "Sector (energy, health, fintech, consumer, deep tech) is a variable, "
    "not a filter. Check size flexible. Outcome variable of interest: "
    "probability of reaching Series A within 24 to 36 months."
)


def load_prompt(name: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "prompts", name), "r") as f:
        return f.read()


def get_client() -> anthropic.Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Create a .env file or export the "
            "variable before running."
        )
    return anthropic.Anthropic(api_key=key)


def call_claude(system: str, user: str, max_tokens: int = 8192) -> str:
    client = get_client()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")


def parse_json_response(raw: str) -> dict:
    """Strip markdown fences if present and parse JSON."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def run_descriptive(company: dict) -> dict:
    """
    Pillar 1. Feature engineering on qualitative inputs.
    Turns founder bios, market description, and product description into
    named, scored variables. What is, stated plainly.
    """
    system = load_prompt("descriptive.txt")
    user = json.dumps(company, indent=2)
    raw = call_claude(system, user)
    return parse_json_response(raw)


def run_predictive(features: dict, weights: dict = None) -> dict:
    """
    Pillar 2. Weighted scoring of the engineered features.
    Weights default to the Gompers grounded scheme above.
    Output is a 0 to 100 score plus per dimension contributions,
    framed as a screening score, not a success probability, since
    v1 has no trained model behind it.
    """
    w = weights or DEFAULT_WEIGHTS
    dims = features.get("dimensions", {})
    contributions = {}
    total = 0.0
    weight_sum = 0.0
    for dim, weight in w.items():
        if dim == "deal_fit":
            continue  # scored in the prescriptive pillar against the thesis
        d = dims.get(dim)
        if d is None:
            continue
        score = float(d.get("score", 0))  # each dimension scored 0 to 10
        contributions[dim] = {
            "score": score,
            "weight": weight,
            "contribution": round(score * weight, 3),
        }
        total += score * weight
        weight_sum += weight
    screening_score = round((total / (10 * weight_sum)) * 100, 1) if weight_sum else 0.0
    return {
        "screening_score": screening_score,
        "contributions": contributions,
        "note": (
            "Weighted screening score, weights grounded in Gompers et al. "
            "(2020). This is a structured prior, not a trained probability. "
            "A trained model requires outcome data and is scoped for v2."
        ),
    }


def run_causal_audit(features: dict, predictive: dict) -> dict:
    """
    Pillar 3. The causal audit.
    For each driver of the score, classify the relationship to the outcome
    (reaching Series A) as causal, correlational, or confounded, with
    literature grounded reasoning. This is the pillar commercial screening
    tools skip, and the honest v1 version of causal inference: reasoning
    over identified mechanisms, not estimation.
    """
    system = load_prompt("causal.txt")
    user = json.dumps(
        {"features": features, "predictive": predictive}, indent=2
    )
    raw = call_claude(system, user)
    return parse_json_response(raw)


def run_prescriptive(
    features: dict, predictive: dict, causal: dict, thesis: str
) -> dict:
    """
    Pillar 4. Decision under the fund's constraints.
    Given the score, the causal decomposition, and the thesis, recommend
    pass, monitor, meet, or diligence, and state what evidence would
    change the recommendation.
    """
    system = load_prompt("prescriptive.txt")
    user = json.dumps(
        {
            "thesis": thesis,
            "features": features,
            "predictive": predictive,
            "causal_audit": causal,
        },
        indent=2,
    )
    raw = call_claude(system, user)
    return parse_json_response(raw)


def screen(company: dict, thesis: str = None, weights: dict = None) -> dict:
    """Run all four pillars in sequence and return the full memo object."""
    thesis = thesis or DEFAULT_THESIS
    features = run_descriptive(company)
    predictive = run_predictive(features, weights)
    causal = run_causal_audit(features, predictive)
    prescriptive = run_prescriptive(features, predictive, causal, thesis)
    return {
        "company": company.get("name", "Unnamed"),
        "descriptive": features,
        "predictive": predictive,
        "causal_audit": causal,
        "prescriptive": prescriptive,
    }
