from dotenv import load_dotenv
import voyageai # Embedduding model provider
import chunking # Custom chunking module for splitting text into chunks
import chromadb # Vector database for storing embeddings and performing similarity search
import bm25s # BM25 search for retrieving relevant chunks based on query text

def generate_embedding(chunks, client,model="voyage-3-large", input_type="query"):
    is_list = isinstance(chunks, list)
    input = chunks if is_list else [chunks]
    result = client.embed(input, model=model, input_type=input_type)
    return result.embeddings if is_list else result.embeddings[0]

if __name__ == "__main__":

    load_dotenv()

    # Initialize clients for embedding generation and vector database
    voyageClient = voyageai.Client()

    # Set up ChromaDB client and collection for storing embeddings
    chromaClient = chromadb.PersistentClient(path="./my_local_chroma_db")
    collection = chromaClient.get_or_create_collection(name="custom_embeddings_collection")

    # Read the input text from a file
    with open("./report.md", "r") as f:
        text = f.read()

    # Split the text into manageable chunks for embedding
    chunks = chunking.chunk_by_section(text)

    # Generate embeddings for each chunk and add them to the collection
    embeddings = generate_embedding(chunks, voyageClient)
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=[str(i) for i in range(len(chunks))]
    )

    # Tokenize the chunks for BM25 search
    corpus_tokens = bm25s.tokenize(chunks, stopwords="english")

    # Initialize BM25 retriever with the corpus of chunks
    retriever = bm25s.BM25(corpus=chunks)
    retriever.index(corpus_tokens)

    query = "Tell me about INC-2023-Q4-011"

    # Generate embedding for the query
    query_embedding = generate_embedding(query, voyageClient)

    # Perform a similarity search in the collection
    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=2
    )
    # For each id, print the first 200 characters of the document and the distance
    print("Results from vector similarity search:")
    for i, doc_id in enumerate(results['ids'][0]):
        print(f"Document ID: {doc_id}")
        print(f"Content: {results['documents'][0][i][:200]}...")
        print(f"Distance: {results['distances'][0][i]}")

    # Perform BM25 search to retrieve relevant chunks based on query text
    query_tokens = bm25s.tokenize(query)
    results, scores = retriever.retrieve(query_tokens, k=2)

    print("\nResults from BM25 search:")
    for doc, score in zip(results[0], scores[0]):
        print(f"Content: {doc[:200]}...")
        print(f"Score: {score:.4f} ")
