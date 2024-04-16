import pandas as pd
import psycopg2 as pg
import pickle

'''
The following libraries are required to be installed in the environment to run the model
    pip install -U scikit-learn==0.23.0
    pip install numpy==1.19.5   
    pip install scipy         
    pip install pandas==1.1.5 
'''

def detecting_fake_news(var):
#retrieving the best model for prediction call
    load_model = pickle.load(open('Detection_Model.sav', 'rb'))
    prediction = load_model.predict([var])
    prob = load_model.predict_proba([var])

    return prob[0][1]

# connection to database
conn = pg.connect(database="naas", user="postgres",
                  password="1234", host="127.0.0.1")

# cursor to execute queries
cursor = conn.cursor()

# read data from news_dawn table
df = pd.read_sql_query("select * from news_dawn", conn)

# adding a new column to the dataframe named 'Prediction' for storing the result of the model with default value 0.0
df['Prediction'] = 0.0

# passing the details of each news to the detecting_fake_news function and storing the result in the Prediction column
for data in df.itertuples():
    df.at[data.Index, 'Prediction'] = detecting_fake_news(data.details)


# update the news_dawn table by adding a column named 'Prediction' and storing the result of the model in it
cursor.execute("ALTER TABLE news_dawn ADD COLUMN IF NOT EXISTS prediction float;")
conn.commit()

# update the news_dawn table by adding a column named 'Prediction' and storing the result of the model in it
for index, row in df.iterrows():
    cursor.execute("UPDATE news_dawn SET prediction = %s WHERE details = %s;", (row['Prediction'], row['details']))
conn.commit()

