#Step-1: Create at least 4 HR policy documents as Python dictionaries (similar to POLICY_DOCUMENTS in the session). Each document must have:

#A unique id
#A text field with 3–5 sentences of policy content
#A metadata field with category and source keys

# Import the List, Dict, and Any types for type hints — helps with code readability
from typing import List, Dict, Any

# Import chromadb — this is our vector database library
import chromadb

# Import the OpenAI client to use embeddings and text generation
from openai import OpenAI

# -----------------------------------------------------------------------
# Step 1: Initialize the OpenAI client
# Make sure OPENAI_API_KEY is set as an environment variable before running
# -----------------------------------------------------------------------
openai_client = OpenAI()

# -----------------------------------------------------------------------
# Step 2: Set the model names we will use throughout the code
# EMBEDDING_MODEL converts text into vectors (numerical representations)
# GENERATION_MODEL is the LLM that will generate the final answer
# -----------------------------------------------------------------------
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI embedding model
GENERATION_MODEL = "gpt-5.2"               # OpenAI LLM for text generation

# -----------------------------------------------------------------------
# Step 3: Define the sample e-commerce policy documents
# Each document has an id, the text content, and metadata (category + source)
# These five documents are our entire "knowledge base" for this demo
# -----------------------------------------------------------------------
POLICY_DOCUMENTS = [
    {
        "id": "1",                  
        "text": (
            "Employees are entitled to 24 days of annual leave per calendar year. "
            "Unused leave up to 10 days may be carried forward to the next year with manager approval. "
            "Sick leave can be availed for up to 12 days annually and may require a medical certificate for absences longer than two consecutive days. "
            "Leave requests should be submitted through the HR portal at least three working days in advance whenever possible."
        ),
        "metadata": {
            "category": "Leave Policy",
            "source": "HR Employee Handbook 2026"
        }
    },
    {
        "id": "2",
        "text": (
            "Employees are permitted to work from home up to three days per week based on project requirements and manager approval. "
            "Only employees who have completed their probation period are eligible for the hybrid work program. "
            "WFH requests must be submitted in the internal attendance system before the start of the workweek. "
            "Employees working remotely are expected to remain available during official working hours and attend all scheduled meetings online."
        ),
        "metadata": {
            "category": "Work From Home Policy",
            "source": "Flexible Work Guidelines 2026"
        }
    },
    {
        "id": "3",
        "text": (
            "The company conducts employee appraisals once every financial year during the month of March. "
            "Performance evaluations are based on a five-point rating scale ranging from Outstanding to Needs Improvement. "
            "Salary increments and bonus eligibility are linked to appraisal ratings and business performance. "
            "Managers are required to complete performance discussions with employees before final ratings are submitted to HR."
        ),
        "metadata": {
            "category": "Appraisal Policy",
            "source": "Performance Management Framework 2026"
        }
    },
    {
        "id": "POL004",
        "text": (
            "Employees are expected to maintain professional behavior and treat colleagues with respect in all workplace interactions. "
            "Sharing confidential company or customer information with unauthorized individuals is strictly prohibited. "
            "Employees must disclose any potential conflict of interest, including external business activities that may affect company operations. "
            "Violation of the code of conduct may result in disciplinary action, including termination of employment."
        ),
        "metadata": {
            "category": "Code of Conduct",
            "source": "Corporate Ethics and Compliance Manual"
        }
    }
]

# -----------------------------------------------------------------------
# Step 4: Function to create embeddings for a list of text strings
# Sends the texts to OpenAI and gets back a list of float vectors
# -----------------------------------------------------------------------
def create_embeddings(texts: List[str]) -> List[List[float]]:
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,   
        input=texts              
    )
    embeddings = [item.embedding for item in response.data]
    return embeddings


# -----------------------------------------------------------------------
# Step 5: Function to create and connect to the ChromaDB vector database
# PersistentClient saves data to disk so we don't lose data on restart
# -----------------------------------------------------------------------
def setup_vector_database():
    # Create a persistent ChromaDB client that stores data in "./chroma_policy_db" folder
    chroma_client = chromadb.PersistentClient(path="./hr_policy_rag")

    # Get an existing collection or create a new one if it does not exist
    # "cosine" distance means we measure similarity by angle, not raw distance
    collection = chroma_client.get_or_create_collection(
        name="hr_policy_collection",   
        metadata={"hnsw:space": "cosine"}     
    )

    # Return the collection object so other functions can use it
    return collection


