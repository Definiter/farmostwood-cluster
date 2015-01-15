from datetime import datetime
from bs4 import BeautifulSoup
from os import path
import re
import cPickle as pickle
import jieba

class Document:
    def __init__(self, title, category, text, time):
        self.title = title
        self.category = category
        self.text = text
        self.time = datetime.strptime(time, '%A, %B %d, %Y at %I:%M%p')

documents = []
sum = 0

logFile = open('log.txt', 'w+')

wordCount = []

for i in range(1, 800):
    filePath =('blog.farmostwood.net/' + str(i) + '.html')
    if path.exists(filePath):
        htmlFile = open(filePath)
        htmlDoc = htmlFile.read()
        soup = BeautifulSoup(htmlDoc)

        title = soup.find_all(property = 'og:title')[0]['content']

        post = soup.find_all(class_ = 'entrytext')[0]
        if post.small == None and soup.small == None:
            logFile.write(str(i) + '\n')
            continue
        time = soup.small.text[27 : soup.small.text[2:].find('\r') + 1]
        time = re.sub(r"st,|nd,|rd,|th,", ",", time)

        category = soup.small.a.text

        soup.small.clear()
        text = post.text[1: -3]
        wordCount.append(len(post.text))
        text = list(jieba.cut(text))
        
        documents.append(Document(title, category, text, time))
        
        sum += 1
        outputFile = open('text/' + str(i) + '.txt', 'w+')
        outputFile.write(title.encode('utf-8'))
        outputFile.write('\n')
        outputFile.write(category.encode('utf-8'))
        outputFile.write('\n')
        outputFile.write(documents[-1].time.strftime('%Y-%m-%d %H:%M'))
        outputFile.write('\n')
        outputFile.write(post.text[1: -3].encode('utf-8'))
        
        outputFile.close()
        htmlFile.close()

logFile.close()

yearCount = {}
for document in documents:
    year = str(document.time.year)
    if not year in yearCount:
        yearCount[year] = 0
    else:
        yearCount[year] += 1

for i in range(2003, 2015):
    print i, yearCount[str(i)]

averageWordCount = 0
for count in wordCount:
    averageWordCount += count
averageWordCount /= float(len(wordCount))

print averageWordCount


pickle.dump(documents, open('documents.txt', 'wb+'), True)
