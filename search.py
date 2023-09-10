from collections import defaultdict
from indexer import BuildIndex
from urllib.parse import urldefrag
from math import log, sqrt
import time
import json
import numpy as np

'''
iIndex: {token:[Posting]}
Posting: {.docid, .tfidf}
ids: {docid: file}
'''

numResults = 15  # This is the amount of results we want to appear on the page

'''
findTopID passes the inverted index, the user search query, and the number of
results we want. The function discovers the top files from the inverted Index 
database, where each file contains all queryWords and returns a list of the doc 
IDs of these files

BOOLEAN RETRIEVAL (OLD IMPLEMENTATION):
    boolAND: {docid: count} 
    For each file that comes up in any of the query terms, keep track of the 
    number of files they appeared in. 
    If the count is less than len(queryWords), the file does not satisfy the 
    AND search query.

    tfidfScore: {docid: count} 
    For each file, keep track of the sum of the tfidf across all query terms.

RANKED RETRIEVAL:
    cosineScores: {docid: similarity score}
    For each document, compute the similarity score to rank the relavancy of
    the document based on the user query words.
'''


def findTopID(iIndex, queryWords, nresults, n, document_lengths):

    # boolean AND:

    # boolAND = defaultdict(int)
    # tfidfScore = defaultdict(int)

    # result = []

    # # For each query token, find all files that contain that query token
    # # For each of these files, update their boolAND count and tfidfScore scores
    # for term in queryWords:
    #     postings = iIndex[term]
    #     for post in postings:
    #         boolAND[post["docid"]] += 1
    #         tfidfScore[post["docid"]] += (post["tfidf"] * log(n/len(iIndex[term])))

    # # Iterating through the files starting from the greatest to smallest tf-idf score
    # # If that file contains all query terms, add to result
    # for doc, score in sorted(tfidfScore.items(), key = lambda x: x[1], reverse = True):
    #     if boolAND[doc] == len(queryWords): # Check if doc contains all query terms
    #         result.append((doc, score))
    #         if len(result) == num:
    #             break
    # return result[0:nresults]

    cosineScores = calculate_cosine_similarity(
        queryWords, iIndex, document_lengths)
    return sorted(cosineScores.items(), key=lambda x: x[1], reverse=True)[0:nresults]


'''
calculate_cosine_similarity passes the query terms, inverted index, and the list of document
lengths. A query vector is created and contains the weight (frequency) for each of the query terms.
If a term is in the inverted index, iterate through each posting of that term in the 
inverted index and create a document vector. Calculate the cosine similarity using the dot
product of the query and doc vector and divide that by the magnitude of the doc vector.
'''

'''
FIRST COSINE SIM
def calculate_cosine_similarity(query_terms, inverted_index, document_lengths):
    document_scores = defaultdict(float)
    query_vector = np.zeros(len(query_terms))
    
    # Calculate the term frequency in the query
    for i, term in enumerate(query_terms):
        query_vector[i] = query_terms.count(term)
    
    # Calculate the document scores using the inverted index
    for term in query_terms:
        if term in inverted_index:
            query_weight = query_vector[query_terms.index(term)]
            
            for eachPosting in inverted_index[term]:
                document_vector = np.zeros(len(query_terms))
                document_vector[query_terms.index(term)] = eachPosting['tfidf'] / document_lengths[str(eachPosting['docid'])]
                
                # Calculate the dot product of the query vector and document vector
                dot_product = np.dot(query_vector, document_vector)
                
                # Calculate the magnitude of the query vector
                query_magnitude = np.linalg.norm(query_vector)
                
                # Calculate the magnitude of the document vector
                document_magnitude = np.linalg.norm(document_vector)
                
                # Calculate the cosine similarity and update the document score
                cosine_similarity = dot_product / (query_magnitude * document_magnitude)
                document_scores[eachPosting['docid']] += query_weight * cosine_similarity

    # sorted_document_scores = dict(sorted(document_scores.items(), key=lambda x:x[1], reverse=True))
    return document_scores
'''


