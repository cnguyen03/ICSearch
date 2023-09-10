from collections import defaultdict
from math import sqrt

def calculate_cosine_similarity(queryWords, iIndex, document_lengths):
    query_weights = defaultdict(float)
    
    # Calculate the term frequency in the query and give it a default weight of 1
    for term in queryWords:
        query_weights[term] += 1
    
    # Normalize the query weights so that query vector is a unit vector
    query_length = sqrt(sum(weight ** 2 for weight in query_weights.values()))
    query_weights = {term: weight / query_length for term, weight in query_weights.items()}
    
    document_scores = defaultdict(float)
    
        # Initialize the document scores with all document IDs
    for doc_id in range(num_documents):
        document_scores[doc_id] = 0.0
        
    # Calculate the document scores using the inverted index
    for term in queryWords:
        if term in iIndex:      # Check if term is in the inverted index
            query_weight = query_weights[term]
        
            for doc_id, frequency in iIndex[term]:
                document_weight = frequency / document_lengths[doc_id]
                document_scores[doc_id] += query_weight * document_weight

    sorted_document_scores = dict(sorted(document_scores.items(), key=lambda x:x[1], reverse=True))
    return sorted_document_scores

if __name__ == "__main__":
    query = ["michael", "teaches", "ics"]
    inverted_index = {"michael": ((1,1), (2,1), (3,1), (4,1)), "teaches": ((1,1), (3,1), (4,1)), "ics": ((1,1), (3,1)), "data": ((1,1))}
    document_lens = [1000, 1000, 1000, 500, 800]
    print(calculate_cosine_similarity(query, inverted_index, document_lens))
