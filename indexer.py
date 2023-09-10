import re
import os   # allows for looping through /DEV
from collections import defaultdict, OrderedDict
from bs4 import BeautifulSoup
import json
from simHash import fingerprint, sim

'''
Posting is a class that when initialized, forms an object
consisting of the document ID and the total tf-idf score
of that document
'''
# class Posting:
#     def __init__(self, docid, tfidf):
#         self.docid = docid # document id the token was found
#         self.tfidf = tfidf # tf-idf score = frequency count 

'''
BuildIndex passes a folder and builds an inverted index. The inverted index
maps a token to its corresponding posting. A posting consists of both the 
document ID and the frequency count of the token in that document. Tokens in
the inverted index may have more than one posting, as the token may appear
in more than one document.
'''
def BuildIndex(devFolder):

    invertedIndex = defaultdict(list)    # invertIndex dictionary to store all inverted index
    doc_num = 0     # record of doc id of current document // total will represent number of documents 
    doc_ids = defaultdict(str)
    invalid = 0
    doc_Lengths = defaultdict(int)
    # allMaps = []
    # store the posting info in the invertedIndex
    for subdir, dirs, files in os.walk(devFolder):
        for document in files:
            myMap, myPosition, docLength = getDocumentContent(os.path.join(subdir, document))      # get all tokens in current doc. mymap: {token: word_count}
            if myMap != None:
                #Detect and eliminate duplicate pages using fingerprint and simhash
                # simDetect = False
                # fscore = fingerprint(myMap)
                # for finger in allMaps:
                #     if sim(fscore, finger):
                #         simDetect = True
                #         break
                # if simDetect:
                #     continue
                # allMaps.append(myMap)
                doc_num += 1
                doc_ids[doc_num] = os.path.join(subdir, document)
                # doc_ids.append((doc_num, os.path.join(subdir, document)))   # print(f'{doc_num}:{os.path.join(subdir, document)}')
                doc_Lengths[doc_num] = docLength
                for token, count in myMap.items():
                    p = (doc_num, count, list(myPosition[token]))
                    #p = Posting(doc_num, count)      # form Posting object
                    invertedIndex[token].append(p)      # add Posting object to invertedIndex {token: set(Posting)}
                    
            else:
                invalid += 1
    # print(f'Unique documents: {doc_num}')
    # print(f'Invalid documents: {invalid}')
    # print(f'Unique tokens: {len(invertedIndex.keys())}')

    # 
    return doc_ids, invertedIndex, doc_num, doc_Lengths

'''
getDocumentContent passes a document and maps every token in that
document to its word count.
Example: {token: word_count}
'''
def getDocumentContent(documentFile):
    # load json file and get the url and html content
    document = open(documentFile)
    doc = json.load(document)
    url = doc["url"]
    content = doc["content"]
    # parse html content to extract tokens (BeautifulSoup)
    soup = BeautifulSoup(content, 'html.parser')
    if soup != None:
        if soup.script != None:
            soup.script.extract()
        if soup.style != None:
            soup.style.extract()
    myMap = defaultdict(int)
    myPosition = defaultdict(set)
    # identify tokens in parsed text and add it to map with its frequency
    docLength = 0
    for string in soup.stripped_strings:
        wordlist = re.split('[^a-zA-Z0-9]+', string)
        for word in wordlist:
            myMap[word.lower()] += 1
            myPosition[word.lower()].add(docLength)
            docLength += 1
        # 2 gram
        if len(wordlist) >= 2:
            for i in range(len(wordlist)-1):
                newPhrase = wordlist[i] + " " + wordlist[i+1]
                myMap[newPhrase.lower()] += 1
        # 3 gram
        if len(wordlist) >= 3:
            for i in range(len(wordlist)-2):
                newPhrase = wordlist[i] + " " + wordlist[i+1] + " " + wordlist[i+2]
                myMap[newPhrase.lower()] += 1

    
    # if the token is found in title, increase frequency count by 10
    # if (soup != None) and (soup.title != None):
    #     title = soup.title.text.strip()
    #     for word in re.split('[^a-zA-Z0-9]+', title):
    #         myMap[word.lower()] += 12

    # if the token is found in header, increase frequency by a certain amount
    # decreasing amount as # in h# increases
    if soup != None:
        for tag, weight in [("title", 12), ("h1", 7), ("h2", 6), ("h3", 5), ("h4", 4), ("h5", 3), ("h6", 2)]:
            for header in soup.find_all(tag):
                hwords = header.text.strip()
                for word in re.split('[^a-zA-Z0-9]+', hwords):
                    myMap[word.lower()] += weight

    return myMap, myPosition, docLength
    

'''
Helper function for json.dumps()
convert set to list
'''
def set_default(obj):
    return [{'docid': post[0], 'tfidf': post[1], 'position': post[2]} for post in obj]


if __name__ == "__main__":

    # choose: build / store, comment out one section

    # build index:
    # when running program, redirect stdout to a txt file
    
    # ids, iIndex = BuildIndex("DEV")
    # print("-----------------------------------------------")
    # print(f'token:[(docid, tfidf)]\n')
    # for token, postings in iIndex.items():
    #     if token != "":
    #         print(f'{token}:{[(post.docid, post.tfidf) for post in postings]}')
    # print("-----------------------------------------------")
    # for num, url in ids:
    #     print(f'{num}:{url}')

    # python3 indexer.py > invertedIndex.txt

    # -----------------------------------------------------------------------------------------
    
    # store index:
    # when running program, redirect stdout to a json file
    # comment out the print statements from BuildIndex 43-45

    # ----------------------------------------------------------
    
    ids, iIndex, n, docLengths = BuildIndex("DEV")

    # inverted index
    newIndex = OrderedDict()
    for key, val in sorted(iIndex.items(), key = lambda x: x[0]):
        newIndex[key] = val
    json_data1 = json.dumps(newIndex, default=set_default, indent=2)
    with open("invertedIndex2.json", "w") as o:
        o.write(json_data1)
    
    # document lengths
    json_data2 = json.dumps(docLengths, default=set_default, indent=2)
    with open("docLengths.json", "w") as s:
        s.write(json_data2)
    
    # document ids
    json_data3 = json.dumps(ids, default=set_default, indent=2)
    with open("ids.json", "w") as t:
        t.write(json_data3)

    print(f"extracted {n} documents")


    # for word in re.split('[^a-zA-Z0-9]+', "some sort of string, just to test whether the order stay the same or not, tis not important i mean this string not important but this feature may be useful for 2 gram and 3 gram alright this looks like a long enough string"):
    #     print(word)
    

    '''iIndex = json.loads("invertedIndex2.json")

    newIndex = OrderedDict()
    # count = 10
    for key, val in sorted(iIndex.items(), key = lambda x: x[0]):
        newIndex[key] = val

    #str1 = str()
    json_data = json.dumps(newIndex, default=set_default, indent=2)
    with open("invertedIndex2.json", "w") as o:
        o.write(json_data)'''

    # m = open("ids.txt")
    # for line in m.readlines():
    #     line = line.strip()
    #     tmp = line.split(":")
    #     tmp[0] = "\"" + tmp[0] + "\""
    #     tmp[1] = "\"" + tmp[1] + "\""
    #     print(f"{tmp[0]}:{tmp[1]},")

    #print(json_data)
    #print(newIndex)

    # a = open("invertedIndex.json").read()
    # a = a[27:-2]
    # print(a)


    # # python3 121-pj3-m2/indexer.py > invertedIndex.json
