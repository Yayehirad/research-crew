"""Build a search index of your lecture PDFs, and search it.

    python notes_index.py                  (re)build the index
    python notes_index.py "a question"     search the index
"""
import sys
import chromadb
from ollama import embed
from pypdf import PdfReader
from config import DOCS_DIR, DB_DIR, EMBED_MODEL

CHUNK_SIZE = 800   # characters per chunk
OVERLAP = 100      # characters shared between neighbouring chunks
COLLECTION = "notes"


def split_text(text: str) -> list[str]:
    """Cut text into overlapping chunks so no sentence is lost at a boundary."""
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - OVERLAP
    return [c for c in chunks if c.strip()]


def get_collection():
    client = chromadb.PersistentClient(path=str(DB_DIR))
    return client.get_or_create_collection(COLLECTION)


def build_index() -> None:
    pdfs = sorted(DOCS_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {DOCS_DIR}")
        print("Put your lecture PDFs there, or change DOCS_DIR in config.py.")
        sys.exit(1)

    # Start fresh each time so old chunks don't pile up
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.get_or_create_collection(COLLECTION)

    total = 0
    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page_number, page in enumerate(reader.pages, start=1):
            chunks = split_text(page.extract_text() or "")
            if not chunks:
                continue
            vectors = embed(model=EMBED_MODEL, input=chunks).embeddings
            collection.add(
                ids=[f"{pdf.name}-p{page_number}-{i}" for i in range(len(chunks))],
                documents=chunks,
                embeddings=vectors,
                metadatas=[{"file": pdf.name, "page": page_number}] * len(chunks),
            )
            total += len(chunks)
        print(f"  {pdf.name}: {len(reader.pages)} pages")
    print(f"Stored {total} chunks from {len(pdfs)} PDFs in {DB_DIR}")


def search_index(question: str, k: int = 4) -> list[dict]:
    """Return the k chunks closest in meaning to the question."""
    collection = get_collection()
    if collection.count() == 0:
        return []
    vector = embed(model=EMBED_MODEL, input=[question]).embeddings[0]
    found = collection.query(query_embeddings=[vector], n_results=k)
    return [
        {"text": text, "file": meta["file"], "page": meta["page"]}
        for text, meta in zip(found["documents"][0], found["metadatas"][0])
    ]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) > 1:                       # a question was given: search
        for hit in search_index(" ".join(sys.argv[1:])):
            snippet = hit["text"][:150].replace("\n", " ")
            print(f"[{hit['file']}, page {hit['page']}] {snippet}...\n")
    else:                                       # no question: build the index
        build_index()