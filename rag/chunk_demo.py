import chunking

if __name__ == "__main__":
    with open("./report.md", "r") as f:
        text = f.read()

    size_chunks = chunking.chunk_by_char(text)
    print("Size-based chunks:")
    print(f"Total chunks: {len(size_chunks)}")
    print("Example chunks:")
    for chunk in size_chunks[:3]:
        print(chunk)
        print("----")
    
    sentence_chunks = chunking.chunk_by_sentence(text)
    print("Sentence-based chunks:")
    print(f"Total chunks: {len(sentence_chunks)}")
    print("Example chunks:")
    for chunk in sentence_chunks[:3]:
        print(chunk)
        print("----")
    
    section_chunks = chunking.chunk_by_section(text)
    print("Section-based chunks:")
    print(f"Total chunks: {len(section_chunks)}")
    print("Example chunks:")
    for chunk in section_chunks[:3]:
        print(chunk)
        print("----")