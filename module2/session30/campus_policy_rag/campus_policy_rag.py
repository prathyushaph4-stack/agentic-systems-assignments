import os
import re
import uuid
import chromadb
import numpy as np
from pypdf import PdfReader
import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel

# CONFIGURATION
# Insert your Gemini API Key here
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

genai.configure(api_key=GEMINI_API_KEY)  # type: ignore[attr-defined]

PDF_FOLDER = "policy_documents"
CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "campus_policies"

EMBEDDING_MODEL = "models/embedding-001"
LLM_MODEL = "gemini-1.5-flash"

CHUNK_SIZE = 150
CHUNK_OVERLAP = 20



# POLICY TYPE DETECTION
def infer_policy_type(filename):
    """
    Infer policy type from filename.
    """

    filename = filename.lower()

    if "hostel" in filename:
        return "hostel"

    elif "refund" in filename:
        return "refund"

    elif "library" in filename:
        return "library"

    else:
        return "general"



# CLEAN TEXT
def clean_text(text):
    """
    Remove extra spaces and newlines.
    """
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", ' ', text)
    return text.strip()


def make_document(text, metadata):
    """
    Creates a standard document dictionary for every page.
    Having a consistent structure makes it easy to handle thousands of documents.
    """
    return {
        "text": text,          
        "metadata": metadata   
    }


# LOAD PDF FILES
def load_pdfs(folder_path):
    """
    Load all PDFs from folder.
    """

    documents = []

    if os.path.isdir(folder_path):
        files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
        for file in files:
            full_path = os.path.join(folder_path, file)
            documents.extend(load_pdfs(full_path))
        return documents

    if not folder_path.lower().endswith(".pdf"):
        return documents

    file = os.path.basename(folder_path)
    reader = PdfReader(folder_path)
    policy_type = infer_policy_type(file)

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            cleaned = clean_text(text)
            documents.append({
                "text": cleaned,
                "source_file": file,
                "page_number": page_number + 1,
                "policy_type": policy_type
            })

    return documents


def load_all_documents(folder_path):
    """
    Loads ALL PDF files from a given folder automatically.
    You just point it to a folder — it finds every PDF and loads all pages.
    No need to call load_pdf_file manually for each file.
    """
    all_documents = []  
    
    
    for filename in os.listdir(folder_path):
        
        if filename.endswith(".pdf"):  
            
            file_path = os.path.join(folder_path, filename)  
            docs = load_pdfs(file_path)                 
            all_documents.extend(docs)  
            print(f"Loaded {len(docs)} pages from: {filename}")
    
    print(f"\nTotal documents loaded: {len(all_documents)}")
    return all_documents 

# CHUNKING
def split_into_chunks(text, chunk_size=150, overlap=20):
    """
    Split text into overlapping chunks.
    """

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk_words = words[start:end]

        chunk = " ".join(chunk_words)

        chunks.append(chunk)

        start += (chunk_size - overlap)

    return chunks



# EMBEDDINGS
def generate_embedding(text):
    """
    Generate embeddings using Gemini embedding model.
    """

    response = genai.embed_content(  # type: ignore[attr-defined]
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document"
    )

    return response["embedding"]



# CHROMADB SETUP
def build_vector_database(documents):
    """
    Create persistent ChromaDB collection.
    """

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    total_chunks = 0

    for doc in documents:

        chunks = split_into_chunks(
            doc["text"],
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP
        )

        for index, chunk in enumerate(chunks):

            embedding = generate_embedding(chunk)

            chunk_id = str(uuid.uuid4())

            metadata = {
                "source_file": doc["source_file"],
                "page_number": doc["page_number"],
                "policy_type": doc["policy_type"]
            }

            collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[metadata]
            )

            total_chunks += 1

    print(f"\nTotal chunks stored in ChromaDB: {total_chunks}")

    return collection



# RETRIEVAL
def retrieve_relevant_chunks(query, collection, top_k=3):
    """
    Retrieve top relevant chunks.
    """
    
    query_embedding = genai.embed_content(  # type: ignore[attr-defined]
        model=EMBEDDING_MODEL,
        content=query,
        task_type="retrieval_query"
    )["embedding"]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results



# PROMPT BUILDING
def build_prompt(query, retrieved_chunks):
    """
    Build final LLM prompt.
    """

    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
You are a campus policy assistant.

Answer ONLY using the provided policy context.

If the answer is not available in the context,
reply exactly with:
"I don't have that information."

Keep the answer simple, short, and student-friendly.

POLICY CONTEXT:
{context}

STUDENT QUESTION:
{query}

ANSWER:
"""

    return prompt



# GENERATE FINAL ANSWER
def generate_answer(prompt):
    """
    Generate response from Gemini LLM.
    """

    model = GenerativeModel(LLM_MODEL)
    response = model.generate_content(prompt)

    return response.text.strip()


# END-TO-END QUESTION ANSWERING
def answer_question(query, collection):
    """
    Full RAG pipeline.
    """

    results = retrieve_relevant_chunks(query, collection)

    retrieved_docs = []
    if results and "documents" in results and len(results["documents"]) > 0:
        retrieved_docs = results["documents"][0] or []

    prompt = build_prompt(query, retrieved_docs)

    answer = generate_answer(prompt)

    return answer





# MAIN
if __name__ == "__main__":

    print("\n===== CAMPUS POLICY RAG SYSTEM =====\n")

    # Load PDFs
    documents = load_pdfs(PDF_FOLDER)

    print(f"Loaded {len(documents)} document pages.")

    # Build vector database
    collection = build_vector_database(documents)

    # Test Queries
    test_queries = [

        "Can I get refund after dropping a course?",

        "What is the deadline for returning library books?",

        "Are hostel visitors allowed on weekends?",

        "Can I stay overnight with my hostel visitor?"
    ]

    print("\n===== STUDENT QUESTIONS =====\n")

    for query in test_queries:

        print(f"QUESTION: {query}")

        answer = answer_question(query, collection)

        print(f"ANSWER: {answer}")

        print("-" * 60)