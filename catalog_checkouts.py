# Libraries
import os
import csv
import json
import datetime
import secrets
import jsonpickle
import requests

# I need to make these local instead of global

# Object, used to store the data of an entry so that it can be compared later on
class Items(object):
    def __init__(self, title=None, author=None, callNumber=None, type=None, icode1=None, location=None, status=None, section=None, checkouts=None, renewals=None, bibId=None, dateAdded=None, lyrcirc=None, ytdcirc=None, dueDate=None, bcode1=None, bcode2=None):
        self.title = ''
        self.author = ''
        self.callNumber = ''
        self.type = ''
        self.icode1 = ''
        self.location = ''
        self.status = ''
        self.section = ''
        self.checkouts = ''
        self.renewals = ''
        self.bibId = ''
        self.dateAdded = ''
        self.lyrcirc = ''
        self.ytdcirc = ''
        self.dueDate = ''
        self.bcode1 = ''
        self.bcode2 = ''

# Returns authentication token to be used in the GET requests
def get_token():
    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v3/token"
    header = {"Authorization": "Basic " + str(secrets.sierra_api), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    token = json_response["access_token"]
    # print(token)
    return token

# While loop that retrieves all the entries contained in Sierra's items table
def get_checkouts():
    items = []
    i = 0
    token = get_token()
    item_id = 100005

    print("Getting checkouts")

    while True:
        url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/items?limit=2000&deleted=false&fields=location,status,bibIds,itemType,callNumber,barcode,fixedFields,varFields&locations&duedate&id=[" + str(item_id) + ",]"
        request = requests.get(url, headers={
                    "Authorization": "Bearer " + get_token()
                })                       
        if request.status_code != 200:
            break

        jfile= json.loads(request.text)
        print("Number of entries: " + str(len(jfile["entries"])))

        # A new Items object is created for each entry
        # Pertinant data is stored from the JSON data
        for entry in jfile["entries"]:
            new_item = Items()
            new_item.type = entry["itemType"]
            new_item.status = entry["status"]["display"]
            new_item.section = entry["location"]["name"]
            new_item.checkouts = entry["fixedFields"]["76"]["value"]
            new_item.renewals = entry["fixedFields"]["77"]["value"]
            new_item.type = entry["fixedFields"]["61"]["display"]
            new_item.icode1 = str(entry["fixedFields"]["59"]["value"])
            new_item.ytdcirc = entry["fixedFields"]["109"]["value"]
            new_item.lyrcirc = entry["fixedFields"]["110"]["value"]
            new_item.bibId = entry["bibIds"][0]
            try:
                new_item.dueDate = entry["status"]["duedate"]
            except:
                new_item.dueDate = ''
            items.append(new_item.__dict__)
        
        item_id = int(jfile["entries"][-1]["id"]) + 1
        print("Next Item Id: " + str(item_id))
        print("Length of Items List: " + str(len(items)))

    get_titles(items)

# While loop, retrieves all the entries in Sierra's bibs table
def get_titles(items):
    titles = []
    i = 0
    token = get_token()
    item_id = 100005

    print("Getting titles")

    while True:
        url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/bibs?limit=2000&deleted=false&fields=id,available,lang,title,author,publishYear,catalogDate,country,fixedFields&id=[" + str(item_id) + ",]"
        request = requests.get(url, headers={
                    "Authorization": "Bearer " + get_token()
                })

        if request.status_code != 200:
            break

        jfile= json.loads(request.text)
        print("Number of entries: " + str(len(jfile["entries"])))

        for entry in jfile["entries"]:
            try:
                new_item = Items()
                new_item.bibId = entry["id"]
                new_item.title = entry["title"]
                new_item.author = entry["author"]
                new_item.dateAdded = entry["catalogDate"]
                new_item.bcode1 = entry["fixedFields"]["29"]["display"]
                try:
                    new_item.bcode2 = entry["fixedFields"]["30"]["display"]
                except:
                    new_item.bcode2 = ''
                titles.append(new_item.__dict__)
            except KeyError:
                continue
            
        item_id = int(jfile["entries"][-1]["id"]) + 1
        print("Next Item Id: " + str(item_id))
        print("Length of Titles List: " + str(len(titles)))

    combine_data(items, titles)

# Comparison function that checks the "bibIds" of each entry from the items and titles lists
def combine_data(items, titles):
    complete_data = []
    incomplete_data = []
    count = 0
    for title in titles:
        for item in items:
            if int(item['bibId']) == int(title['bibId']):
                count += 1
                item['title'] = title['title']
                item['author'] = title['author']
                item['dateAdded'] = title['dateAdded']
                item['bibId'] = title['bibId']
                if item["dueDate"] != '':
                    item["dueDate"] = "Checked Out"
                complete_data.append(item)
                print("Found a match: " + str(count))
                continue
        if title['bibId'] not in items:
            incomplete_data.append(title)
            continue
        continue
    print(len(complete_data))
    translate_icode(complete_data, incomplete_data)

def translate_icode(complete_data, incomplete_data):
    icode_translations = [{"74": "Adult Fiction Books"}, 
                          {"75": "Adult Non-Fiction Books"},
                          {"76": "Adult Periodicals"},
                          {"77": "Adult Audio"},
                          {"78": "Adult Video"},
                          {"79": "Adult Other Non-Print"},
                          {"84": "Children's Fiction Books"},
                          {"85": "Children's Non-Fiction Books"},
                          {"86": "Children's Periodicals"},
                          {"87": "Children's Audio"},
                          {"88": "Children's Video"},
                          {"89": "Children's Other Non-Print"},
                          {"94": "Young-Adult Fiction Books"},
                          {"95": "Young-Adult Non-Fiction Books"},
                          {"96": "Young-Adult Periodicals"},
                          {"97": "Young-Adult Audio"},
                          {"98": "NIU"},
                          {"99": "Young-Adult Other Non-Print"}]
    
    for entry in complete_data:
        try:
            comparator_1 = int(entry['icode1'])
        except:
            continue
        for indicator in icode_translations:
            comparator_2 = str(indicator.keys())[12:14]
            if comparator_1 == int(comparator_2):
                readable_icode = str(indicator.values())[14:-3]
                entry["icode1"] = readable_icode
    
    write_csv(complete_data, incomplete_data)



def write_csv(complete_data, incomplete_data):    
    with open('catalog_checkouts.csv', 'w', newline='') as file:
            if os.stat('catalog_checkouts.csv').st_size == 0:
                fieldnames = complete_data[0].keys()
                csv_writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore', delimiter=',')
                csv_writer.writeheader()

            for entry in complete_data:
                csv_writer.writerow(entry)
            
            for entry in incomplete_data:
                csv_writer.writerow(entry)

get_checkouts()



