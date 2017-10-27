# import required library for accessing Sierra with authorization
import requests
import csv
import json
import datetime
import secrets

now = datetime.datetime.now()
today = now.isoformat().split('T')[0]

# function that gets the authentication token
def get_token():
    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v3/token"
    header = {"Authorization": "Basic " + str(secrets.sierra_api), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    token = json_response["access_token"]
    return token
    
# function that updates the items json file
def update_items(writer):
    # loop through each URI, incrementing by the limit of 2,000 until all item data accessed
    i = 0
    token = get_token()
    id = 100005
    
    while True:
              
        url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v3/items?limit=2000&fields=id,status&duedate=["+today+"T00:00:00Z,]&id=["+str(id)+",]"
        request = requests.get(url, headers={
                    "Authorization": "Bearer " + get_token()
                })
                
        if request.status_code != 200:
            break
                
        jfile= json.loads(request.text)
        
        for entry in jfile["entries"]:
            row = []
            try:
                # print(entry)
                row.append(entry["id"])
                row.append(entry["status"]["display"])
                row.append(entry["status"]["duedate"])
                writer.writerow(row)
            except KeyError:
                continue
        
        id = int(jfile["entries"][-1]["id"]) + 1
        
        print(id)

print(str(now))

# open a csv file for writing
items = open('//CHFS/Shared Documents/OpenData/datasets/staging/checked_out_items.csv', 'w')

# create a csvwriter object
csvwriter = csv.writer(items)

# write a header & call the create_csv function
csvwriter.writerow(['id','Status','Due Date'])
update_items(csvwriter)

# close file
items.close()

print(str(datetime.datetime.now()))
