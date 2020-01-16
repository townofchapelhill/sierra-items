#  Via the Sierra API, extract fines data
#    link to the patron for classification data
#    link to the item and bib records
#    

import requests
import csv
import json
import secrets, filename_secrets

# authenticate to the Sierra API
def get_token():
    url = "https://catalog.chapelhillpubliclibrary.org/iii/sierra-api/v5/token"
    # Get the API key from secrets file
    header = {"Authorization": "Basic " + str(secrets.sierra_api), "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=header)
    if response.status_code != 200:
        print(f'get Sierra Token failed with code {response.status_code} ')
        exit(1)
    json_response = json.loads(response.text)
    return json_response["access_token"]
    
# retrieve linked patron
def get_patron_record(patronURL):
    global sierraToken
    response = requests.get(patronURL, headers={"Authorization": "Bearer " + sierraToken})
    if response.status_code != 200:
        print(f'patron retrieval failed for {patronURL} with response code:{response.status_code} ')
        pType = ""
    else:
        patronRecord = json.loads(response.text)
        pType = patronRecord["patronType"]
    return pType

# retrieve linked bib record
def get_bib_record(bibId):
    global sierraToken
    bibURL = "https://catalog.chapelhillpubliclibrary.org:443/iii/sierra-api/v5/bibs/" + bibId
    response = requests.get(bibURL, headers={"Authorization": "Bearer " + sierraToken})
    if response.status_code != 200:
        print(f'bib record retrieval failed for {bibURL} with response code:{response.status_code} ')
        materialType = ""
    else:
        bibRecord = json.loads(response.text)
        materialType = bibRecord["materialType"]["value"]
    return materialType

# retrieve linked item
def get_item_record(itemURL):
    global sierraToken
    response = requests.get(itemURL, headers={"Authorization": "Bearer " + sierraToken})
    if response.status_code != 200:
        print(f'item retrieval failed for {itemURL} with response code:{response.status_code} ')
    else:
        itemRecord = json.loads(response.text)
        if itemRecord["deleted"]:
            materialType = "deleted"
        else:
            materialType = get_bib_record(itemRecord["bibIds"][0])
            
    return materialType

# retrieve fine record and associated data, write to csv
def get_fine_records(outputFile):
    global sierraToken
    i = 0
    header = {"Authorization": "Bearer " + sierraToken}
    outputRecord = {'materialType': '', 'pType': 0, 'chargeType': '', 'itemCharge': 0.0, 'processingFee': 0.0, 'billingFee': 0.0, 'paidAmount': 0.0, 'assessedDate': ''}
    fieldNames = outputRecord.keys()
    with open(outputFile, 'w') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
      writer.writeheader()
      while True:
        fineURL = "https://catalog.chapelhillpubliclibrary.org:443/iii/sierra-api/v5/fines/?limit=200&offset=" + str(i)
        response = requests.get(fineURL, headers=header)
        if response.status_code != 200:
            print(f'fine retrieval failed for {fineURL} with response code:{response.status_code} ')
            # how do I terminate the while loop?
        else:
            finesRetrieved = json.loads(response.text)
            for fineRecord in finesRetrieved["entries"]:
                outputRecord = {}
                patronURL = fineRecord["patron"]
                if "item" in fineRecord.keys():
                    itemURL = fineRecord["item"]
                    outputRecord['materialType'] = get_item_record(itemURL)
                else:
                    outputRecord['materialType'] = "none"
                outputRecord['pType'] = get_patron_record(patronURL)
                outputRecord['chargeType'] = fineRecord["chargeType"]["display"]
                outputRecord['itemCharge'] = fineRecord["itemCharge"]
                outputRecord['processingFee'] = fineRecord["processingFee"]
                outputRecord['billingFee'] = fineRecord["billingFee"]
                outputRecord['paidAmount'] = fineRecord["paidAmount"]
                outputRecord['assessedDate'] = fineRecord["assessedDate"].split('T')[0]
                writer.writerow(outputRecord)
        i += 200
        print(f'Fine records processed: {i}')
        # refresh the access token
        sierraToken = get_token()
    csvfile.close()
    return

if __name__ == '__main__':
    # get Sierra access token
    sierraToken = get_token()
    outputFile = "data/fines.csv"
    get_fine_records(outputFile)
    exit