# -----------------------------------------------------------------------
# Step 6: Function to index (store) all policy documents into ChromaDB
# We store the text, metadata, and embeddings together for each document
# -----------------------------------------------------------------------
def index_hr_documents(collection):
    # Extract the "id" field from each policy document into a list
    ids = [doc["id"] for doc in POLICY_DOCUMENTS]

    # Extract the "text" field from each policy document into a list
    texts = [doc["text"] for doc in POLICY_DOCUMENTS]

    # Extract the "metadata" field from each policy document into a list
    metadatas = [doc["metadata"] for doc in POLICY_DOCUMENTS]

    # Generate embeddings for all policy texts in one API call
    embeddings = create_embeddings(texts)

    # Store everything in ChromaDB using upsert
    # upsert = update if ID exists, insert if it does not — safe to run multiple times
    collection.upsert(
        ids=ids,               # Unique IDs for each chunk
        documents=texts,       # Raw text content of each chunk
        metadatas=metadatas,   # Category and source metadata
        embeddings=embeddings  # Vector representations of each chunk
    )

    # Print a confirmation message once all documents are stored
    print(f"Indexed {len(POLICY_DOCUMENTS)} policy documents successfully.")


# -----------------------------------------------------------------------
# Step 7: Retriever function — finds most relevant policy chunks
# Converts the user query to an embedding and searches ChromaDB
# -----------------------------------------------------------------------
def retrieve_hr_content(
    collection,
    query: str,
    top_k: int = 3    # top_k controls how many chunks to retrieve
) -> List[Dict[str, Any]]:

    # Convert the user query into an embedding vector using OpenAI
    query_embedding = create_embeddings([query])[0]  # [0] because we only sent one query

    # Search ChromaDB for the top_k most similar policy chunks
    results = collection.query(
        query_embeddings=[query_embedding],                      # Query vector
        n_results=top_k,                                         # Number of results to fetch
        include=["documents", "metadatas", "distances"]          # What to include in response
    )

    # Build a clean list of retrieved chunks with text, metadata, and distance
    retrieved_chunks = []
    documents = results["documents"][0]   # List of matching text strings
    metadatas = results["metadatas"][0]   # List of matching metadata dicts
    distances = results["distances"][0]   # List of similarity distances (lower = more similar)

    # Loop through results and combine them into one dictionary per chunk
    for document, metadata, distance in zip(documents, metadatas, distances):
        retrieved_chunks.append({
            "text": document,       # The policy text
            "metadata": metadata,   # Category and source info
            "distance": distance    # How close this chunk is to the query
        })

    # Return the list of retrieved chunks
    return retrieved_chunks


# -----------------------------------------------------------------------
# Step 8: Helper function to print retrieved chunks so we can inspect them
# This helps students see what the retriever found before the LLM answers
# -----------------------------------------------------------------------
def print_retrieved_chunks(query: str, chunks: List[Dict[str, Any]]):
    # Print a divider and the customer query
    print("\n" + "=" * 80)
    print(f"Customer Query: {query}")
    print("=" * 80)

    # Loop through each retrieved chunk and print its details
    for index, chunk in enumerate(chunks, start=1):
        print(f"\nResult {index}")
        print(f"Source   : {chunk['metadata']['source']}")    # Which policy document
        print(f"Category : {chunk['metadata']['category']}")  # Which category
        print(f"Distance : {chunk['distance']:.4f}")          # Similarity score (lower = closer)
        print(f"Content  : {chunk['text']}")                  # The actual policy text


# -----------------------------------------------------------------------
# Step 9: Prompt builder — injects retrieved policy chunks into the prompt
# This is the most important step in RAG: grounding the LLM with real data
# -----------------------------------------------------------------------
def build_grounded_prompt(query: str, chunks: List[Dict[str, Any]]) -> str:
    # Build the context string by combining all retrieved chunks
    context = ""
    for index, chunk in enumerate(chunks, start=1):
        source = chunk["metadata"]["source"]  # Get source name for the chunk
        text = chunk["text"]                  # Get the chunk text
        # Append each chunk with its source label
        context += f"\nPolicy Chunk {index} | Source: {source}\n{text}\n"

    # Build the full prompt with instructions, context, and the customer question
    prompt = f"""You are a helpful HR policy assistant for an e-commerce company.
Answer the customer's question using ONLY the policy context provided below.
Rules:
1. Do not make up policy details.
2. If the answer is not present in the context, say:
   "I do not have enough information in the provided policy documents."
3. Keep the answer simple, clear, and customer-friendly.
4. Mention important conditions or exceptions if they are present in the context.

Policy Context:
{context}

Customer Question:
{query}

Final Answer:"""

    # Return the fully assembled prompt
    return prompt


