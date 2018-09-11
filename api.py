import json
import requests
import auth
import config
import os

def get_token():
  try:
    url = 'https://dat-day-z.auth0.com/oauth/token'
    data = {
      "audience": "http://ec2-34-221-7-217.us-west-2.compute.amazonaws.com/api",
      "grant_type": "client_credentials",
      "client_id": auth.client_id,
      "client_secret": auth.client_secret
    }
    headers = { 'content-type': 'application/json' }
    r = requests.post(url, data=json.dumps(data), headers=headers).json()
    token = r['access_token']
    return token
  except: 
    print('Something getting token')

real_path = os.path.dirname(os.path.realpath(__file__))
file_path = real_path + '/graphics/hiTech.png'
file_to_upload = file_path
data = { "folder" : config.s3_folder}
url = 'https://api.thepbcam.com/api/upload'
token = get_token()
headers = { "Authorization" : "Bearer %s" %token}
files = [( 'files' , open(file_to_upload, 'rb') )]
r = requests.post(url, files=files, data=data, headers=headers)
print(r.r)