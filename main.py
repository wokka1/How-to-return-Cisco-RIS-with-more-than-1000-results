'''
This script grabs all device names from CUCM AXL, then splits them into chunks of 900, and then makes requests to RIS for each chunk in order to avoid
the 1000 record limit.

3/13/2018 Reilly Chase | rchase@rchase.com
pip install suds-jurko
'''
from suds.client import Client
from suds.xsd.doctor import Import
from suds.xsd.doctor import ImportDoctor
import ssl
'''
Variables that might need to be changed:
'''
USERNAME = ''
PASSWORD = ''
CUCM_LIST = ['server1', 'server2']
WSDL = 'file:///C:/Users/you/PyCharmProjects/your-proj/network-stats/AXLAPI.wsdl'

'''
USERNAME permissions - must have read permissions to CUCM AXL/SOAP on each server 
'''

registered = 0
unregistered = 0
rejected = 0
unknown = 0
partially_registered = 0
none_status = 0
devices_already_seen = []
for CUCM in CUCM_LIST:
    # Get list of all phone names

    ssl._create_default_https_context = ssl._create_unverified_context
    location = 'https://' + CUCM + ':8443/axl/'

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
        if len(phones_query) < 899:
            d = {}
            d["Item"] = phone.name
            phones_query.append(d)
            continue
        else:
            d = {}
            d["Item"] = phone.name
            phones_query.append(d)
            phone_queries.append(phones_query)
            phones_query = []
            continue
        phone_queries.append(phones_query)


    print len(phone_queries)
    print len(phone_list)

    for query in phone_queries:
        print CUCM
        ssl._create_default_https_context = ssl._create_unverified_context
        wsdl = 'https://' + CUCM + ':8443/realtimeservice/services/RisPort?wsdl'
        location = 'https://' + CUCM + ':8443/realtimeservice/services/RisPort'
        tns = 'http://schemas.cisco.com/ast/soap/'
        imp = Import('http://schemas.xmlsoap.org/soap/encoding/', 'http://schemas.xmlsoap.org/soap/encoding/')
        imp.filter.add(tns)

        client = Client(wsdl, location=location, username=USERNAME, password=PASSWORD, plugins=[ImportDoctor(imp)])
        print query
        result = client.service.SelectCmDevice('', {'SelectBy': 'Name', 'SelectItems': query})
        print result['SelectCmDeviceResult']['TotalDevicesFound']
        for node in result['SelectCmDeviceResult']['CmNodes']:
            for device in node['CmDevices']:
                if device['Status']:
                    print device['Stauts']
                else:
                    print "Blank?"
                    print device
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

            print "Registered: " + str(registered)
            print "Unregistered: " + str(unregistered)
            print "Rejected: " + str(rejected)
            print "Unknown: " + str(unknown)
            print "Partially Registered: " + str(partially_registered)
            print "Never Registered: " + str(none_status)