# -----------------------------------------------------------------------
# Step 10: Generator function — uses the LLM to answer based on context
# This is the "Generation" part of Retrieval-Augmented Generation
# -----------------------------------------------------------------------
def generate_answer_from_context(query: str, chunks: List[Dict[str, Any]]) -> str:
    # Build the grounded prompt by injecting retrieved policy chunks
    prompt = build_grounded_prompt(query, chunks)

    # Call the OpenAI LLM with the grounded prompt
    response = openai_client.responses.create(
        model=GENERATION_MODEL,    # Use the generation model we defined
        instructions=(
            "You are a precise and helpful HR policy assistant."  # System instruction
        ),
        input=prompt               # The grounded prompt with policy context
    )

    # Return the generated text from the LLM response
    return response.output_text

# -----------------------------------------------------------------------
# Step 11: Standalone LLM function — answers WITHOUT any retrieval
# This is for comparison: shows how the LLM answers from memory alone
# -----------------------------------------------------------------------
def generate_answer_without_retrieval(query: str) -> str:
    # Call the OpenAI LLM without any retrieved policy context
    response = openai_client.responses.create(
        model=GENERATION_MODEL,    # Same generation model
        instructions=(
            "You are a helpful e-commerce customer support assistant. "
            "Answer based on your general knowledge."  # No company policy given
        ),
        input=query                # Only the raw customer question — no context
    )

    # Return the generated text from the LLM
    return response.output_text



# -----------------------------------------------------------------------
# Step 12: Complete RAG pipeline — ties retrieval and generation together
# This is the main function students will call for production-style usage
# -----------------------------------------------------------------------
def answer_with_rag(collection, query: str, top_k: int = 3) -> str:
    # Step A: Retrieve the top_k most relevant policy chunks
    retrieved_chunks = retrieve_hr_content(
        collection=collection,   # The ChromaDB collection
        query=query,             # Customer's question
        top_k=top_k              # How many chunks to retrieve
    )

    # Step B: Print the retrieved chunks so we can inspect what was found
    print_retrieved_chunks(query, retrieved_chunks)

    # Step C: Generate the final grounded answer using retrieved context
    answer = generate_answer_from_context(query, retrieved_chunks)

    # Return the final answer
    return answer


# -----------------------------------------------------------------------
# Step 13: Top-K experiment — shows how retrieval depth affects answers
# Runs the same query with different top_k values so students can compare
# -----------------------------------------------------------------------
def top_k_experiment(collection, query: str):
    # Print a section header for the experiment
    print("\n" + "#" * 80)
    print("TOP-K EXPERIMENT")
    print("#" * 80)

    # Try top_k values of 1, 2, 3, and 5 one by one
    for top_k in [1, 2, 3, 5]:
        print(f"\n\n--- Answer with Top-K = {top_k} ---")

        # Retrieve chunks using the current top_k value
        chunks = retrieve_hr_content(
            collection=collection,   # ChromaDB collection
            query=query,             # The experiment query
            top_k=top_k              # Current depth we are testing
        )

        # Generate an answer using the retrieved chunks
        answer = generate_answer_from_context(query, chunks)

        # Print the generated answer for this top_k level
        print(answer)


# -----------------------------------------------------------------------
# Step 14: Main function — runs the full demo from start to finish
# -----------------------------------------------------------------------
def main():
    # Step A: Set up the ChromaDB vector database (creates or reuses the collection)
    collection = setup_vector_database()

    # Step B: Index all five policy documents into the vector database
    index_hr_documents(collection)

    # Step C: Define a sample customer query for the demo
    sample_query = "How many days of annual leave am I entitled to per year?"
                    #"Do I need manager approval before working from home?"
                    #"When is the appraisal cycle conducted and how is the increment decided?"
    
    # Step D: First, answer WITHOUT retrieval (LLM from memory only)
    print("\n\nWITHOUT RETRIEVAL:")
    print("-" * 80)
    answer_without_rag = generate_answer_without_retrieval(sample_query)
    print(answer_without_rag)


    # Step E: Now answer WITH RAG (retrieval + LLM)
    print("\n\nWITH RAG:")
    print("-" * 80)
    answer_with_retrieval = answer_with_rag(
        collection=collection,   # ChromaDB collection
        query=sample_query,      # Customer's question
        top_k=3                  # Retrieve top 3 most relevant chunks
    )
    print("\nFinal RAG Answer:")
    print(answer_with_retrieval)

    # Step F: Run the top-K experiment to show how depth affects answers
    top_k_experiment(
        collection=collection,
        query="Can I return an electronic item if it has liquid damage?"
    )


# Standard Python entry point — runs main() only when script is executed directly
if __name__ == "__main__":
    main()
