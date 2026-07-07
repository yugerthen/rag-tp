from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL
from vectordb import VectorDB
from moderator import Moderator

class RAG:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.moderator = Moderator()
        self.vectordb = VectorDB()
        with open("prompt_rag.txt", "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def _build_prompt(self, chunks):
        chunks_text = "\n".join(
            f"[{i+1}] {doc} (source: {meta['source']})"
            for i, (doc, meta) in enumerate(zip(chunks["documents"][0], chunks["metadatas"][0]))
        )
        return self.prompt_template.replace("{{Chunks}}", chunks_text)

    def answer_question(self, question):
        moderation = self.moderator.moderate(question)
        if moderation.get("is_prompt_injection"):
            return "Je ne peux pas repondre a cette demande : elle a ete identifiee comme une tentative de detournement de mes instructions."

        chunks = self.vectordb.retrieve(question, n=3)
        system_prompt = self._build_prompt(chunks)

        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.1
            )
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'appel au LLM : {e}")

        return response.choices[0].message.content

if __name__ == "__main__":
    rag = RAG()
    reponse = rag.answer_question("Quelle est la couleur du chat de Bob ?")
    print(reponse)