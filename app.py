from pickle import LIST
import requests
from bs4 import BeautifulSoup
from ast import Invert
from curses.ascii import isalpha, isdigit
from turtle import position
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
# from bs4 import BeautifulSoup
from pprint import pprint
import csv

#starting time
start_time = time.time()

# =====================
# get search object
# =====================
def clean_name(name):
    output = ''
    for letter in name:
        if letter != '*':
            output += letter
    
    return output

url = 'https://www.ohsaa.org/school-resources/school-enrollment'
# making requests instance
reqs = requests.get(url)
# using the BeautifulSoup module
soup = BeautifulSoup(reqs.text, 'html.parser')
content = soup.find(id = 'dnn_ctr2069_HtmlModule_lblContent')
table = content.find('table')
count = 0
school_names = []
cities = []
IDs = []
for row in table.find_all('tr'):
    for elem in row.find_all('td'):
        if count == 0:
            IDs.append(elem.text)
        if count == 1:
            school_names.append(clean_name(elem.text))
        if count == 2:
            cities.append(elem.text)
        count += 1
    count = 0
def get_search_object(school_names, counties, id):
    output = {
        'SI_link' : 'http://officials.myohsaa.org/Outside/Schedule?ohsaaId=' + id,
        'SD_link' : 'http://officials.myohsaa.org/Outside/Schedule/SchoolDistrict?ohsaaId=' + id,
        'AD_link' : 'http://officials.myohsaa.org/Outside/Schedule/AthleticDirector?ohsaaId=' + id,
        'SP_link' : 'http://officials.myohsaa.org/Outside/Schedule/SportsInformation?ohsaaId=' + id,
        'school name' : school_names,
        'city' : counties
    }
    return output

max_length = len(school_names)
scrap_amount = input('Enter amount of schools (enter <all> for entire list): ')
if scrap_amount == 'all':
    scrap_amount = max_length
else:
    scrap_amount = int(scrap_amount)
i = 0
search_objects = []
while i < max_length:
    search_objects.append(get_search_object(school_names[i], cities[i], IDs[i]))
    i += 1
# =====================
search_objects = search_objects[1: len(search_objects)]

def combine_list(list):
    return ' | '.join([str(item) for item in list])

def get_AD_info(soup):
    AD_names = []
    AD_emails = []
    table = soup.find('table')
    phone = table.find('span', class_ = 'athleticDepartmentSubheader').text
   
    for row in table.find_all('tr'):
        for names in row.find_all('span', class_ = 'fieldValue'):
            AD_names.append(names.text)
        for emails in row.find_all('a', class_ = 'fieldValue'):
            AD_emails.append(emails.text)
    emails = combine_list(AD_emails)
    names = combine_list(AD_names)
    output = {
        'AD phone' : clean_number(phone[7: len(phone)]),
        'AD emails' : emails,
        'AD names' : names
    }
    return output

def clean_number(number: str):
    output = ''
    place = number.find('x')
    if place != -1:
        output = number[0:place - 1]
    else:
        output = number
    return output

def clean_address(address):
    output = ''
    tmp = ''
    for elem in address:
        for letter in elem:
            if isalpha(letter) or isdigit(letter) or letter == ',':
                tmp += letter
            else:
                tmp += ' '
    output = tmp
    return output

def get_SI_info(soup):
    content = soup.find_all('div', class_ = 'displaySection')    
    textNodes = content[0].find_all(text=True)
    school_address = textNodes[2].strip()
    school_address += textNodes[3].strip()
    school_phone = ''
    principle_name = ''
    principle_email = ''
    tmp = []
    amount = 0
    for elem in content[0].find_all('span', class_ = 'fieldValue'):
        amount += 1
        tmp.append(elem.text.strip())
    # print('amount: ' + str(amount))
    if amount == 3:
        school_phone = tmp[0]
        principle_name = tmp[2]
        mailing = 'N\A'
    elif amount == 4:
        mailing = tmp[0]
        school_phone = tmp[1]
        principle_name = tmp[3]
    tmp = []
    for elem in content[0].find_all('a'):
        tmp.append(elem.text)
    try:
        principle_email = tmp[1]
    except:
        principle_email = 'N/A'
    tmp = []
    for elem in content[1].find_all('span' , class_ = 'fieldValue'):
        tmp.append(elem.text)
    county = tmp[1]
    output = {
        'school address' : clean_address(school_address),
        'mailing address' : mailing,
        'school phone' : school_phone,
        'principle name' : principle_name,
        'principle email' : principle_email,
        'county' : county
    }
    return output

