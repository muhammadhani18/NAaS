import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
from datetime import datetime

import psycopg2 as pg

# connection to database
conn = pg.connect(database="naas", user="postgres",
                  password="1234", host="127.0.0.1")
cursor = conn.cursor()

# read data from news_dawn table
df = pd.read_sql_query("select * from news_dawn", conn)

# Assuming 'CreationDate' is in datetime format, if not, convert it to datetime
df['CreationDate'] = pd.to_datetime(df['creation_date'], errors='coerce')

# Combine relevant text fields for analysis
df['CombinedText'] = df['header'] + ' ' + df['summary'] + ' ' + df['details']

# Define the aspect you want to analyze
aspect_to_analyze = "cabinet"

# Function to get sentiment polarity for a given text
def get_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Apply sentiment analysis to each row and create a new column 'Sentiment'
df['Sentiment'] = df['CombinedText'].apply(get_sentiment)

# Filter rows containing the aspect of interest
aspect_df = df[df['CombinedText'].str.contains(aspect_to_analyze, case=False)]

# Group by 'CreationDate' and calculate the average sentiment for each date
sentiment_timeline = aspect_df.groupby(by=df['creation_date'].dt.date)['Sentiment'].mean()

# Plot the sentiment timeline
plt.figure(figsize=(10, 6))
sentiment_timeline.plot(marker='o', linestyle='-', color='b')
plt.title(f'Sentiment Timeline for "{aspect_to_analyze}"')
plt.xlabel('Date')
plt.ylabel('Average Sentiment')
plt.grid(True)
plt.show()

