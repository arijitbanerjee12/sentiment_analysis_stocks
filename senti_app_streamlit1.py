# -*- coding: utf-8 -*-
"""
Created on Sun Jul  4 02:39:28 2021

@author: Arijit
"""


# -*- coding: utf-8 -*-



#import requests
#from bs4 import BeautifulSoup 

import streamlit as st
import time

import yfinance as yf
#from transformers import AutoTokenizer, AutoModelForSequenceClassification
from bs4 import BeautifulSoup
#import re
import pandas as pd
#import torch
import requests
from googlesearch import search
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords 
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer 
nltk.download(["names","stopwords","state_union","twitter_samples","movie_reviews","averaged_perceptron_tagger","vader_lexicon","punkt",'wordnet'])
from nltk.sentiment import SentimentIntensityAnalyzer
from gnews import GNews


def get_preprocessed_sent(sentence):
  #lowe sentence
  sentence = sentence.lower()
  #tokenize
  #remove Stopwords
  stop_words = set(stopwords.words('english')) 
  word_tokens = word_tokenize(sentence)  
  filtered_sentence = [w for w in word_tokens if not w in stop_words] 
  #Stemmer
  stem_words = []
  ps = PorterStemmer()
  for word in filtered_sentence:
    stem_words.append(ps.stem(word))
  #Lametization
  lem_words = []
  lemmatizer = WordNetLemmatizer()
  for word in stem_words:
    lem_words.append(lemmatizer.lemmatize(word))

  ret_sent = ""
  for i in lem_words:
    ret_sent= ret_sent+i +" "
  return(ret_sent.strip())




# def get_sentiment_score(sentence):
#   tokens = tokenizer.encode(sentence, return_tensors='pt')
#   result = model(tokens)
#   #result.logits
#   score = int(torch.argmax(result.logits))+1
#   return score

def get_sentiment_score_nltk(sentence):
  sia = SentimentIntensityAnalyzer()
  score_dict = sia.polarity_scores(sentence)
  return score_dict['compound']



def get_ticker_name(company_name):
    company = company_name.upper()
    ticker = None
    # to search
    query = company + " yahoo finance india"
    search_res =  search(query, tld="co.in", num=10, stop=10, pause=2)
    final_link = None 
    
    for j in search_res:
        #print(j)
        link = j
    
        if 'in.finance.yahoo' in link:
            split_list = link.split('/')
            #print(split_list)
            tic = split_list[-2]
            #print(tic)
            if tic[0] == company[0]:
                #print("True")
                try:
                    comp = tic.split(".")
                    ticker  =comp[0]
                    final_link = j
                except:
                    ticker  = tic 
                    final_link = j
            
    #print(ticker)
    
    if ticker == None:
      str1 = "Please make sure the company is listed in Indian Stock market " + "If yes please provide the correct spelling issue ticker = none"
      
      return str1


    if '-' in ticker:
      l = ticker.split('-')
      ticker = l[0]


    return ticker , final_link
###################### gnews            

def get_news_headlines(company , preceding_days , max_results_num):
    
    
    
    periods = str(preceding_days)+ 'd'
    google_news = GNews(language='en', country='IN', period=periods, max_results=30)
    json_resp = google_news.get_news(company)
    h = 1 
    for i in json_resp:
        #print(h)
        #print(i['title'])
        h+=1
    return json_resp

