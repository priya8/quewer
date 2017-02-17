"""
From this paper: http://acl.ldc.upenn.edu/acl2004/emnlp/pdf/Mihalcea.pdf 

External dependencies: nltk, numpy, networkx

Based on https://gist.github.com/voidfiles/1646117
"""

import nltk
import itertools
from operator import itemgetter
import networkx as nx
import os
import re
import difflib

#apply syntactic filters based on POS tags if noun adjective or nnp
def filter_for_tags(tagged, tags=['NN', 'JJ', 'NNP']):
    return [item for item in tagged if item[1] in tags]

def normalize(tagged):
    return [(item[0].replace('.', ''), item[1]) for item in tagged]

def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

def lDistance(firstString, secondString):
    "Function to find the Levenshtein distance between two words/sentences - gotten from http://rosettacode.org/wiki/Levenshtein_distance#Python"
    if len(firstString) > len(secondString):
        firstString, secondString = secondString, firstString
    distances = range(len(firstString) + 1)
    for index2, char2 in enumerate(secondString):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(firstString):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1], distances[index1+1], newDistances[-1])))
        distances = newDistances
    return distances[-1]

def buildGraph(nodes):
    "nodes - list of hashtables that represents the nodes of the graph"
    gr = nx.Graph() #initialize an undirected graph
    gr.add_nodes_from(nodes)
    nodePairs = list(itertools.combinations(nodes, 2))

    #add edges to the graph (weighted by Levenshtein distance)
    for pair in nodePairs:
        firstString = pair[0]
        secondString = pair[1]
        levDistance = lDistance(firstString, secondString)
        gr.add_edge(firstString, secondString, weight=levDistance)

    return gr

def buildGraphForSentences(nodes,keyphrases):
    "nodes - list of hashtables that represents the nodes of the graph"
    gr = nx.Graph() #initialize an undirected graph
    gr.add_nodes_from(nodes)
    nodePairs = list(itertools.combinations(nodes, 2))

    #add edges to the graph (weighted by Levenshtein distance)
    for pair in nodePairs:
        value = 1.0
        firstString = pair[0]
        secondString = pair[1]
        #modifying the weights on the basis of keyword factor in them
        if any(word in firstString for word in keyphrases):
            value = value+0.05
        if any(word in secondString for word in keyphrases):
            value = value+0.05
        levDistance = lDistance(firstString, secondString)*value
        gr.add_edge(firstString, secondString, weight=levDistance)

    return gr

def extractKeyphrases(text):
    #tokenize the text using nltk
    wordTokens = nltk.word_tokenize(text)

    #assign POS tags to the words in the text
	#define type of word.
    tagged = nltk.pos_tag(wordTokens)
    textlist = [x[0] for x in tagged]
    
    tagged = filter_for_tags(tagged)
    tagged = normalize(tagged)

    unique_word_set = unique_everseen([x[0] for x in tagged])
    word_set_list = list(unique_word_set)

   #this will be used to determine adjacent words in order to construct keyphrases with two words

    graph = buildGraph(word_set_list)

    #pageRank - initial value of 1.0, error tolerance of 0,0001, 
    calculated_page_rank = nx.pagerank(graph, weight='weight')

    #most important words in ascending order of importance
    keyphrases = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)

    #the number of keyphrases returned will be relative to the size of the text (a third of the number of vertices) why a third ??
    aThird = len(word_set_list) / 3
    keyphrases = keyphrases[0:aThird+1]

    #take keyphrases with multiple words into consideration as done in the paper - if two words are adjacent in the text and are selected as keywords, join them
    #together
    modifiedKeyphrases = set([])
    dealtWith = set([]) #keeps track of individual keywords that have been joined to form a keyphrase
    i = 0
    j = 1
    while j < len(textlist):
        firstWord = textlist[i]
        secondWord = textlist[j]
        if firstWord in keyphrases and secondWord in keyphrases:
            keyphrase = firstWord + ' ' + secondWord
            modifiedKeyphrases.add(keyphrase)
            dealtWith.add(firstWord)
            dealtWith.add(secondWord)
        else:
            if firstWord in keyphrases and firstWord not in dealtWith: 
                modifiedKeyphrases.add(firstWord)

            #if this is the last word in the text, and it is a keyword,
            #it definitely has no chance of being a keyphrase at this point    
            if j == len(textlist)-1 and secondWord in keyphrases and secondWord not in dealtWith:
                modifiedKeyphrases.add(secondWord)
        
        i = i + 1
        j = j + 1
        
    return modifiedKeyphrases

def extractSentences(text,keyphrases):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentenceTokens = sent_detector.tokenize(text.strip())
    noOfSentence = len(sentenceTokens)
    graph = buildGraphForSentences(sentenceTokens,keyphrases)
    calculated_page_rank = nx.pagerank(graph, weight='weight')

    #most important sentences in ascending order of importance
    sentences = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)
    sentence_splitted = []
	#split sentence concatnated by algorithm
    for sentence in sentences :
        for sen in re.split('[?.]',sentence):
		    sentence_splitted.extend(sen + '.')
    #find optimum summarization length
    opti = noOfSentence
    if(noOfSentence >10 and noOfSentence < 20):
         opti = noOfSentence/2
    if(noOfSentence >=20 and noOfSentence < 40) :
         opti = (noOfSentence/2)+5
    if(noOfSentence >=40):
         opti = 30
    summary = []
    
    for sentence in sentences[0:opti] :
        summary.append(sentence)
    ordered = ''
    #reorder the summary in the order of recieving. this is a really long task. it will eat up a lot of time.
    for sentRec in sentenceTokens :
        for sentSumm in summary:
            if(sentRec == sentSumm):
                ordered = ordered + sentSumm + '\n'      
    return ordered

#def writeFiles(summary, keyphrases):
    "outputs the keyphrases and summaries to appropriate files"
    #write keywords from question
    #keyphraseFile = open('keywords/' + 'queKeywords.txt', 'w')
    #for keyphrase in keyphrases:
    #    keyphrase = keyphrase.encode('utf-8')
    #    keyphraseFile.write(keyphrase+'\n')
    #keyphraseFile.close()

    #write answer summary file
    #summaryFile = open('summaries/' + 'ansSummary.txt', 'w')
    #summary = summary.encode('utf-8')
    #summaryFile.write(summary)
    #summaryFile.close()

    #print "-"


#retrieve question and summarize answer according to it
def summarized(qtext,anstext):
    #articles = os.listdir("articles")
    #articleFile = open('articles/' + 'que.txt', 'r')
    #text = articleFile.read() 
    #qtext = text.decode('utf-8')
    keyphrases = extractKeyphrases(qtext)
    #ansFile = open('articles/' + 'ans.txt' ,'r')
    #anstext = ansFile.read()
    #anstext = anstext.decode('utf-8')
    summary = extractSentences(anstext,keyphrases)
    #writeFiles(summary, keyphrases)
    return summary