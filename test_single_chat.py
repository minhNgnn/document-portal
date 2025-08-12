import sys
from pathlib import Path
from langchain_community.vectorstores import FAISS
from src.single_doc_chat.data_ingestion import SingleDocIngestor
from src.single_doc_chat.retriever import ConversationRAG
from utils.model_loader import ModelLoader

FAISS_INDEX_PATH = Path("faiss_index")


def test_conversation_rag(pdf_path: str, question: str):
    try:
        model_loader = ModelLoader(pdf_path)

        if FAISS_INDEX_PATH.exists():
            print("Loading FAISS index...")
            embeddings = model_loader.load_embeddings()
            vector_store = FAISS.load_local(
                FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
            )
            retriever = vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": 5}
            )
        else:
            # Ingest doc and create retriever
            print("FAISS index not found. Ingesting document...")
            with open(pdf_path, "rb") as f:
                uploaded_files = [f]
                ingestor = SingleDocIngestor()
                retriever = ingestor.ingest_files(uploaded_files)
        print("Running Conversational RAG...")
        session_id = "test_session"
        rag = ConversationRAG(retriever, session_id)

        response = rag.invoke(question)
        print(f"\nQuestion :{question} \nResponse: {response}")
    except Exception as e:
        print(f"Error during test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    pdf_path = "path/to/your/pdf"
    question = "What is the main topic of the document?"

    if not Path(pdf_path).exists():
        print(f"PDF file does not exist: {pdf_path}")
        sys.exit(1)

    test_conversation_rag(pdf_path, question)
