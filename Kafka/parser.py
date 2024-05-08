import json
import os
import pathlib
import re
from copy import deepcopy
from datetime import datetime
import datefinder
import glob
import numpy as np
import pandas as pd
from dateparser.search import search_dates
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from fuzzywuzzy import fuzz
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
nltk.download('vader_lexicon')

nlp = spacy.load('en_core_web_sm', disable=['ner', 'textcat'])


class TimeTag:
    def __init__(self, date, count):
        self.date = date
        self.count = count
        self.weight = count
        self.flag = False

    def __repr__(self):
        return f'date: {self.date}, weight: {self.weight}, count: {self.count}'


class parser():
    def __init__(self):
        self.index = {}

    def clean(self, doc):
        doc = doc.lower()
        doc = nlp(doc)
        tokens = [tokens.lower_ for tokens in doc]
        tokens = [tokens for tokens in doc if (tokens.is_stop == False)]
        tokens = [tokens for tokens in tokens if (tokens.is_punct == False)]
        try:
            final_token = [WordNetLemmatizer().lemmatize(token.text) for token in tokens]
        except:
            import nltk
            nltk.download('wordnet')
            nltk.download('omw-1.4')
            final_token = [WordNetLemmatizer().lemmatize(token.text) for token in tokens]
        return " ".join(final_token)

    def sentences(self, text):
        text = re.split('[.?]', text)
        clean_sent = []
        for sent in text:
            clean_sent.append(sent)
        return clean_sent

    def load_cities(self, file):
        df = pd.read_csv(file)
        df = df.dropna()
        df = df["Locations"]
        Data_of_region = df.values.tolist()
        Data_of_region = [each_city.lower() for each_city in Data_of_region]
        Data_of_region = list(dict.fromkeys(sorted(Data_of_region)))
        index = dict()
        flag = False
        push = False
        current_alphabet = ""
        start = 0
        finish = 0
        for i in range(len(Data_of_region)):
            if i != 0 and Data_of_region[i][0] != Data_of_region[i][0]:
                flag = True
                push = True
                finish = i-1
            if push == True:
                index[current_alphabet] = finish
            if flag == False:
                start = i
                current_alphabet = Data_of_region[i][0]
                index.__setitem__(current_alphabet, start)
        self.index = index
        self.Data_of_region = Data_of_region

    def preprocess_text(self, text):
        tokens = text.lower().split()
        stopwords = set(['a', 'an', 'the', 'and', 'but', 'to', 'of', 'at', 'in', 'on', 'with', 'for', 'by', 'from', 'said'])
        tokens = [token for token in tokens if token not in stopwords]
        preprocessed_text = ' '.join(tokens)
        return preprocessed_text
    
    def Lda(self, articles, num_topics=1, num_words=1, max_df=0.90, min_df=1):
        vectorizer = TfidfVectorizer(max_df=max_df, min_df=min_df,stop_words='english')
        X = vectorizer.fit_transform(articles)
        feature_names = vectorizer.get_feature_names_out()
        lda = LatentDirichletAllocation(n_components=num_topics, max_iter=10, random_state=10).fit(X)
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            topic_words = [feature_names[i] for i in topic.argsort()[:-num_words - 1:-1]]
            topics.extend(topic_words)
        return topics

    def topic_model_nmf(self, articles, num_topics=1, num_words=1, max_df=0.90, min_df=1):
        vectorizer = TfidfVectorizer(max_df=max_df, min_df=min_df,stop_words='english')
        X = vectorizer.fit_transform(articles)
        feature_names = vectorizer.get_feature_names_out()
        nmf = NMF(n_components=num_topics, max_iter=1000, random_state=10).fit(X)
        topics = []
        for topic_idx, topic in enumerate(nmf.components_):
            topic_words = [feature_names[i] for i in topic.argsort()[:-num_words - 1:-1]]
            topics.extend(topic_words)
        return topics

    def extract_topics(self, details):
        topics_nmf = self.topic_model_nmf(list(self.preprocess_text(details).split(" ")), num_topics=3, num_words=3)
        topics_lda = self.Lda(list(self.preprocess_text(details).split(" ")), num_topics=3, num_words=3)
        topics = [topic for topic in topics_lda if topic in topics_nmf]
        return topics

    def get_sentiment_tb(self, text):
        blob = TextBlob(text)
        sentiment_score = blob.sentiment.polarity
        normalized_score = (sentiment_score + 1) / 2
        return normalized_score

    def get_sentiment_nl(self, text):
        sid = SentimentIntensityAnalyzer()
        sentiment_scores = sid.polarity_scores(text)
        compound_score = sentiment_scores['compound']
        normalized_score = (compound_score + 1) / 2
        return normalized_score

    def get_sentiment(self, text):
        scoretb = self.get_sentiment_tb(text)
        scorenl = self.get_sentiment_nl(text)
        final_score = ((scorenl + scoretb)) / 2
        return final_score

    def createTags(self, tags):
        tagValues = []
        newTags = []
        for tag in tags:
            try: 
                tagValues.append(list(datefinder.find_dates(tag[0]))[0])
                newTags.append(tag)
            except:
                pass
        tagValues, indices, counts = np.unique(tagValues, return_index=True, return_counts=True)
        newTags = [newTags[index] for index in indices]
        newtags = []
        for i in range(len(newTags)):
            newtags.append(TimeTag(newTags[i][1], counts[i]))
        return newtags

    def addTextType(self, tags, textType):
        for tag in tags:
            tag["textType"] = textType
        return tags

    def Get_location(self, read_more, header):
        header = self.clean(header)
        header = header.split()
        text = self.sentences(self.clean(read_more))
        cities = dict()
        

        if len(self.index) <= 0:
            self.load_cities("Alldata_refined.csv")
        for i in text:
            doc = nlp(i)
            jump = 0
            for token in range(len(doc)):
                try:
                    if token < jump:
                        continue
                    jump = 0
                    if doc[token].pos_ == "PROPN":
                        self.flag = False
                        end = self.index[doc[token].text.lower()[0]]
                        if end == self.index['a']:
                            start = 0
                        else:
                            start = chr(ord(doc[token].text.lower()[0])-1)
                            start = self.index[start]
                            start += 1
                        area_count = 0
                        previous = ""
                        for areas in range(start, end):
                            words = self.Data_of_region[areas].split()
                            subtoken = token
                            checker = []
                            if fuzz.ratio(doc[subtoken].text.lower(),words[0])>=95:
                                checker.append(words[0])
                                for iterator in range(len(words)-1):
                                    if subtoken + (iterator + 1 ) < len(doc):
                                        if fuzz.ratio(doc[subtoken + iterator+1 ].text.lower(),words[iterator+1])>=70:
                                            checker.append(words[iterator+1])
                                city = ' '.join(checker)
                                if len(previous) < len(city): 
                                    area_count = len(checker)
                                    self.flag = True
                                    previous = city
                                else:
                                    city = previous
                        if self.flag:
                            match = False
                            word1 = ""
                            word2 = ""
                            if token != 0:
                                word1 = doc[token-1].text.lower()
                            jump = token + area_count
                            if jump + 1 < len(doc):
                                word2 = doc[jump+1].text.lower()
                            if word1 in header or word2 in header:
                                match = True
                            if city in cities:
                                if match:
                                    cities[city] += 3
                                else:
                                    cities[city] += 1
                            else:
                                if match:
                                    cities.__setitem__(city, 3)
                                else:
                                    cities.__setitem__(city, 1)
                except:
                    continue
        self.city = max(cities, key=cities.get, default="null")
        if self.city == 0:
            print(cities)
        df = pd.read_csv("Alldata_refined.csv")
        df = df.dropna()
        df["Locations"] = df["Locations"].apply(lambda x: x.upper())
        if df[df["Locations"] == self.city.upper()].empty:
            if self.city != "null":
                self.flag = False
                cityList = sorted(((v,k) for k,v in cities.items()), reverse=True)
                for city in cityList:
                    if df[df["Locations"] == city[1].upper()].empty == False:
                        self.city = city[1]
                        self.flag = True
                        break
            
            if self.flag == False: 
                self.city = "null"
        self.cities = cities

    def Get_Time(self, data, timeData):
        tags = []
        settings = {'PREFER_DAY_OF_MONTH': 'first', 'RELATIVE_BASE': datetime.strptime(data[6], "%Y-%m-%d")}
        headers = data[1].split("\n")
        headerParse = [search_dates(header, settings=settings) for header in headers]
        headerParse1 = search_dates(data[1], settings=settings)
        headerParse.append(headerParse1)

        summaries = data[2].split("\n")
        summaryParse = [search_dates(summary, settings=settings) for summary in summaries]
        summaryParse1 = search_dates(data[2], settings=settings)
        summaryParse.append(summaryParse1)

        details = data[3]
        lines = details.split('\n')
        del lines[-2]
        details = '\n'.join(lines)    
        detailsParse = [search_dates(detail1, settings=settings) for detail1 in lines]
        detailsParse1 = search_dates(details, settings=settings)
        detailsParse.append(detailsParse1)
        tags = headerParse + summaryParse + detailsParse
        tags = [tag for tag in tags if isinstance(tag, type(None)) == False]
        tags = [item for sublist in tags for item in sublist]

        try:
            tags = self.createTags(tags)
            tags = sorted(tags, key=lambda x: x.weight, reverse=True)
            timeData["focusTime"] = tags[0].date.date().strftime('%Y-%m-%d')
        except:
            timeData["focusTime"] = data[6]
        
        timeData["CreationDate"] = data[6]

        timeData["Header"] = dict()
        timeData["Header"]["Text"] = data[1]

        timeData['Summary'] = dict()
        timeData['Summary']["Text"] = data[2]
        
        timeData['Details'] = dict()
        timeData['Details']["Text"] = details
        
        timeData['Link'] = data[4]
        timeData['Category'] = data[5]
        return timeData

    def read(self, dataFrame):
        self.Get_location(dataFrame["Detail"], dataFrame["Header"])
        return self.city


def main():
    li = []
    jsonObject = []
    Parser = parser()
    for filename in glob.iglob(r'../Scrapper/2024/**/*.csv', recursive=True):
        path = pathlib.PurePath(filename)
        fileName = path.name[:-4]
        print(fileName)
        df = pd.read_csv(filename, index_col=None, header=0, dtype="string")
        print("Now parsing", filename)
        li.append(df)
        df = pd.concat(li, axis=0, ignore_index=True)
    
    for i in range(len(df)):
        results = dict()
        city = Parser.read(df.loc[i])
        if city != "null":
            results = Parser.Get_Time(list(df.loc[i]), results)
            results["focusLocation"] = city
            results["topics"] = Parser.extract_topics(df.iloc[i]["Detail"])
            results["sentiment"] = Parser.get_sentiment(df.iloc[i]["Header"])
            if "Pic_url" in df.iloc[i]:
                results["picture"] = df.iloc[i]["Pic_url"]
            jsonObject.append(deepcopy(results))          
        else:
            continue
    with open("results.json", "w") as file:
        json.dump(jsonObject, file, indent=4)

main()
