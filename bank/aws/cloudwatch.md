# AWS CloudWatch

## Q: How would you set up monitoring and alerting for a microservice on AWS?
### Solution
- **Metrics:** golden signals (latency p50/p99, error rate, traffic, saturation), from the ALB, ECS/Lambda and custom app metrics. Publish custom metrics cheaply with **Embedded Metric Format** (EMF) in your logs, or with Micrometer's CloudWatch registry.
- **Logs:** structured JSON plus a correlation ID; **Logs Insights** queries for investigations; metric filters to turn log patterns into metrics.
- **Tracing:** X-Ray / ADOT (OpenTelemetry) across services.
- **Alarms:** alert on symptoms (error rate, p99 latency, DLQ depth > 0, queue age), not on CPU alone. **Composite alarms** reduce noise. Route via SNS to PagerDuty/Slack.
- Dashboards per service, plus **Synthetics** canaries for critical user journeys.

## Q: Write a Logs Insights query to find the slowest endpoints in the last hour.
### Solution
```
fields @timestamp, path, latencyMs
| filter ispresent(latencyMs)
| stats count() as calls, avg(latencyMs) as avg, pct(latencyMs, 99) as p99 by path
| sort p99 desc
| limit 10
```
This assumes JSON logs. Insights automatically discovers JSON fields. For errors: `filter level = "ERROR" | stats count() by bin(5m), exception`. Mention cost too: Insights charges per GB scanned, so narrow the time range and log groups.