#############################
# Get the news and the ticker symbol  
def main_func(company ,ticker, days):

  print(company , ticker)


  return_dict= {}
  news = get_news_headlines(company ,days,20)
  #for i in news:
  #    print(i['title'])
  
  company_ticker, company_link = get_ticker_name(company)
  return_dict['company_ticker'] = company_ticker
  return_dict['company_link'] = company_link
  print("ticker " , company_ticker)
  company_ticker = ticker
  ############################       

  #print(news)
  #print(company_ticker,company_link)

  # get the html content from the ticker finology    
  url = 'https://ticker.finology.in/company/' + str(company_ticker)

  r = requests.get(url)
  htmlContent = r.content
  #parse the html 
  soup = BeautifulSoup(htmlContent, 'html.parser')
  #print(type(soup.title.text))
  title = soup.title.text
  #print(type(title))
  ## To avoid wrong values in the search bar

  if 'Best Stock Research and Market Analysis Platform - Ticker' in  title or news == None:
      #print("Please make sure the company is listed in Indian Stock market ")
      #print("If yes please provide the correct spelling m")
      str1 = "Please make sure the company is listed in Indian Stock market " + "If yes please provide the correct spelling " + "Issue with ticker name"
      
      return str1

      
  else:
      
      ###  Sector of the company
      
      title = soup.title.text
      title_list = title.split(",")
      print_title =  title_list[0].strip() , "and Sentiment Analysis"
      return_dict['print_title'] = print_title
      anchors = soup.find_all('p','strong' , class_ = 'compinfo sector mt-1'  )
      st = ''
      #print(anchors)
      for i in anchors:
          t = i.get_text()
          st+=t
      
      pattern = st.split(':')
      sector = pattern[-1]
      sector = sector.strip()
      print("Sector - " ,sector)           # print the sector
              
      return_dict['Sector'] = sector
      news_df =  pd.DataFrame(news)
      
      news_df = news_df[['title' , 'description','published date']]
      news_df.head(5)   
      len_df = len(news_df)
      title_df = news_df['title']
      description_df = news_df['description']
      return_dict['news_df'] = news_df
      #sentiment_list = []
      sentiment_list_nltk = []
      for i in range(len_df):

        title_s = get_preprocessed_sent(title_df[i])
        desc_s = get_preprocessed_sent(description_df[i])

        # sentiment_title = get_sentiment_score(title_s)
        # sentiment_desc = get_sentiment_score(desc_s)
        # avg_sentiment = (sentiment_title +sentiment_desc)/2

        sentiment_title_nltk = get_sentiment_score_nltk(title_s)
        sentiment_desc_nltk = get_sentiment_score_nltk(desc_s)
        avg_sentiment_nltk = (sentiment_title_nltk +sentiment_desc_nltk)/2

        #sentiment_list.append(avg_sentiment)
        sentiment_list_nltk.append(avg_sentiment_nltk)
      
      #return_dict['sentiment_list'] = sentiment_list
      return_dict['sentiment_list_nltk'] = sentiment_list_nltk

      #print(sentiment_list)
      #overall_sentiment = sum(sentiment_list)/len(sentiment_list)
      #print(overall_sentiment)
      overall_sentiment_nltk = sum(sentiment_list_nltk)/len(sentiment_list_nltk)
      #print(overall_sentiment_nltk)
      #return_dict['overall_sentiment'] = overall_sentiment
      return_dict['overall_sentiment_nltk'] = overall_sentiment_nltk

      return return_dict


def get_company_name(ticker):
    
    try:
        company_info = yf.Ticker(str(ticker + '.NS'))
        company_name = company_info.info['longName']
        return company_name
    except:
        return 'NA'
    
    



st.sidebar.write("Options")
options = st.sidebar.selectbox("Which Dashboard", ['Home','Sentiment Analysis','Fund allocation'])






#################################### Sentiment Analysis tab


