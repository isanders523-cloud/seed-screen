# Seed Screen

A four pillar seed stage screening engine that treats the qualitative variables of venture screening as statistical variables, and separates correlation from causation in the score it produces.

## Thesis

Roughly half of early stage VCs describe their investment decisions as intuitive and qualitative (Gompers, Gornall, Kaplan, and Strebulaev, Journal of Financial Economics, 2020). The variables behind those decisions, which include founder market fit, team completeness, market timing, product wedge, distribution advantage, and traction, are treated as gut calls when each is measurable and each has a correlational or causal relationship with the outcome that matters at seed, which is reaching Series A.

The commercial AI screening tools that exist today stop at prediction, meaning correlational pattern matching over startup databases. This engine adds the layer those tools skip: a causal audit that classifies every driver of the score as causal, correlational, or confounded, with the reasoning and literature stated, so the user knows what the score is actually made of before acting on it.

Sector is a variable inside the model, not a filter on it. The default thesis is sector agnostic.

## Architecture

The engine follows the House of AI framework (Bapna and Ghose, THRIVE, MIT Press, 2024): four pillars on a data engineering foundation.

1. **Descriptive.** Feature engineering on qualitative inputs. Founder bios, market notes, and product descriptions become seven named dimensions, each scored 0 to 10 with evidence and gaps stated. Nothing is scored that is not evidenced in the input.

2. **Predictive.** A weighted screening score over the engineered features. Default weights are grounded in the Gompers et al. (2020) survey of 885 institutional VCs, in which the team was named an important factor by 95 percent of firms and the single most important factor by 47 percent. The score is labeled a structured prior rather than a trained probability, since v1 has no outcome data behind it.

3. **Causal audit.** For each material driver of the score, the engine classifies the relationship to the outcome as causal, correlational, or confounded, citing the relevant literature: Sorensen (2007) on selection versus treatment in VC outcomes, Gompers, Kovner, Lerner, and Scharfstein (2010) on serial founder success, and the treatment versus selection literature (Colombo and Grilli). The audit reports a score composition, meaning what fraction of the weighted score rests on causal mechanisms versus correlational or confounded signals.

4. **Prescriptive.** A decision against the fund's stated thesis: pass, monitor, meet, or diligence, with the decision discipline that a high score resting on confounded signals is a meet at best, and that every recommendation names the evidence that would change it.

## Honest scope

The causal pillar in v1 is a literature grounded audit, which is reasoning over identified mechanisms, not econometric estimation. True causal identification (Heckman corrections, instrumental variables, panel methods) requires outcome data across many companies and is scoped for v2. The v1 engine is honest about this boundary in its own output.

## Run

```
pip install -r requirements.txt
cp .env.example .env   # add your Anthropic API key
streamlit run app.py
```

Demo run on a fictional company:

```
python demo_company.py
```

The engine was calibrated against a real, private company that is not included in this repository.

## Literature

- Bapna, R. and Ghose, A. (2024). THRIVE: Maximizing Well-Being in the Age of AI. MIT Press. The House of AI framework.
- Gompers, P., Gornall, W., Kaplan, S., Strebulaev, I. (2020). How Do Venture Capitalists Make Decisions? Journal of Financial Economics 135(1).
- Sorensen, M. (2007). How Smart Is Smart Money? A Two Sided Matching Model of Venture Capital. Journal of Finance 62(6).
- Gompers, P., Kovner, A., Lerner, J., Scharfstein, D. (2010). Performance Persistence in Entrepreneurship. Journal of Financial Economics 96(1).
