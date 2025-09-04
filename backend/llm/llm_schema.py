INSIGHT_CARD_SCHEMA = {
  "type": "object",
  "properties": {
    "cards": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["kind","title","summary","period","metrics"],
        "properties": {
          "kind": { "type": "string", "enum": [
            "cashflow","category_trend","subscription","anomaly","merchant","runway","action"
          ]},
          "title":  { "type": "string", "maxLength": 120 },
          "summary":{ "type": "string", "maxLength": 280 },
          "impact": { "type": ["number","null"] },
          "period": { "type": "string", "maxLength": 40 },
          "metrics":{ "type": "object" },
          "cta":    { "type": ["object","null"] }
        }
      }
    }
  },
  "required": ["cards"],
  "additionalProperties": False
}
