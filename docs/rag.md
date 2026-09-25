# RAG

The repository includes operational runbooks and a deterministic retriever interface.

The current implementation deliberately keeps the default local deployment dependency-light. The `RunbookRetriever` interface can be replaced by an embeddings + vector database implementation without changing the incident API.

For a production vector layer, use a managed or separately deployed vector store and store document metadata such as source, version, chunk ID and embedding model.
