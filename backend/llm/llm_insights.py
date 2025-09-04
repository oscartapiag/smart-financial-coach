# llm_insights.py
import json
from typing import Dict, Any
import openai
from openai import OpenAI
from jsonschema import validate, ValidationError
from llm_schema import INSIGHT_CARD_SCHEMA

SYSTEM = (
  "You are a concise personal finance analyst. "
  "Speak plainly, no emojis, no hedging. "
  "Only use the numeric data provided; do not invent values. "
  "Return valid JSON only."
  "Provide insights that lead to measurable changes in user spending or saving habits."
)

USER_TMPL = """\
Context:
- Time range: {time_range}
- Latest period cashflow: income=${income:.2f}, expenses=${expenses:.2f}, net=${net:.2f}
- Prior period net: ${prior_net:.2f}
- Category deltas (MoM): {category_deltas}
- Top merchants this month: {top_merchants}
- Subscription candidates: {subs_summary}
- Optional cash balance: {cash_balance}

Task:
Return 3–6 insights. Use exactly this JSON schema:

{schema}

Do not include any non-JSON text. Do not wrap in markdown fences.
"""

_client = OpenAI()

def _summarize(inputs: Dict[str, Any]) -> Dict[str, Any]:
    cat = sorted(inputs.get("category_deltas", []), key=lambda x: -abs(x.get("delta_amount",0)))[:6]
    merch = inputs.get("top_merchants", [])[:5]
    subs  = [
        {"merchant": str(s.get("merchant")), "score": float(s.get("score", 0)), "amount": s.get("amount_mean")}
        for s in inputs.get("subscriptions", [])[:6]
    ]
    return {
        "time_range": inputs.get("time_range","Last 30d"),
        "income": float(inputs.get("income",0)),
        "expenses": float(inputs.get("expenses",0)),
        "net": float(inputs.get("net",0)),
        "prior_net": float(inputs.get("prior_net",0)),
        "category_deltas": cat,
        "top_merchants": merch,
        "subs_summary": subs,
        "cash_balance": inputs.get("cash_balance"),
    }

def _validate_json(text: str) -> Dict[str, Any]:
    data = json.loads(text)
    validate(instance=data, schema=INSIGHT_CARD_SCHEMA)
    return data

def generate_llm_cards(inputs: Dict[str, Any]) -> Dict[str, Any]:
    compact = _summarize(inputs)
    prompt = USER_TMPL.format(**compact, schema=json.dumps(INSIGHT_CARD_SCHEMA, indent=2))

    # Use standard Chat Completions API with JSON mode
    try:
        chat = _client.chat.completions.create(
            model="gpt-4o-mini",  # Use standard, fast model
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )
        raw = chat.choices[0].message.content
        return _validate_json(raw)
    except Exception as e:
        print(f"LLM API error: {e}")
        return {"cards": []}
