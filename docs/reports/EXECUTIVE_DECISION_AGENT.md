# InsightAI Executive Decision Agent

Date: 2026-06-27

## Summary

The Executive Decision Agent converts analytical results into business-ready decision support. It runs after Insight Generation and before anomaly/root-cause analysis so executive context is available to later agents and the final explanation.

## Responsibilities

- Executive summary
- Business risks
- Growth opportunities
- Department performance
- Financial impact
- Customer trends
- Operational issues
- Strategic recommendations
- Priority actions
- Confidence score
- Action plan

## Output Shape

```json
{
  "executive_summary": "Revenue trend is positive, but inventory and regional concentration require attention.",
  "business_risks": ["regional dependency", "low inventory exposure"],
  "growth_opportunities": ["expand high-performing regions", "target high-value customers"],
  "department_performance": {
    "sales": "improving",
    "operations": "watch inventory"
  },
  "financial_impact": "medium",
  "customer_trends": ["repeat customers drive revenue"],
  "operational_issues": ["restock low inventory products"],
  "strategic_recommendations": ["prioritize revenue retention and replenishment"],
  "priority_actions": ["review top accounts", "monitor revenue drop causes"],
  "confidence_score": 0.88,
  "action_plan": ["confirm metric definition", "share dashboard", "schedule report"]
}
```

## LangGraph Placement

Current flow:

1. Insight Generation Agent
2. Executive Decision Agent
3. Anomaly Detection Agent
4. Root Cause Analysis Agent, when needed
5. Forecasting and Visualization Agents

## Monitoring

The Admin Agent Monitoring Dashboard shows executive decision confidence from persisted workflow traces. The raw output is stored in `agent_traces.agent_outputs.executive_decision`.

## Limitations

The local deterministic mode creates consistent executive summaries without OpenAI. With `OPENAI_API_KEY` configured, the agent can be expanded to use live LLM reasoning while preserving the same output contract and safety checks.
