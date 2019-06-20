# Libraries
import os
import csv
import json
import datetime
import secrets
import jsonpickle
import requests
from datetime import datetime

# !!! CURRENTLY TAKES OVER 20 HOURS TO COMPLETE RUN TIME !!!
# Working on cutting that down

# Future Devs: check out the Sierra docs for help: https://sandbox.iii.com/iii/sierra-api/swagger/index.html#!/items

# Object, used to store the data of an entry so that it can be compared later on
class Items(object):
    def __init__(self, title=None, author=None, callNumber=None, type=None, icode1=None, location=None, status=None, checkouts=None, renewals=None, bibId=None, dateAdded=None, lyrcirc=None, ytdcirc=None, dueDate=None, bcode1=None, bcode2=None, found=None):
        self.title = ''
        self.author = ''
        self.callNumber = ''
        self.type = ''
        self.icode1 = ''
        self.location = ''
        self.status = ''
        self.checkouts = ''
        self.renewals = ''
        self.bibId = ''
        self.dateAdded = ''
        self.lyrcirc = ''
        self.ytdcirc = ''
        self.dueDate = ''
        self.bcode1 = ''
        self.bcode2 = ''
        self.found = bool

# Returns authentication token to be used in the GET requests
def get_token():
    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v3/token"
    header = {"Authorization": "Basic " + str(secrets.sierra_api), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    json_response = json.loads(response.text)
    token = json_response["access_token"]
    return token

# While loop that retrieves all the entries contained in Sierra's items table
def get_checkouts():
    items = []
    i = 0
    token = get_token()
    item_id = 100005
    startTime = datetime.now()

    print("Getting checkouts")

    # Loop through items until query fails when all entries have been retrieved, pull 2000 records at a time, store them in "items" list
    while True:
        url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/items?limit=2000&deleted=false&fields=location,status,bibIds,itemType,callNumber,barcode,fixedFields,varFields&locations&id=[" + str(item_id) + ",]"
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
            new_item.location = entry["location"]["name"]
            new_item.checkouts = entry["fixedFields"]["76"]["value"]
            new_item.renewals = entry["fixedFields"]["77"]["value"]
            new_item.type = entry["fixedFields"]["61"]["display"]
            new_item.icode1 = str(entry["fixedFields"]["59"]["value"])
            new_item.ytdcirc = entry["fixedFields"]["109"]["value"]
            new_item.lyrcirc = entry["fixedFields"]["110"]["value"]
            new_item.bibId = entry["bibIds"][0]
            new_item.found = False
            try:
                new_item.barcode = entry["barcode"]
                new_item.dueDate = entry["status"]["duedate"]
            except:
                pass
            items.append(new_item.__dict__)
        
        item_id = int(jfile["entries"][-1]["id"]) + 1
        print("Next Item Id: " + str(item_id))
        print("Length of Items List: " + str(len(items)))

    get_titles(items, startTime)

# While loop, retrieves all the entries in Sierra's bibs table
def get_titles(items, startTime):
    titles = []
    i = 0
    token = get_token()
    item_id = 100005

    print("Getting titles")

    # Loop through database until query fails when all entries have been retrieved, pull 2000 records at a time, store them in "titles" list
    while True:
        url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/bibs?limit=2000&deleted=false&suppressed=false&fields=id,available,lang,title,author,publishYear,catalogDate,country,fixedFields,varFields&id=[" + str(item_id) + ",]"
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
                for field in entry["varFields"]:
                    if field['fieldTag'] == "c":
                        try:
                            new_item.callNumber = field["subfields"][0]['content']
                        except:
                            pass
                # try:
                new_item.bcode2 = entry["fixedFields"]["30"]["value"].strip()
                # except:
                    # new_item.bcode2 = ''
                titles.append(new_item.__dict__)
            except KeyError:
                continue
            
        item_id = int(jfile["entries"][-1]["id"]) + 1
        print("Next Item Id: " + str(item_id))
        print("Length of Titles List: " + str(len(titles)))

    combine_data(items, titles, startTime)


# Comparison function that checks the "bibIds" of each entry from the items and titles lists
def combine_data(items, titles, startTime):
    complete_data = []
    count = 0
    for item in items:
        if item['found'] == True:
            continue
        for title in titles:
            # if title['found'] == True:
            #     continue
            if int(item['bibId']) == int(title['bibId']):
                count += 1
                item['title'] = title['title']
                item['author'] = title['author']
                item['dateAdded'] = title['dateAdded']
                item['bibId'] = title['bibId']
                item['bcode1'] = title['bcode1']
                item['bcode2'] = title['bcode2']
                item['callNumber'] = title['callNumber']
                item['found'] = True
                title['found'] = True
                complete_data.append(item)
                continue
    print(len(complete_data))
    translate_icode(complete_data, startTime)

# This function translates the icode1 and bcode2 values retrieved from Sierra into plain English
def translate_icode(complete_data, startTime):

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

    bcode_translations = [{'-': 'Books'},
                          {'b': 'Book Kit'},
                          {'d': 'DVD'},
                          {'f': 'Equipment'},
                          {'h': 'Newspapers'},
                          {'k': 'Kit'},
                          {'m': 'Music CD'},
                          {'p': 'Magazine or Journal'},
                          {'v': 'E-Videos'},
                          {'a': 'E-Audio Books'},
                          {'c': 'Books on CD'},
                          {'e': 'E-Books'},
                          {'g': 'Graphic Novels'},
                          {'i': 'Online Periodical'},
                          {'l': 'Large Print'},
                          {'n': 'E-Music'},
                          {'r': 'Web Resource'}]

    # comparison loops
    for entry in complete_data:
        try:
            comparator_1 = int(entry['icode1'])
            comparator_3 = entry['bcode2']
        except:
            continue

        for indicator in icode_translations:
            comparator_2 = str(indicator.keys())[12:14]
            if comparator_1 == int(comparator_2):
                readable_icode = str(indicator.values())[14:-3]
                entry["icode1"] = readable_icode
        
        for indicator2 in bcode_translations:
            comparator_4 = str(indicator2.keys())[12:13]
            if comparator_3 == comparator_4:
                readable_bcode = str(indicator2.values())[14:-3]
                entry["bcode"] = readable_bcode
    
    write_csv(complete_data, startTime)



def write_csv(complete_data, startTime):    
    with open('catalog_checkouts.csv', 'w', newline='') as file:
            if os.stat('catalog_checkouts.csv').st_size == 0:
                fieldnames = complete_data[0].keys()
                csv_writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore', delimiter=',')
                csv_writer.writeheader()

            for entry in complete_data:
                csv_writer.writerow(entry)

    print(datetime.now() - startTime)


get_checkouts()



