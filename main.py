from chromadb_search.chromadb_helpers import insert_into_chromadb, search_related_words
from chromadb_search.extract_data import fetch_vocab
import time


def main():
    # Fetch vocabulary from SQLite
    # vocabulary = fetch_vocab()
    
    # Insert vocabulary into ChromaDB
    # insert_into_chromadb(vocabulary)
    
    # Search related words based on user input
    start = time.perf_counter()
    user_input = "Arbeit"
    related_words = search_related_words(user_input, 100)
    end = time.perf_counter()
    elapsed = end - start
    
    print(f"[{elapsed:.4f} seconds] Related words:", related_words["documents"])

if __name__ == "__main__":
    main()
