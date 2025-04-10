import chromadb
from chromadb_search.create_embeddings import generate_embedding

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chromadb_data")

# Create or get a collection in ChromaDB
collection = client.get_or_create_collection("vocabulary_embeddings")

def insert_into_chromadb(vocabulary):
    for entry in vocabulary:
        word = entry.word
        embedding = generate_embedding(word)
        # Insert word and embedding into ChromaDB
        collection.upsert(
            ids=[str(entry.id)],
            documents=[word],
            metadatas=[{"level": entry.level}],
            embeddings=[embedding]
        )
        print(f"Added record: {entry.id} - {entry.word}")

def search_related_words(user_input, limit=5):
    user_embedding = generate_embedding(user_input)
    
    # Perform the similarity search
    results = collection.query(
        query_embeddings=[user_embedding],
        n_results=limit  # Number of similar words you want to retrieve
    )
    
    return results
