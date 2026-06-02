from dotenv import load_dotenv
import voyageai
import chunking

def generate_embedding(text, model="voyage-3-large", input_type="query"):
    result = client.embed([text], model=model, input_type=input_type)

    return result.embeddings[0]

if __name__ == "__main__":

    load_dotenv()

    client = voyageai.Client()

    with open("./report.md", "r") as f:
        text = f.read()

    chunks = chunking.chunk_by_section(text)

    embedding = generate_embedding(chunks[0])
    print("Embedding for first chunk:")
    print(embedding)