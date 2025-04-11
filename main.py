from chromadb_search.chromadb_helpers import insert_into_chromadb, search_related_words
from chromadb_search.extract_data import fetch_vocab
import time

def execute_search(input, priority_keywords):
    start = time.perf_counter()
    related_words = search_related_words(input, priority_keywords)
    end = time.perf_counter()
    elapsed = end - start
    
    print(f"[{elapsed:.4f} seconds] Related words:", [word["word"] for word in related_words])
    print([f"{word["word"]} - {word["metadata"]["level"]}" for word in related_words if word["metadata"]["level"] != "c1.1" and word["metadata"]["level"] != "c1.2"])

def main():
    # Fetch vocabulary from SQLite
    # vocabulary = fetch_vocab()
    
    # Insert vocabulary into ChromaDB
    # insert_into_chromadb(vocabulary)
    
    # Search related words based on user input
    execute_search("Umwelt", priority_keywords=["umwelt", "natur", "klima", "ökolog", "nachhalt", "umweltschutz", "umweltbewusst"])

if __name__ == "__main__":
    main()
