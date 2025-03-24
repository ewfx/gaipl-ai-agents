import pysnow
import os
from dotenv import load_dotenv
import logging
import urllib.parse
load_dotenv()

myinstance = os.getenv("snow_instance")

password = os.getenv("password", "")
username = os.getenv("username", "")
clientId = os.getenv("clientid", "")
clientSecret = os.getenv("clientsecret", "")
        
# URL encode the credentials
encoded_password = urllib.parse.quote(password.encode('utf-8'))

encoded_username = urllib.parse.quote(username.encode('utf-8'))

# Create client object
c = pysnow.Client(instance='myinstance', user='username', password='password')

# Define a resource, here we'll use the incident table API
incident = c.resource(api_path='/table/incident')

# Query for incidents with state 1
response = incident.get(query={'state': 1}, stream=True)

# Iterate over the result and print out `sys_id` of the matching records.
for record in response.all():
    print(record['sys_id'])