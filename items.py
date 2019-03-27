# import required library for accessing Sierra with authorization
import requests
import csv
import json
import datetime
import secrets

now = datetime.datetime.now()

# function checks if a string is an ASCII (english characters only)
def is_ascii(s):
	return all(ord(c) < 128 for c in s)

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
    item_id = 100005
    
    while True:
        
        url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/items?limit=2000&deleted=false&fields=id,bibIds,status,callNumber,location,status,itemType,fixedFields&id=[" + str(item_id) + ",]"
        request = requests.get(url, headers={
                    "Authorization": "Bearer " + get_token()
                })
                
        if request.status_code != 200:
            break
                
        jfile= json.loads(request.text)
        
        for entry in jfile["entries"]:
            row = []
            try:
                callNum = entry["callNumber"]
                if is_ascii(callNum) == False:
                    for letter in callNum:
                        if is_ascii(letter) == False:
                            callNum = callNum.replace(letter, '?')
                row.append(entry["id"])
                row.append(entry["status"]["display"])
                row.append(entry["location"]["name"])
                row.append(entry["itemType"])
                row.append(entry["fixedFields"]["76"]["value"])
                row.append(entry["fixedFields"]["77"]["value"])
                row.append(entry["callNumber"])
                row.append(entry["bibIds"][0])
                writer.writerow(row)
            except KeyError:
                continue
        
        item_id = int(jfile["entries"][-1]["id"]) + 1
        
        print(item_id)

print(str(now))

# open a csv file for writing
items = open('items.csv', 'w')

# create a csvwriter object
csvwriter = csv.writer(items)

# write a header & call the create_csv function
csvwriter.writerow(['id','Status', 'Collection', 'Item Type', 'Total Checkouts', 'Total Renewals', 'Call Number', 'BibIds'])
update_items(csvwriter)

# close file
items.close()

print(str(datetime.datetime.now()))
