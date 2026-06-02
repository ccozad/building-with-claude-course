from dotenv import load_dotenv
import voyageai
import chunking
import chromadb

def generate_embedding(chunks, client,model="voyage-3-large", input_type="query"):
    is_list = isinstance(chunks, list)
    input = chunks if is_list else [chunks]
    result = client.embed(input, model=model, input_type=input_type)
    return result.embeddings if is_list else result.embeddings[0]

if __name__ == "__main__":

    load_dotenv()

    voyageClient = voyageai.Client()

    chromaClient = chromadb.PersistentClient(path="./my_local_chroma_db")
    collection = chromaClient.get_or_create_collection(name="custom_embeddings_collection")

    with open("./report.md", "r") as f:
        text = f.read()

    chunks = chunking.chunk_by_section(text)

    embeddings = generate_embedding(chunks, voyageClient)
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=[str(i) for i in range(len(chunks))]
    )

    query_embedding = generate_embedding("What did the software engineering team accomplish last year?", voyageClient)

    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=2
    )
    # For each id, print the first 200 characters of the document and the distance
    for i, doc_id in enumerate(results['ids'][0]):
        print(f"Document ID: {doc_id}")
        print(f"Content: {results['documents'][0][i][:200]}...")
        print(f"Distance: {results['distances'][0][i]}")