if options == 'Sentiment Analysis':
    
    st.header("                       ")
    
    st.image("https://www.thepythoncode.com/media/articles/sentiment-analysis.png")
    st.header("SENTIMENT ANALYSER")
    st.subheader("Get the market sentiments for this stock")
    
    #company = st.text_input('Please enter the Company and press enter ex - Infosys')
    ticker = st.text_input('Please enter the Ticker of the company and press enter ex - INFY ')
    days = st.slider('Consider nws for these many preceding days ', min_value=1, max_value=14)
    
    a = st.button('Search')
    if a:
        
        
        st.spinner()
        with st.spinner(text='In progress'):
            #time.sleep(5)
            
            company_name = get_company_name(ticker)
            if company_name == 'NA':
                st.error("Please provide a valid Ticker name")
                st.stop()
            
            a = main_func(company_name , ticker, days)
            #print(a)
            if 'Please make sure the company' in a :
                st.error("Please provide a valid Ticker name")
                st.stop()
            ### Write code here for Sentiment analysis
            
            company_info = yf.Ticker(str(ticker + '.NS'))
            st.success('Done')
            st.balloons()
            
            
            
            logo = str(company_info.info['logo_url'])
            if logo != None:
                st.image(str(company_info.info['logo_url']))
            st.title(company_name) # Company name
            st.subheader("Sector - " + str(a['Sector']))
            st.header("   ")
            st.title(a['print_title'][0] +" " + a['print_title'][1]  ) #title
            
            st.subheader("Current Price - " + str(company_info.info['currentPrice'] ))
            st.subheader("Market Capitalization - " + str(company_info.info['marketCap'] ))
            
            st.header("Top Stories")
            news = a['news_df']
            st.table(news.iloc[0:5])
            st.title(" ")
            st.title("Sentiment Score")
            score = a['overall_sentiment_nltk']
            flag = 0
            if score >= -.13 and score <=.13:
                flag = 3 # neutral
            elif score > .13 and score <=.39:
                flag = 4 # Moderately Positive
            elif score > .39:
                flag = 5 # highly positive
            elif score < -.13 and score >= -.39:
                flag = 3 # moderately negative
            elif score < -.39 :
                flag = 1 # Highly negative
            
            
            
            
            if flag == 1:
                st.image("data:image/png;base64,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")
                st.header("Score = 1")
                st.header("Highly Negative")
            elif flag == 2:
                st.image("data:image/jpeg;base64,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")
                st.header("Score = 2")
                st.header("Moderately Negative")
            elif flag == 3:
                st.image("data:image/png;base64,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")
                st.header("Score = 3")
                st.header("Neutral")
            elif flag == 4:
                st.image("data:image/jpeg;base64,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")
                st.header("Score = 4")
                st.header("Moderately Positive")
            elif flag == 5:
                st.image("https://i.pinimg.com/originals/f9/08/52/f90852ab39e9c63042567c02848e5647.png")
                st.header("Score = 5")
                st.header("Highly Positive")
            
            
            st.write(" Thanks  ")
            st.stop()
  





################################## Home tab

if options == 'Home':
    
    st.title(""" Stocks Sentiment Analysis """)
    
    st.title(""" and Portfolio Management """)
    st.image("https://images.financialexpress.com/2021/04/STOCK_MARKET-11a.jpg") # Home Image
    
    
    st.title("About the App")
    st.write("""
            
    Hi Every one I have created this app to help people to get the sentiments of the market towards the 
    co
    
    
   
    """)
    
    
    
    with st.form("Feedback form"):
        st.title("Feedback Form")
        #slider_val = st.slider("Rating" , min_value=0, max_value=5)
        st.subheader("Ratings ")
        ratings = st.radio('', [1,2,3,4,5])
        st.subheader('Suggestions ')
        feedback = st.text_area(' ')
        checkbox_val = st.checkbox("I have used this app ")
    
       # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            
            st.image("https://i.pinimg.com/236x/65/d4/a3/65d4a33521f6f15d4b8f3b5cdeaec29d.jpg")  #thansk image
            st.write(feedback)
            st.write(ratings)

    st.write("Arijit Banerjee")



############## 
import requests
from bs4 import BeautifulSoup 


#################################### Fund Management tab    


if options == 'Fund allocation':
    st.title("FUND MANAGER ")
    st.header("    ")
    st.image("https://www.proschoolonline.com/wp-content/uploads/2017/12/10-PRACTICAL-STEPS-TO-BECOME-A-FUND-MANAGER.-Image1.jpg")
    st.title("    ")
    companies = st.text_input('Please enter the Companies you want to invest in and press enter ex - Infosys,TCS,Reliance')
    tickers = st.text_input('Please enter the Tickers of the company and press enter ex - INFY,TCS,RIL')
    amt = st.text_input("Please enter the amount you want to invest")
    st.title("    ")
    a = st.button('Calculate')
    if a:
        
        #st.write("Processing.... Please wait")
        st.balloons()
        st.spinner()
        with st.spinner(text='In progress'):
            time.sleep(5)
            
            
            
            ### Write code here for Sentiment analysis
            st.success('Done')
