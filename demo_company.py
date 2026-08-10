"""
Demo run: Harborline, a fictional seed stage company.

Every detail below is invented. The company, founders, numbers, and
investors do not exist. The file exists so the engine can be demonstrated
publicly without touching any real company's information.

Run: python demo_company.py
Requires ANTHROPIC_API_KEY in the environment or a .env file.
"""

import json
from engine import screen

HARBORLINE = {
    "name": "Harborline",
    "url": "",
    "one_liner": (
        "Software that automates berth scheduling and demurrage disputes "
        "for small and mid size ports, sold to terminal operators."
    ),
    "founder_bios": (
        "Dana Okafor (CEO): eight years in terminal operations at a mid "
        "Atlantic port authority, most recently operations manager for a "
        "container terminal; built the port's internal berth scheduling "
        "spreadsheet that the product replaces. First time founder. "
        "Priya Raman (CTO): staff engineer at a logistics SaaS company for "
        "five years, before that two years at a freight visibility "
        "startup that was acquired; has shipped scheduling and optimization "
        "systems in production. Second startup, first as a founder. "
        "No third cofounder; a founding sales hire is planned post raise."
    ),
    "market_description": (
        "Roughly 300 small and mid size ports in North America, most "
        "running berth scheduling on spreadsheets and email. Demurrage and "
        "detention fees are a persistent, quantifiable pain that port "
        "customers dispute manually. Large ports are served by heavyweight "
        "terminal operating systems that are overkill and overpriced for "
        "this segment. No regulatory catalyst; the tailwind is labor "
        "shortage and fee pressure rather than policy."
    ),
    "product_description": (
        "A scheduling engine that assigns berth windows against vessel "
        "ETAs and tide constraints, plus a dispute module that assembles "
        "demurrage evidence packets automatically from AIS data and "
        "terminal logs. Sold as SaaS at a per berth annual price. The "
        "scheduling optimization is standard constraint programming; the "
        "defensibility claim rests on the dispute evidence workflow and "
        "the terminal log integrations, which are tedious to replicate."
    ),
    "traction_notes": (
        "Two paid pilots live at regional ports, each $18,000 annual "
        "contracts signed after 60 day trials. One LOI from a third port "
        "pending budget cycle. Approximately 40 percent of one pilot "
        "port's demurrage disputes now assembled through the tool. Founders "
        "report a 9 port waitlist gathered at an industry conference, "
        "unverified. Angel round of $250,000 closed last year from two "
        "logistics operators."
    ),
    "round_details": (
        "Raising $1.5M seed on a $9M post money SAFE. No lead committed. "
        "Use of proceeds: founding sales hire, two engineers, 18 months "
        "runway."
    ),
}


if __name__ == "__main__":
    result = screen(HARBORLINE)
    print(json.dumps(result, indent=2))