def get_SP_info(soup):
    sports = []
    boys_couches = []
    boys_emails = []
    girls_couches = []
    girls_emails = []
    count = 0
    table = soup.find('table')
    for row in table.find_all('tr'):
        for elem in row.find_all('td'):
            if count == 0:
                sports.append(elem.text.strip())
            if count == 1:
                boys_couches.append(elem.text.strip())
                a_tag = elem.find('a', href=True)
                try:
                    email = a_tag['href']
                    boys_emails.append(email[7:len(email)])
                except:
                    boys_emails.append('N/A')
            if count == 2:
                girls_couches.append(elem.text.strip())
                a_tag = elem.find('a', href=True)
                try:
                    email = a_tag['href']
                    girls_emails.append(email[7:len(email)])
                except:
                    girls_emails.append('N/A')
            count += 1
        count = 0
    output = {
        'sports' : combine_list(sports),
        'boys couches' : combine_list(boys_couches),
        'boys couches emails' : combine_list(boys_emails),
        'girls couches' : combine_list(girls_couches),
        'girls couches emails' : combine_list(girls_emails)
    }
    return output
# =====================
#creating webdriver
# =====================
# s = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=s)
# driver.maximize_window()
# =====================
AD_data = []
SI_data = []
SD_data = []
SP_data = []
count = 1
for object in search_objects[0:scrap_amount]:
    # driver.get(object['AD_link'])
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    reqs = requests.get(object['AD_link'])
    soup = BeautifulSoup(reqs.text, 'html.parser')
    AD_data.append(get_AD_info(soup))
    
    # driver.get(object['SI_link'])
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    reqs = requests.get(object['SI_link'])
    soup = BeautifulSoup(reqs.text, 'html.parser')
    SI_data.append(get_SI_info(soup))

    # driver.get(object['SP_link'])
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    reqs = requests.get(object['SP_link'])
    soup = BeautifulSoup(reqs.text, 'html.parser')
    SP_data.append(get_SP_info(soup))

    print(count)
    count += 1
    print('==========')



def make_school_object(search_object, AD_data, SI_data, SP_data):
    output = {
        'link' : search_object['SI_link'],
        'school name' : search_object['school name'],
        'city' : search_object['city'],
        'county' : SI_data['county'],
        'school_address' : SI_data['school address'],
        'mailing address' : SI_data['mailing address'],
        'school phone number' : SI_data['school phone'],
        'principle name' : SI_data['principle name'],
        'principle email' : SI_data['principle email'],
        'AD number' : AD_data['AD phone'],
        'AD names' : AD_data['AD names'],
        'AD emails' : AD_data['AD emails'],
        'sports' : SP_data['sports'],
        'boys couches' : SP_data['boys couches'],
        'boys couches emails' : SP_data['boys couches emails'],
        'girls couches' : SP_data['girls couches'],
        'girls couches emails' : SP_data['girls couches emails']
    }
    return output

school_data = []
print('search objects: ' + str(len(search_objects)))
print('AD_data: ' + str(len(AD_data)))
print('SI_data: ' + str(len(SI_data)))
print('SP_data: ' + str(len(SP_data)))

# =====================
# combine lists
# =====================
for i, elem in enumerate(SP_data):
    try:
        school_data.append(make_school_object(search_objects[i], AD_data[i], SI_data[i], SP_data[i]))
    except:
        print('error out of index')
        print('place: ' + str(i))
        print('====school===')
        print(search_objects[i])
        print('=============')
# =====================

# =====================
# print list to console
# =====================
count = 0
for elem in school_data:
    print(count)
    pprint(elem)
    print('==================')
    count += 1
print('length: ' + str(len(school_data)))

# =====================
# save to csv file
# =====================
filename = input('Enter file name: ')
filename = filename + '.csv'

with open(filename, 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=school_data[0].keys())
    wr.writeheader()
    wr.writerows(school_data)
# =====================

# driver.quit()
print('Run Time: ' + str(time.time() - start_time))