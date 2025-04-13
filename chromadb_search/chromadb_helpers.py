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

# def search_related_words(user_input, limit=5):
#     user_embedding = generate_embedding(user_input)
    
#     # Perform the similarity search
#     results = collection.query(
#         query_embeddings=[user_embedding],
#         n_results=limit  # Number of similar words you want to retrieve
#     )
    
#     return results

def search_related_words(user_input, priority_keywords, limit=200, max_distance=40):
    user_embedding = generate_embedding(user_input)
    
    # Get more results than you might keep, just in case
    results = collection.query(
        query_embeddings=[user_embedding],
        n_results=limit
    )
    
    distances = results['distances'][0]
    documents = results['documents'][0]
    ids = results['ids'][0]
    metadatas = results.get('metadatas', [[]])[0]

    # Filter by distance threshold
    filtered = [
        {
            "id": id_,
            "word": doc,
            "distance": dist,
            "metadata": meta
        }
        for id_, doc, dist, meta in zip(ids, documents, distances, metadatas)
        if dist <= max_distance
    ]

    return rerank_results(filtered, priority_keywords)


def rerank(results, boost_keywords, alpha=1.0, beta=0.5):
    reranked = []

    for result in results:
        word_lower = result["word"].lower()
        # Boost if any keyword appears in the word
        boost_score = sum(1 for kw in boost_keywords if kw in word_lower)
        # New score: higher is better, so invert similarity (assumes lower = better match)
        score = -result["distance"] + alpha * boost_score
        reranked.append((result["word"], score))

    # Sort by descending score (higher = more relevant)
    return sorted(reranked, key=lambda x: x[1], reverse=True)


def rerank_results(results, priority_keywords=None, alpha=1.5, normalize=True):
    if priority_keywords is None:
        priority_keywords = ["umwelt", "klima", "ökolog", "nachhalt", "natur", "umweltschutz"]

    # Normalize distances to scores [0, 1], where 1 = most relevant
    if normalize:
        distances = [r["distance"] for r in results]
        min_dist, max_dist = min(distances), max(distances)
        norm_score = lambda d: 1.0 - ((d - min_dist) / (max_dist - min_dist + 1e-8))
    else:
        norm_score = lambda d: -d  # inverse distance as score

    reranked = []
    for item in results:
        word_lower = item["word"].lower()
        base_score = norm_score(item["distance"])

        # Boost if keyword present in word
        keyword_boost = sum(1 for kw in priority_keywords if kw in word_lower)
        final_score = base_score + alpha * keyword_boost

        # Add score for sorting or output
        item["score"] = final_score
        reranked.append(item)

    # Sort descending by score
    reranked.sort(key=lambda x: x["score"], reverse=True)
    return reranked
