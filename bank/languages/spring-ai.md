# Spring AI

## Q: What does Spring AI give you, and how would you call an LLM from a Spring Boot service?
### Solution
Spring AI is a portable abstraction over model providers (OpenAI, Anthropic, Bedrock, Ollama, …). Its main pieces:
- `ChatClient`: fluent API for prompts, system messages, and streaming.
- **Structured output**: maps the model's response to a Java record/bean.
- `EmbeddingModel` + `VectorStore` (PGVector, Redis, OpenSearch, …) for RAG.
- **Tool/function calling**: expose Spring beans as tools the model can invoke.
- **Advisors**: interceptors for chat memory, RAG retrieval, logging.

```java
record Answer(String summary, List<String> risks) {}

Answer a = chatClient.prompt()
    .system("You are a compliance analyst.")
    .user(u -> u.text("Assess: {txn}").param("txn", txnJson))
    .call()
    .entity(Answer.class);
```
Swap the provider (e.g. Bedrock) by changing the starter and properties, not the code.

## Q: How would you build a RAG feature with Spring AI, and what goes wrong in production?
### Solution
**Ingest:** a `DocumentReader` (PDF/Tika) feeds a `TokenTextSplitter` (chunking with overlap), which feeds the `EmbeddingModel`, which writes to the `VectorStore` with metadata (source, date, ACL).
**Query:** a `QuestionAnswerAdvisor` (or `RetrievalAugmentationAdvisor`) does a similarity search (top-k + metadata filter) and puts the retrieved chunks in the prompt.

Production issues:
- **Chunking quality** dominates answer quality. Tune the size and overlap; keep headings with their chunks.
- **Access control:** filter by user entitlements in the metadata filter, not after generation.
- **Staleness:** re-index pipelines plus deletes when the source changes.
- **Evaluation:** a golden question set; measure retrieval hit rate separately from answer quality.
- **Cost/latency:** cache embeddings, cap context size, stream responses.
- **Hallucination:** tell the model to answer only from the context and cite sources, with a fallback of "I don't know".
