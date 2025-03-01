import time
import chromadb

from src.utils import BaseAgent, retry_on_exception, logger


class EmbeddingAgent(BaseAgent):
    @retry_on_exception(attempts=3)
    def generate(self, text):
        result = self.client.models.embed_content(
            model="text-embedding-004",
            contents=[text]
        )
        return result.embeddings[0].values


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=":memory:")
        self.collection = self.client.get_or_create_collection(name="vector_store")
        self.embedding_agent = EmbeddingAgent()

    def store(self, descriptions_df):

        for i, data in enumerate(descriptions_df.iterrows()):
            if i % 30 == 0:
                logger.debug("Generating vector store: {} / {}".format(i, len(descriptions_df)))

            index, row = data
            time.sleep(1)
            description = row["description"]
            embedding = self.embedding_agent.generate(description)
            self.upload_single_record(index, embedding, description, row["video_path"])

    def upload_single_record(self, index, embedding, text, path):
        """Add an embedding with associated metadata."""
        index = str(index)
        self.collection.add(
            ids=[index],
            embeddings=[embedding],
            metadatas=[{"text": text, "path": path}]
        )

    def query(self, query, k=5):
        """Retrieve top-k nearest neighbors along with their metadata."""
        query_embedding = self.embedding_agent.generate(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        return results
