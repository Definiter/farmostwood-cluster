import cPickle as pickle
import math
import random
import copy

clusterSum = 6

class Document:
    def __init__(self, title, category, text, time):
        self.title = title
        self.category = category
        self.text = text
        self.time = datetime.strptime(time, '%A, %B %d, %Y at %I:%M%p')

class DocVector:
    cluster = -1
    num = -1
    def __init__(self, v):
        self.v = v
    def normalize(self):
        docLen = 0
        for term in self.v:
            docLen += term * term
        docLen = math.sqrt(docLen)
        if docLen != 0:
            for i in range(len(self.v)):
                self.v[i] = self.v[i] / docLen
        else:
            self.v = [1] * len(self.v)
            self.normalize()
    def distance(self, docVec2):
        dis = 0
        for i in range(len(self.v)):
            dis += (self.v[i] - docVec2.v[i]) ** 2
        dis = math.sqrt(dis)
        return dis
    def cosDis(self, docVec2):
        dis = 0
        for i in range(len(self.v)):
            dis += self.v[i] * docVec2.v[i]
        return dis
    def printVec(self):
        print self.num, ':'
        for term in self.v:
            print term,
        print
            

def printDocMat(d):
    matrixFile = open('matrix.txt', 'w+')
    for document in d:
        matrixFile.write('document No.' + str(document.num) + '\n')
        for i, term in enumerate(document.v):
            if term != 0:
                matrixFile.write(str(i) + ':' + str(term) + '\n')
        matrixFile.write('\n')
    matrixFile.close()

def calcRSS(docVec, clusterCenter):
    RSS = [0] * clusterSum
    for doc in docVec:
        RSS[doc.cluster] += clusterCenter[doc.cluster].distance(doc) ** 2
    totalRSS = 0
    for rss in RSS:
        totalRSS += rss
    return rss

resultFile = open('result.txt', 'w+')
def printClusterResult(docVec):
    clusterDoc = [] 
    for i in range(clusterSum):
        clusterDoc.append([])
    for doc in docVec:
        if doc.cluster != -1:
            clusterDoc[doc.cluster].append(doc)
        else:
            clusterDoc[clusterSum].append(doc)
    for i, cluster in enumerate(clusterDoc):
        resultFile.write(str(i) + ':\n')
        for doc in cluster:
            resultFile.write(str(doc.num) + ' - ' + documents[doc.num].category + ' ')
            resultFile.write(documents[doc.num].title.encode('utf-8'))
            resultFile.write('\n')
        resultFile.write('\n')
    del clusterDoc

documents = []
documents = pickle.load(open('documents.txt'))


docNonPhoto = []
for doc in documents:
    if doc.category != 'Photo':
        docNonPhoto.append(doc)

documents = docNonPhoto

'''
contentFile = open('content.txt', 'w+')
for i, doc in enumerate(documents):
    contentFile.write(str(i) + ' - ') 
    contentFile.write(doc.category)
    contentFile.write(' : ')
    contentFile.write(doc.title.encode('utf-8'))
    contentFile.write('\n')
contentFile.close()
'''

documentSum = len(documents)

#calc every term's document frequency
termDF = {}
for document in documents:
    termTF = {}
    for term in document.text:
        if not term in termTF:
            termTF[term] = 0
        termTF[term] += 1
    for term in termTF:
        if termTF[term] > 0:
            if not term in termDF:
                termDF[term] = 0
            termDF[term] += 1

#calc every term's IDF
termIDF = {}
for term in termDF:
    termIDF[term] = math.log(documentSum / termDF[term], 2)

IDF = []
for term in termIDF:
    IDF.append(termIDF[term])
IDF = sorted(IDF)
thresholdIDF = IDF[int(1 / 100.0 * len(IDF))]

newTermIDF = {}
for term in termIDF:
    if (termIDF[term] >= thresholdIDF):
        newTermIDF[term] = termIDF[term]
termIDF = newTermIDF

#sign term's index
termSum = -1
termToIndex = {}
indexToTerm = []
for term in termIDF:
    termSum += 1
    termToIndex[term] = termSum
    indexToTerm.append(term)
termSum += 1

print termSum

#calc document-term matrix
docVec = []
for i, document in enumerate(documents):
    termTF = {}
    for term in document.text:
        if not term in termTF:                      
            termTF[term] = 0
        termTF[term] += 1
    docVec.append(DocVector([0] * termSum))
    for term in termTF:
        if term in termIDF:
            docVec[-1].v[termToIndex[term]] = termTF[term] * termIDF[term]
    docVec[-1].normalize()
    docVec[-1].num = i

#get documents' keywords
keywordFile = open('keyword.txt', 'w+')
for doc in docVec:
    d = documents[doc.num]
    keywordFile.write(d.title.encode('utf-8') + ':\n')
    termTFIDF = []
    for i, term in enumerate(doc.v):
        termTFIDF.append((i, term))
    termTFIDF = sorted(termTFIDF, key = lambda x : x[1], reverse = True)
    for i in range(5):
        keywordFile.write(indexToTerm[termTFIDF[i][0]].encode('utf-8'))
        keywordFile.write(', ')
    keywordFile.write('\n\n\n')
keywordFile.close()
    



#k-means cluster

##random initial seed

clusterCenter = [0] * clusterSum
seeds = []
for i in range(clusterSum):
    seed = random.randint(0, documentSum - 1)
    while seed in seeds:
        seed = random.randint(0, documentSum - 1)
    docVec[seed].cluster = i
    seeds.append(seed)
    clusterCenter[i] = copy.deepcopy(docVec[seed])

##nonrandom initial seeds
'''
clusterCenter = [0] * clusterSum
seeds = [0, 272, 276, 113, 100, 263, 209, 117, 14]
for i, seed in enumerate(seeds):
    docVec[seed].cluster = i
    clusterCenter[i] = copy.deepcopy(docVec[seed])
'''

##cluster
rssThreshold = 1e-10
count = 0
while True:
    count += 1
    print count, ':'
    preRSS = calcRSS(docVec, clusterCenter)
    #assgin cluster
    for i in range(len(docVec)):
        '''
        minDis = 1e10
        for center in clusterCenter:
            dis = center.distance(docVec[i])
            if minDis > dis:
                minDis = dis
                closestCenter = center
        docVec[i].cluster = copy.deepcopy(closestCenter.cluster)
        #resultFile.write(str(i) + '<->' + str(closestCenter.num) + ' ' + str(minDis) + '\n')
        '''
        maxCosDis = -1e10
        for center in clusterCenter:
            dis = center.cosDis(docVec[i])
            if maxCosDis < dis:
                maxCosDis = dis
                closestCenter = center
        docVec[i].cluster = copy.deepcopy(closestCenter.cluster)
        
    nowRSS = calcRSS(docVec, clusterCenter)
    if abs(preRSS - nowRSS) < rssThreshold:
        break
    #find new center
    newCenter = []
    for i in range(clusterSum):
        newCenter.append(DocVector([0] * termSum))
    clusterCount = [0] * clusterSum
    for doc in docVec:
        clusterCount[doc.cluster] += 1
        for i, term in enumerate(doc.v):
            newCenter[doc.cluster].v[i] += term
    for i in range(len(newCenter)):
        for j in range(len(newCenter[i].v)):
            if clusterCount[i] != 0:
                newCenter[i].v[j] /= clusterCount[i]
    for i in range(len(clusterCenter)):
        newCenter[i].normalize()
        newCenter[i].cluster = i
        clusterCenter[i] = copy.deepcopy(newCenter[i])

printClusterResult(docVec)
resultFile.close()


