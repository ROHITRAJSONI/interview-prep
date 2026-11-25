# AWS Bedrock

## Q: Why would an enterprise use Bedrock instead of calling a model provider's API directly?
### Solution
- **Data governance:** prompts and outputs stay inside AWS, aren't used to train the models, and can go over **VPC endpoints (PrivateLink)**. Access is controlled with IAM and audited in CloudTrail.
- **One API, many models** (Anthropic Claude, Amazon Nova/Titan, Llama, Mistral…) via `InvokeModel` / the model-agnostic **Converse API**.
- Managed building blocks: **Knowledge Bases** (managed RAG), **Agents**, **Guardrails** (PII redaction, denied topics, content filters), model evaluation, and **provisioned throughput** for guaranteed capacity.

In a bank, the first point is usually the deciding factor: compliance has already approved AWS as a data processor.

## Q: How would you call Bedrock from a Java service robustly?
### Solution
Use the AWS SDK v2 `BedrockRuntimeClient` with the **Converse API** (`converse` / `converseStream`), so swapping models only changes the model ID. Credentials come from the task/Lambda role.

Robustness:
- Handle `ThrottlingException` with exponential backoff and jitter. Request quota increases or use cross-region inference profiles for capacity.
- Set timeouts, and stream long responses to the client.
- Cap `maxTokens`, and log token usage for cost tracking.
- Apply **Guardrails** to both inputs and outputs.
- Put the model ID and prompt version in config, so you can roll back without redeploying.
