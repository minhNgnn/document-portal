import sys

from pathlib import Path
from src.multi_doc_chat.data_ingestion import DocumentIngestor
from src.multi_doc_chat.retriever import ConversationalRAG


def test_document_ingestion_and_rag():
    try:
        test_files = [
            "/Users/pc/Developer/document-portal/data/multi_doc_chat/market_analysis_report.docx",
            "/Users/pc/Developer/document-portal/data/multi_doc_chat/NIPS-2017-attention-is-all-you-need-Paper.pdf",
            "/Users/pc/Developer/document-portal/data/multi_doc_chat/sample.pdf",
            "/Users/pc/Developer/document-portal/data/multi_doc_chat/state_of_the_union.txt",
        ]
        uploaded_files = []
        for file_path in test_files:
            if Path(file_path).exists():
                uploaded_files.append(open(file_path, "rb"))
            else:
                print(f"File not found: {file_path}")

        if not uploaded_files:
            print("No valid files uploaded.")
            sys.exit(1)

        # step 2
        ingestor = DocumentIngestor()
        retriever = ingestor.ingest_files(uploaded_files=uploaded_files)

        for uploaded_file in uploaded_files:
            uploaded_file.close()
        session_id = "test_multi_doc_session"
        rag = ConversationalRAG(session_id=session_id, retriever=retriever)

        # Test retrieval first
        print("Testing retrieval...")
        retrieved_docs = retriever.invoke("President Zelensky speech parliament")
        print(f"Retrieved {len(retrieved_docs)} documents:")
        for i, doc in enumerate(retrieved_docs):
            print(f"Doc {i + 1}: {doc.page_content[:200]}...")

        question = (
            "What did President Zelensky say in his speech to the European Parliament?"
        )

        # Debug the context passing
        print(f"\nTesting question: {question}")
        print("Debug: Testing context formatting...")

        # Test the retriever directly
        docs = retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        print(f"Context length: {len(context)}")
        print(f"Context preview: {context[:500]}...")

        answer = rag.invoke(question)
        print(f"Question: {question}")
        print(f"Answer: {answer}")

    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_document_ingestion_and_rag()
