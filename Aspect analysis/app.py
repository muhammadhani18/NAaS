import keyword
import json
from flask import Flask, render_template, request, jsonify
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
from datetime import datetime
import psycopg2 as pg
from flask_cors import CORS, cross_origin

app = Flask(__name__)

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Database connection
conn = pg.connect(database="naas", user="postgres",
                  password="1234", host="127.0.0.1", port="5432")

# Read data from news_dawn table
global keywords
global date

df = pd.read_sql_query("select * from news_dawn", conn)

# Assuming 'creation_date' is in datetime format, if not, convert it to datetime
df['creation_date'] = pd.to_datetime(df['creation_date'], errors='coerce')

# Combine relevant text fields for analysis
df['CombinedText'] = df['header'] + ' ' + df['summary'] + ' ' + df['details']

# Define the aspects you want to analyze (four keywords)
aspects_to_analyze = ["Voters", "PPP", "Khan", "Black"]

# Function to get sentiment polarity for a given text
def get_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Create a dictionary to store sentiment timelines for each keyword

# @app.route('/')
# def index():
#     return render_template('../Frontend/sentiment.html')
sentiment_timelines = {}

@app.route('/plotSentiment', methods=['POST'])
@cross_origin()
def plot_sentiment():
    keywords = request.json['keywords']
    date = json.loads(request.json['date'])
    start_date = datetime.strptime(date['startDate'], '%Y-%m-%d')
    end_date = datetime.strptime(date['endDate'], '%Y-%m-%d')
    print(f"KEYWORDS: {keywords}")
    for aspect in keywords:
        aspect_df = df[df['CombinedText'].str.contains(aspect, case=False)]
        if not aspect_df.empty:
            # Filter creation dates between start and end dates
            aspect_df = aspect_df[(aspect_df['creation_date'] >= start_date) & (aspect_df['creation_date'] <= end_date)]
            # Group by creation date and compute sentiment
            sentiment_timeline = aspect_df.groupby(by=aspect_df['creation_date'].dt.date)['CombinedText'].apply(lambda x: x.apply(get_sentiment).mean())
            # Sort by creation date
            sentiment_timeline = sentiment_timeline.sort_index()
            sentiment_timelines[aspect] = sentiment_timeline
            print(sentiment_timelines)

    plot_data = []
    for keyword in keywords:
        if keyword in sentiment_timelines:
            x_values = list(sentiment_timelines[keyword].index)
            y_values = list(sentiment_timelines[keyword].values)
            plot_data.append({'x': x_values, 'y': y_values, 'type': 'scatter', 'mode': 'lines+markers', 'name': keyword})
        else:
            print(f"No data available for keyword: {keyword}")
    print(f"PLOT DATA: {plot_data}")        
    return jsonify(plotData=plot_data)


if __name__ == '__main__':
    app.run(debug=True)