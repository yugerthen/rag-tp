import os
import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
from config import EMBEDDING_MODEL, CHROMA_DB_PATH, CORPUS_CSV_PATH

class VectorDB:
    def __init__(self, collection_name="corpus"):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection_name = collection_name

        existing_collections = [c.name for c in self.client.list_collections()]

        if collection_name in existing_collections:
            self.collection = self.client.get_collection(collection_name)
            model_name = self.collection.metadata["embedding_model"]
            self.model = SentenceTransformer(model_name)
            print(f"Base rechargee avec le modele : {model_name}")
        elif os.path.exists(CORPUS_CSV_PATH):
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"embedding_model": EMBEDDING_MODEL}
            )
            self._index_corpus()
            print("Base creee et indexee")
        else:
            raise RuntimeError("Aucune base existante et aucun corpus disponible pour en creer une.")

    def _index_corpus(self):
        df = pd.read_csv(CORPUS_CSV_PATH)
        texts = df["text"].tolist()
        ids = df["id"].tolist()
        metadatas = df[["source", "categorie"]].to_dict(orient="records")

        embeddings = self.model.encode(
            texts,
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

    def retrieve(self, question, n=3):
        question_embedding = self.model.encode([question], normalize_embeddings=True)
        results = self.collection.query(
            query_embeddings=question_embedding.tolist(),
            n_results=n
        )
        return results

if __name__ == "__main__":
    db = VectorDB()
    resultats = db.retrieve("Quelle est la couleur du chat de Bob ?", n=3)
    for doc, meta in zip(resultats["documents"][0], resultats["metadatas"][0]):
        print(f"- {doc} (source: {meta['source']})")