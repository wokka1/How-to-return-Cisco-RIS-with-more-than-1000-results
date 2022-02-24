'''
This script grabs all device names from CUCM AXL, then splits them into chunks of 900, and then makes requests to RIS for each chunk in order to avoid
the 1000 record limit.

3/13/2018 Reilly Chase | rchase@rchase.com
https://github.com/reillychase/How-to-return-Cisco-RIS-with-more-than-1000-results

2/24/2022 Charles GOldsmith | wokkad@gmail.com
added pandas and export data to csv, sorting and removing duplicates
added menu for first/second run and compares

pip install pandas
pip install suds-jurko
'''
from suds.client import Client
from suds.xsd.doctor import Import
from suds.xsd.doctor import ImportDoctor
import pandas as pd
import ssl
import time
import os
from pyfiglet import Figlet

'''
Variables that might need to be changed:
    '''
USERNAME = 'administrator'
PASSWORD = ''
CUCM_PUB = ['publisher.company.com']
WSDL = 'file:///C:/Users/you/PyCharmProjects/your-proj/network-stats/AXLAPI.wsdl'

'''
    USERNAME permissions - must have read permissions to CUCM AXL/SOAP on each server 
    '''

# Do not change these without understanding the code
output_file1 = "phone_registration_first.csv"
output_file2 = "phone_registration_second.csv"
output_diff = "phone_registration_differential.csv"
f = Figlet(font='slant')
os.system("clear")

# main routine to pull in phone registration data
def main(outputfile,USERNAME,PASSWORD,CUCm_PUB,WSDL):
  registered = 0
  unregistered = 0
  rejected = 0
  unknown = 0
  partially_registered = 0
  none_status = 0
  devices_already_seen = []
  header = {"index": ["Device Name","Status","IP Address","Description","Username","Node"]}
  df = pd.DataFrame(header, columns=["device","status","ip","desc","user","node"])


  for CUCM in CUCM_PUB:
  # Get list of all phone names

    sub = CUCM
    ssl._create_default_https_context = ssl._create_unverified_context
    location = 'https://' + CUCM + ':8443/axl/'

    print ("\nAXL Query initiated")
    tns = 'http://schemas.cisco.com/ast/soap/'
    imp = Import('http://schemas.xmlsoap.org/soap/encoding/',
        'http://schemas.xmlsoap.org/soap/encoding/')
    imp.filter.add(tns)

    client = Client(WSDL,location=location,faults=False,plugins=[ImportDoctor(imp)],
        username=USERNAME,password=PASSWORD)
    resp = client.service.listPhone({'name': '%'}, returnedTags={'name': '', 'model': ''})
    phone_list = resp[1]['return'].phone
    phones_query = []
    phone_queries = []
    for phone in phone_list:
        if len(phones_query) < 1000:
            d = {}
            d["Item"] = phone.name
            phones_query.append(d)
        else:
            d = {}
            d["Item"] = phone.name
            phones_query.append(d)
            phone_queries.append(phones_query)
            phones_query = []
            time.sleep(1)
            continue
        if phone == phone_list[-1]:
            print ("AXL Query completed")
            phone_queries.append(phones_query)


    print ("Phone Queries : ",len(phone_queries))
    print ("Phone List length : ",len(phone_list))

    
    for query in phone_queries:
        ssl._create_default_https_context = ssl._create_unverified_context
        wsdl = 'https://' + CUCM + ':8443/realtimeservice/services/RisPort?wsdl'
        location = 'https://' + CUCM + ':8443/realtimeservice/services/RisPort'
        tns = 'http://schemas.cisco.com/ast/soap/'
        imp = Import('http://schemas.xmlsoap.org/soap/encoding/', 'http://schemas.xmlsoap.org/soap/encoding/')
        imp.filter.add(tns)

        client = Client(wsdl, location=location, username=USERNAME, password=PASSWORD, plugins=[ImportDoctor(imp)])
        result = client.service.SelectCmDevice('', {'SelectBy': 'Name', 'SelectItems': query})
        print ("Devices Found in this Query: ",result['SelectCmDeviceResult']['TotalDevicesFound'])
        for node in result['SelectCmDeviceResult']['CmNodes']:
            for device in node['CmDevices']:
                if device['Status']:
                    nam = str(device['Name'])
                    stat = str(device['Status'])
                    ip = str(device['IpAddress'])
                    desc = str(device['Description'])
                    user = str(device['LoginUserId'])
                    sub = str(node['Name'])

                    # add record to end of list, appending it
                    df.loc[df.shape[0]] = [nam, stat, ip, desc, user, sub]

                else:
                    print ("Received Blank status, shouldn't happen, look at data")
                    print (device)
                if device['Name'] in devices_already_seen:
                    continue
                else:
                    devices_already_seen.append(device['Name'])
                if device['Status'] == "Registered":
                    registered += 1
                if device['Status'] == "UnRegistered":
                    unregistered += 1
                if device['Status'] == ['Rejected']:
                    rejected += 1
                if device['Status'] == ['Unknown']:
                    unknown += 1
                if device['Status'] == ['PartiallyRegistered']:
                    partially_registered += 1
                if device['Status'] == '':
                    none_status += 1

  print ("Registered: " + str(registered))
  print ("Unregistered: " + str(unregistered))
  print ("Rejected: " + str(rejected))
  print ("Unknown: " + str(unknown))
  print ("Partially Registered: " + str(partially_registered))
  print ("Never Registered: " + str(none_status))


  df.sort_values(by=["device"], inplace=True)
  df.drop_duplicates(subset=["device"], keep="first", inplace=True)
  print(df)
  df.to_csv(outputfile, index=False)
  return()

def compare(first,second,diff):
# reads in both first and second csv's, compares and writes out the diff
    try:
        df1 = pd.read_csv(first)
    except:
        print("\n\nFile not found : ",first)
        print("\nExecute 1st option at main menu\n\n")
        return()
    try:
        df2 = pd.read_csv(second)
    except:
        print("\n\nFile not found : ",second)
        print("\nExecute 2nd option at main menu\n\n")
        return()


    df_diff = pd.concat([df1,df2]).drop_duplicates(keep=False)
    print(df_diff)
    df_diff.to_csv(diff, index=False)

    return()

#main menu
while True:
    print("\n\n")
    print(f.renderText("Phone Registration"))
    print("\nChoose wisely : ")
    print("""
    1 : Initial list of registered phones
    2 : Second list of registered phones (after maintenance)
    3 : Compare first and second list
    0 : Exit"""
    )
    choice = input("\nEnter your choice : ")

    if choice == '1':
        main(output_file1,USERNAME,PASSWORD,CUCM_PUB,WSDL)
    elif choice == '2':
        main(output_file2,USERNAME,PASSWORD,CUCM_PUB,WSDL)
    elif choice == '3':
        compare(output_file1,output_file2,output_diff)
    else:
        exit()