def calculate_cosine_similarity(query_terms, inverted_index, document_lengths):
    document_scores = defaultdict(float)
    query_vector = np.zeros(len(query_terms))

    # Calculate the term frequency in the query
    for i, term in enumerate(query_terms):
        query_vector[i] = query_terms.count(term)

    # Normalize the query vector
    query_vector /= np.linalg.norm(query_vector)

    # Boolean to check if all queryWords are in the doc
    boolAND = defaultdict(int)

    # Calculate the document scores using the inverted index
    unique_terms = 0
    for term in query_terms:
        if " " not in term:
            unique_terms += 1
        # Check if the term is in the inverted index
        if term in inverted_index:
            # doc_weight = query_vector[query_terms.index(term)] // SCRAPPED
            for eachPosting in inverted_index[term]:
                # Add to boolAND
                boolAND[eachPosting[0]] += 1

                document_vector = np.zeros(len(query_terms))
                document_vector[query_terms.index(
                    term)] = eachPosting[1] / document_lengths[str(eachPosting[0])]

                # Calculate the dot product of the query vector and document vector
                dot_product = np.dot(query_vector, document_vector)

                # Calculate the magnitude of the document vector and query vector
                document_magnitude = np.linalg.norm(document_vector)
                query_magnitude = np.linalg.norm(query_vector)

                # Calculate the cosine similarity and update the document score
                cosine_similarity = dot_product / \
                    (document_magnitude*query_magnitude)
                doc_weight = eachPosting[1]

                # Check if the current doc now contains all queryWords
                if boolAND[eachPosting[0]] == unique_terms:
                    doc_weight = doc_weight ** 2

                document_scores[eachPosting[0]
                                ] += doc_weight * cosine_similarity

    # sorted_document_scores = dict(sorted(document_scores.items(), key=lambda x:x[1], reverse=True))
    return document_scores


if __name__ == "__main__":

    # Build index
    # TODO: switch to loading index from disk
    print("---- Start Building Index ----")

    load_start = time.time_ns()//1000000
    with open("invertedIndex2.json", "r") as invertedIndex:
        iIndex = json.load(invertedIndex)
    n = 55393
    load_end = time.time_ns()//1000000
    print(f'Load inverted index in:\t{load_end-load_start} milliseconds')

    load_start = time.time_ns()//1000000
    with open("ids.json", "r") as docIDs:
        ids = json.load(docIDs)
    load_end = time.time_ns()//1000000
    print(f'Load ids in:\t{load_end-load_start} milliseconds')

    load_start = time.time_ns()//1000000
    with open("docLengths.json", "r") as docL:
        docLength = json.load(docL)
    load_end = time.time_ns()//1000000
    print(f'Load doc lengths in:\t{load_end-load_start} milliseconds')

    # ids, iIndex, n = BuildIndex("../DEV")

    print("----  End Building Index  ----")

    cont = True
    while True:
        print("---- start of query ----")
        # Retrieve the search query input from user
        # does not delete duplicate terms in the search query
        initial_command = input("Search query: ").lower().split()
        command = initial_command
        if len(initial_command) >= 2:
            for i in range(len(initial_command)-1):
                newPhrase = initial_command[i] + " " + initial_command[i+1]
                for _ in range(3):
                    command.append(newPhrase)
        if len(initial_command) >= 3:
            for i in range(len(initial_command)-2):
                newPhrase = initial_command[i] + " " + \
                    initial_command[i+1] + " " + initial_command[i+2]
                for _ in range(5):
                    command.append(newPhrase)

        # if "" in command:
        #     command.remove("")

        # if len(command) == 0:     empty search query?
        #     break

        # start timer for tracking the duration of the search
        start = time.time_ns()//1000000

        topIds = findTopID(iIndex, command, numResults, n, docLength)
        # topURL = []
        print(f"Query Terms:\t{command}\n")

        # end timer
        end = time.time_ns()//1000000
        print(f'Query results in:\t{end-start} milliseconds')

        validURL = 0
        validURLList = []
        for i, score in topIds:
            if validURL >= 5:
                break
            with open(ids[str(i)], "r") as o:
                data = json.load(o)
                url = urldefrag(data["url"])[0]
                if url not in validURLList:
                    validURL += 1
                    validURLList.append(url)
                    print(f'Score:\t{score}\nURL:\t{url}')
            # topURL.append(ids[i])
        print("----  End of Query  ----")
        while True:
            checkCont = input("Keep Searching? (y/n): ")
            if checkCont.lower() in ["n", "no", "false"]:
                cont = False
                break
            elif checkCont.lower() in ["y", "yes", "true"]:
                break
            else:
                print("Invalid Input\n")

        if cont == False:
            break
