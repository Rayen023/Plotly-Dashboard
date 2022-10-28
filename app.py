import pymongo
import pandas as pd

# connect to server on the cloud
#client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.gmxxrig.mongodb.net/?retryWrites=true&w=majority")

def _connect_mongo(username, password):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = f"mongodb+srv://{username}:{password}@cluster0.gmxxrig.mongodb.net/?retryWrites=true&w=majority"
        client = pymongo.MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)
    return client

# test the connection
# db = client.test
# print(db)
# exit()

#Go into database
db = _connect_mongo('admin','admin')['industry']

#Go into one database's collection (table)
collection = db['production']

data = pd.read_csv('AI_jobs.csv' , index_col='Id')
data.reset_index(inplace = True, drop = True)
print(data.head())

#insert into collection
#collection.insert_many(data.to_dict('records')) # records : How is data trasformed to dict

#retrieving from collection
df = pd.DataFrame.from_records(collection.find())
#print(collection.find_one())
#df.set_index('_id',inplace = True)
print(df.head())