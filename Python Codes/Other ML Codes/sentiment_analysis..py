# -*- coding: utf-8 -*-
"""sentiment_analysis2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PNlP__4u25JqX6NyzZakoFMqcYr0JQNh
"""

import csv
import pandas as pd

# This is Main function.
# Extracting streaming data from Twitter, pre-processing, and loading into MySQL
# Import related setting constants from settings.py 
import re
import tweepy
import pandas as pd
from textblob import TextBlob
# Streaming With Tweepy 
# http://docs.tweepy.org/en/v3.4.0/streaming_how_to.html#streaming-with-tweepy


# Override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):

    '''
    Tweets are known as “status updates”. So the Status class in tweepy has properties describing the tweet.
    https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object.html
    '''

    def on_status(self, status):
        '''
        Extract info from tweets
        '''
        
        if status.retweeted:
            # Avoid retweeted info, and only original tweets will be received
            return True
        # Extract attributes from each tweet
        id_str = status.id_str
        created_at = status.created_at
        text = deEmojify(status.text)    # Pre-processing the text  
        sentiment = TextBlob(text).sentiment
        polarity = sentiment.polarity
        subjectivity = sentiment.subjectivity
        user_created_at = status.user.created_at
        user_location = deEmojify(status.user.location)
        user_description = deEmojify(status.user.description)
        user_followers_count =status.user.followers_count
        longitude = None
        latitude = None
        if status.coordinates:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]
            
        retweet_count = status.retweet_count
        favorite_count = status.favorite_count
        
        print(status.text)
        print("Long: {}, Lati: {}".format(longitude, latitude))

        


        csvFile = open('covid_india.csv', 'a')
        csvWriter = csv.writer(csvFile)
        # Store all data in MySQL
        csvWriter.writerow([id_str, created_at, text, polarity,user_location])
            
    
    def on_error(self, status_code):
        '''
        Since Twitter API has rate limits, stop srcraping data as it exceed to the thresold.
        '''
        if status_code == 420:
            # return False to disconnect the stream
            return False

