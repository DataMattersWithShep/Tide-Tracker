import requests
from datetime import datetime, timedelta
from io import StringIO
import pandas as pd
from twilio.rest import Client
import configparser

# Enable me here and below to track time to print
# start=datetime.now()

main_config = configparser.ConfigParser()
main_config.read("config.ini")
token = main_config['LOGIN']['noaa_token']
twilio_user = str(main_config['LOGIN']['twilio_user'])
twilio_pass = str(main_config['LOGIN']['twilio_pass'])
twilio_phone_number = main_config['LOGIN']['twilio_phone_number']
phone_number_list = main_config['LOGIN']['phone_number_list'].split(',')

today = datetime.today()
yesterday = (today - timedelta(days=1))
today = today.strftime('%Y%m%d')
yesterday = yesterday.strftime('%Y%m%d')
url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=water_level&application=NOS.COOPS.TAC.WL&begin_date=" + str(yesterday) + "&end_date=" + str(today) + "&datum=MLLW&station=8571421&time_zone=GMT&units=english&format=csv"
headers = {"token":token}

r = requests.get(url, "dataset", headers = headers).text

df = pd.read_csv(StringIO(r))
df = df.iloc[::-1]

#Get last 60 measurements (every 6 mins * 10 = 1 hr)
latest_df = df.head(10)

threshold_ft = 1

latest_height = latest_df[" Water Level"].iloc[0]
max_height = max(latest_df[" Water Level"])

if (max_height >= threshold_ft):
    for pn in phone_number_list:
        client = Client(str(twilio_user), str(twilio_pass))

        message = "Tide threshold of " + str(threshold_ft) + " ft was met or exceeded in the past hour. Maximum detected height was " + str(max_height)  + " ft."
        print(message)
        client.messages.create(to=str(pn),
                            from_=twilio_phone_number,
                            body=message)
else:
  print("Maximum height was not exceeded in this check")
  
# Enable me here and below to track time to print
# print(datetime.now()-start)
