from cgi import print_directory
import pandas as pd
import psycopg2 as pg
import json
import time

file = open(r"/home/pcn/Desktop/NAaS/Parser/results4.json")

data = json.load(file)
# print(data)
# Connect to postgres database
conn = pg.connect(database="naas", user="postgres",
                  password="1234", host="127.0.0.1", port="5432")
cursor = conn.cursor()

for row in data:

        # Check if focus location is a province, then insert with district, tehsil, union council as NULL
    cursor.execute("Select name from province where name=%s",
                   (str(row["focusLocation"]).upper(),))
    province = cursor.fetchone()
    print(f"province: {province}")
    if province:
        if "picture" in row:
            cursor.execute("Insert into NEWS_Tribune(header, summary, details, focus_time, focus_location, link, category, province, topics, location_type, picture, sentiment, creation_date) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                       (row["Header"]["Text"], row["Summary"]["Text"], row["Details"]["Text"], row["focusTime"], row["focusLocation"].upper(), row["Link"], row["Category"], province[0], row["topics"], "Province", row["picture"], row["sentiment"], row["CreationDate"]))
        else:
            cursor.execute("Insert into NEWS_Dawn(header, summary, details, focus_time, focus_location, link, category, province, topics, location_type, sentiment, creation_date) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                       (row["Header"]["Text"], row["Summary"]["Text"], row["Details"]["Text"], row["focusTime"], row["focusLocation"].upper(), row["Link"], row["Category"], province[0], row["topics"], "Province", row["sentiment"], row["CreationDate"]))
    
    # Else, Check if focus location is a district, then insert with tehsil, union council as NULL
    else:
        cursor.execute(
            "Select name, province from district where name=%s", (str(row["focusLocation"]).upper(),))
        district = cursor.fetchone()
        print(f"district: {district}")
        if district:
            if "picture" in row:
                cursor.execute("Insert into NEWS_Tribune(header, summary, details, focus_time, focus_location, link, category, province, district, topics, location_type, picture, sentiment, creation_date) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                           (row["Header"]["Text"], row["Summary"]["Text"], row["Details"]["Text"], row["focusTime"], row["focusLocation"].upper(), row["Link"], row["Category"], district[1], district[0], row["topics"], "District", row["picture"], row["sentiment"], row["CreationDate"]))
            else:
                cursor.execute("Insert into NEWS_Dawn(header, summary, details, focus_time, focus_location, link, category, province, district, topics, location_type, sentiment, creation_date) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                           (row["Header"]["Text"], row["Summary"]["Text"], row["Details"]["Text"], row["focusTime"], row["focusLocation"].upper(), row["Link"], row["Category"], district[1], district[0], row["topics"], "District", row["sentiment"], row["CreationDate"]))
           

    # Else, Check if focus location is a tehsil, then insert with union council as NULL
        else:
            cursor.execute(
                "Select name, district from tehsil where name=%s", (str(row["focusLocation"]).upper(),))
            tehsil = cursor.fetchone()
            if tehsil:
                cursor.execute(
                    "Select name, province from district where name=%s", (tehsil[1],))
                district = cursor.fetchone()
                if district:
                    if "picture" in row:
                        cursor.execute("Insert into NEWS_Tribune(header, summary, details, focus_time, focus_location, link, category, province, district, tehsil, topics, location_type, picture, sentiment, creation_date) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                                   (row["Header"]["Text"], row["Summary"]["Text"], row["Details"]["Text"], row["focusTime"], row["focusLocation"].upper(), row["Link"], row["Category"],  district[1], district[0], tehsil[0], row["topics"], "Tehsil", row["picture"], row["sentiment"], row["CreationDate"]))
                    else:
                        cursor.execute("Insert into NEWS_Dawn(header, summary, details, focus_time, focus_location, link, category, province, district, tehsil, topics, location_type, sentiment, creation_date) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                                   (row["Header"]["Text"], row["Summary"]["Text"], row["Details"]["Text"], row["focusTime"], row["focusLocation"].upper(), row["Link"], row["Category"],  district[1], district[0], tehsil[0], row["topics"], "Tehsil", row["sentiment"], row["CreationDate"]))
    conn.commit()    

print("Data inserted successfully")