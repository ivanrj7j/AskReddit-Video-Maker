from random import randint, random
import requests
import json
import pymongo
# importing needed modules 


def readableNumber(number:int)->str:
    if number < 1000:
        return str(number)
    elif number < 1000000:
        return str(round(number/1000, 1))+'k'
    elif number < 1000000000:
        return str(round(number/1000000, 1))+'M'
        



class Crawler:
    SortByOptions = [
        "hot/", "new/", "top/?t=all", "top/?t=year", "top/?t=month",
        "top/?t=week", "top/?t=day", "top/?t=hour"
    ]

    # options to sort the subreddit

    def __init__(self, configuration: str, limitPerRequest='100') -> None:
        with open(configuration, "r") as configurationFile:
            self.configuration = json.load(configurationFile)
            # getting the configuration

        self.LIMIT = limitPerRequest
        # the max number of posts to fetch

        self.Subreddit = self.configuration["Config"]["Subreddit"]
        self.SortBy = self.SortByOptions[self.configuration["Config"]
                                         ["SortBy"]]
        self.URL = "https://oauth.reddit.com/r/" + self.Subreddit + self.SortBy
        # getting the url of the subreddit

        self.ClientID = self.configuration["Config"]["ClientID"]
        self.SecretToken = self.configuration["Config"]["SecretToken"]
        self.UserName = self.configuration["Config"]["UserName"]
        self.Password = self.configuration["Config"]["Password"]
        # getting the authentication details

        self.OutputFolder = self.configuration["Config"]["DestinationFolder"]
        # getting the location of the output folder

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

    def crawlPosts(self, db):
        """
        Crawls over the subreddit 
        """

        meh = requests.get(self.URL,
                           headers=self.headers,
                           params={'limit': self.LIMIT})
        # sending the request
        self.fetchPosts(meh, db)

    def fetchPosts(self, r, col):
        try:
            for post in r.json()['data']['children']:
                if not post['data']['over_18']:
                    title = post['data']['title']
                    permalink = 'https://www.reddit.com'+post['data']['permalink']
                    author = post['data']["author"]
                    votes = readableNumber(int(post['data']['ups']*post['data']['upvote_ratio']))
                    upvotes = (int(post['data']['ups']*post['data']['upvote_ratio']))
                    comments = readableNumber(post['data']["num_comments"])
                    data = {'title':title, 'permalink':permalink, 'author':author, 'votes':votes, 'comments':comments, 'upvotes':upvotes}
                    x = col.find_one({'permalink':permalink})
                    if not x:
                        col.insert_one(data)
            last = 't3_'+post['data']['id']
            print("LOOP COMPLETE")
            meh = requests.get(self.URL,
                            headers=self.headers,
                            params={'limit': self.LIMIT, 'after':last})
            self.fetchPosts(meh, col)
        except:
            print(["EXITING"])

    def prepareRequest(self, after=None, limit='100', url=None):
        if not url:
            if after:
                meh = requests.get(self.URL,
                            headers=self.headers,
                            params={'limit': limit, 'after':after})
            else:
                meh = requests.get(self.URL,
                            headers=self.headers,
                            params={'limit': limit})
            # sending the request
        else:
            if after:
                meh = requests.get(url,
                            headers=self.headers,
                            params={'limit': limit, 'after':after})
            else:
                meh = requests.get(url,
                            headers=self.headers,
                            params={'limit': limit})

        return meh

    def getCollectedData(self, db):
        client = pymongo.MongoClient(db)
        db = client['dataBase']
        col = db['data'].find()
        return col