def clean_tweet(self, tweet): 
    ''' 
    Use sumple regex statemnents to clean tweet text by removing links and special characters
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) \
                                |(\w+:\/\/\S+)", " ", tweet).split()) 
def deEmojify(text):
    '''
    Strip all non-ASCII characters to remove emoji characters
    '''
    if text:
        return text.encode('ascii', 'ignore').decode('ascii')
    else:
        return None

API_KEY = 'NPOZDKAbob1tBMsDUFQ07gRAr'
API_SECRET_KEY = 'p0sztMBbhjzUS9ygnZk9ij5yT0lIFeOyxYZKoMBTDhL2M6Vpmy'
ACCESS_TOKEN = '1328561335-ACXCyUvKLz8xKhvBZVy6iyy5H2OS7zjkM2Vtciz'
ACCESS_TOKEN_SECRET = '2O7CvtFKit2LFrb4h0NhqBf0YKppuWyWmDCukl1yxlDIo'

auth  = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener = myStreamListener)
myStream.filter(languages=["en"], track =['india covid','india covid19','india lockdown'])

dataset=pd.read_csv("/content/covid_india.csv",header=None)

dataset

import nltk
nltk.download('wordnet')

import nltk
nltk.download('stopwords')

import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer,PorterStemmer
from nltk.corpus import stopwords
import re
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer() 

def preprocess(sentence):
  sentence=str(sentence)
  sentence = sentence.lower()
  sentence=sentence.replace('{html}',"") 
  cleanr = re.compile('<.*?>#@')
  cleantext = re.sub(cleanr, '', sentence)
  rem_url=re.sub(r'http\S+', '',cleantext)
  rem_num = re.sub('[0-9]+', '', rem_url)
  tokenizer = RegexpTokenizer(r'\w+')
  tokens = tokenizer.tokenize(rem_num)  
  filtered_words = [w for w in tokens if len(w) > 2 if not w in stopwords.words('english')]
  stem_words=[stemmer.stem(w) for w in filtered_words]
  lemma_words=[lemmatizer.lemmatize(w) for w in stem_words]
  return " ".join(filtered_words)


dataset.iloc[:,2]=dataset.iloc[:,2].map(lambda s:preprocess(s))

pip install ibm_watson

import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions

authenticator = IAMAuthenticator('6Hc3iMJs5gGstVanqPXRjaPXmPBO7rhyy4KpSp7USNl4')
natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2019-07-12',
    authenticator=authenticator
)

natural_language_understanding.set_service_url('https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/b7b78abd-f1ec-4551-89bd-1ba280052302')

angry=[]
disgust=[]
fear=[]
joy=[]
sadness=[]




for i in range(0,20):
  response = natural_language_understanding.analyze(
    text=dataset.iloc[i,2],
    features=Features(keywords=KeywordsOptions(sentiment=True,emotion=True,limit=2))).get_result()
  angry.append(response['keywords'][0]['emotion']['anger'])
  disgust.append(response['keywords'][0]['emotion']['disgust'])
  joy.append(response['keywords'][0]['emotion']['joy'])
  sadness.append(response['keywords'][0]['emotion']['sadness'])
  fear.append(response['keywords'][0]['emotion']['fear'])

disgust

import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

authenticator = IAMAuthenticator('QKtodOb0vauIw_xQaFiVb_RUbGP9JMCzriwFqToIUL5Y')
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator
)

tone_analyzer.set_service_url('https://api.eu-gb.tone-analyzer.watson.cloud.ibm.com/instances/2dcd3376-2e99-4217-8d15-544fa1b1dea7')

Tentative=[]
analytical=[]

for i in range(0,20):
  tone_analysis = tone_analyzer.tone({'text': dataset.iloc[i,2]},content_type='application/json').get_result()
  Tentative.append(tone_analysis['document_tone']['tones'][1]['score'])
  analytical.append(tone_analysis["sentences_tone"][1]['tones'][0]['score'])

created_at=[]
for i in range(0,20):
  created_at.append(dataset.iloc[i,1])

sentiment=[]
for i in range(0,20):
  sentiment.append(dataset.iloc[i,3])

Hatred_content=[]
Rising_Tension=[]
Acceptance=[]
ignorance=[]
confidence=[]
revolt=[]
for i in range(0,20):
  Hatred_content.append((3*angry[i]+3*disgust[i]-2*sentiment[i])/8)
  Rising_Tension.append((2*angry[i]+4*fear[i]+4*sadness[i]-2*sentiment[i])/12)
  Acceptance.append((5*joy[i]+3*sentiment[i])/8)
  ignorance.append((5*fear[i]-2*sentiment[i])/7)
  confidence.append((joy[i]+4*sentiment[i])/5)
  revolt.append((5*angry[i]-sentiment[i]+disgust[i])/7)

import numpy as np
import matplotlib.pyplot as plt


N = 5
A = Hatred_content[10:15]
B=Rising_Tension[10:15]
C=Acceptance[10:15]
D=ignorance[10:15]
E=confidence[10:15]
F=revolt[10:15]


Std=[0.001,0.004,0.005,0.004,0.003]
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

p1 = plt.bar(ind, A, width, yerr=Std)
p2 = plt.bar(ind, B, width,
             bottom=A, yerr=Std)
p3= plt.bar(ind, C, width,
             bottom=B, yerr=Std)
p4=plt.bar(ind,D, width,bottom=C, yerr=Std)
p5=plt.bar(ind,E, width,bottom=D, yerr=Std)
p6=plt.bar(ind,F,width,bottom=E,yerr=Std)

plt.ylabel('Scores')
plt.title('Scores by Date and Time')
plt.xticks(ind, created_at[0:5])
#plt.yticks(np.arange(-0.09, 0.09, 0.01))
plt.legend((p1[0], p2[0],p3[0],p4[0],p5[0],p6[0]), ('Hatred Content', 'Rising Tension','Acceptance Among People','Ignorance','Confidence on governance','Revolt against Government Policy'))

plt.show()



