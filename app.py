from pickle import LIST
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
from pprint import pprint
import csv
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
from requests.structures import CaseInsensitiveDict

def get_school_address(school_address):
    return school_address['street1'] + ', ' + school_address['city'] + ', ' + school_address['state'] + ' ' + school_address['postalCode'] 

def get_single_contact(contact):
    output = {
        'name' : contact['firstName'] + ' ' + contact['lastName'],
        'email' : contact['email'],
        'phone number' : contact['workPhone']
    }
    return output

def add_contacts(count, single_contact):
    output = {
        'contact ' + str(count) : single_contact
    }
    return output

def find_AD(contacts):
    for contact in contacts:
        if contact['contactType'] == 16:
            return contact

def get_school_data(school):

    ad = find_AD(school['contacts'])

    output = {
        'enrollment' : school['enrollmentCount'],
        'name' : school['name'], 
        'Conference' : school['primaryConference'], 
        'website' : school['websiteUrl'], 
        'twitter' : school['athleticDepartmentTwitterId'], 
        'school phone number' : school['phone'], 
        'school address' : get_school_address(school['mailingAddress']), 
        'AD first name' : ad['firstName'],
        'AD last name' : ad['lastName'],
        'AD email' : ad['email'],
        'AD phone number' : ad['workPhone'],
    }

    return output



if __name__ == "__main__":
    start_time = time.time()

    url = "https://myihsaa-prod-ams.azurewebsites.net/api/school-directory/search"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"

    data = """
    {
      "Id": 78912,
      "Customer": "Jason Sweet",
      "Quantity": 1,
      "Price": 18.00
    }
    """
    
    profile_url_start = "https://myihsaa-prod-ams.azurewebsites.net/api/schools/"
    html_url_start = 'https://www.myihsaa.net/schools/'
    url_end = "/profile"


    school_data = []

    resp = requests.post(url, headers=headers, data=data)
    api_data = resp.json()

    for count, item in enumerate(api_data['items']):
        profile_reqs = requests.get(profile_url_start + item['id'] + url_end)
        school = get_school_data(profile_reqs.json())
        school_data.append(school)
        pprint(school)
        print('\n' + str(count))
        print('=================')


    with open('indiana_school_data.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=school_data[0].keys())
        wr.writeheader()
        wr.writerows(school_data)

    print('Run Time: ' + str(time.time() - start_time))