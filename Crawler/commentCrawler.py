from turtle import up
import pymongo
import requests
from random import randint
import json

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['dataBase']
col = db['posts']
# connecting to the database 



class CommentCrawler:

    def __init__(self, configuration: str, commentURL:str, data:list,limitPerRequest='5') -> None:
        with open(configuration, "r") as configurationFile:
            self.configuration = json.load(configurationFile)
            # getting the configuration

        self.LIMIT = limitPerRequest
        # the max number of posts to fetch

        self.postdata = data

        self.URL = "https://oauth.reddit.com" + commentURL
        # getting the url of the subreddit

        self.ClientID = self.configuration["Config"]["ClientID"]
        self.SecretToken = self.configuration["Config"]["SecretToken"]
        self.UserName = self.configuration["Config"]["UserName"]
        self.Password = self.configuration["Config"]["Password"]
        # getting the authentication details

        self.auth = requests.auth.HTTPBasicAuth(self.ClientID,
                                                self.SecretToken)
        # getting the authentication token

        self.headers = {'User-Agent': 'MyBot/0.0.1'}
        # setup our header info, which gives reddit a brief description of our app

        self.data = {
            'grant_type': 'password',
            'username': self.UserName,
            'password': self.Password
        }
        # here we pass our login method (password), username, and password

        self.res = requests.post('https://www.reddit.com/api/v1/access_token',
                                 auth=self.auth,
                                 data=self.data,
                                 headers=self.headers)
        # send our request for an OAuth token

        self.TOKEN = self.res.json()['access_token']
        # convert response to JSON and pull access_token value

        # add authorization to our headers dictionary
        self.headers = {
            **self.headers,
            **{
                'Authorization': f"bearer {self.TOKEN}"
            }
        }

    def fetch(self, path:str):
        r = requests.get(self.URL, params={'limit':self.LIMIT}, headers=self.headers)
        for comment in r.json():
            if comment['data']['children'][0]['kind'] == 't1':
                dt = comment['data']['children'][0]['data']
                body = dt['body']
                author = dt['author']
                upvotes = dt['score']
                permalink = dt['permalink']
                dataPoints = {'question':self.postdata, 'body':body, 'author':author, 'upvotes':upvotes, 'permalink':permalink}
        with open(path, "w") as d:
            json.dump(dataPoints, d)

loops = 10

for i in range(loops):
    data = list(col.find())
    datapoint = dict(data[randint(0, len(data)-1)])
    filename = "Data/"+str(datapoint.pop('_id'))+".json"
    url = datapoint['permalink'].replace('https://www.reddit.com', '')
    a = CommentCrawler('config.json', url, datapoint)
    a.fetch(filename)
    print(f"{str(((i+1)/loops)*100)}% complete", end="\r")