# How to return Cisco RIS with more than 1000 results

***This script grabs all device names from CUCM AXL, then splits them into chunks of 900, and then makes requests to RIS for each chunk in order to avoid the 1000 record limit.***

From what I've gathered, there is no pagination built into Cisco's RISport70 API. I will be writing a Python script to gather devices names from AXL, and create batched requests to get registration info on them 500 at a time. With a limit of 15 requests per minute, this will give a max of 7,500 device registrations checks in a minute.

https://developer.cisco.com/site/sxml/documents/api-reference/risport/
<soap:MaxReturnedDevices>1000</soap:MaxReturnedDevices>

https://cisco-marketing.hosted.jivesoftware.com/thread/78105

Unfortunately there is no 'paging' capability built in to the API - the application will need to manage this.  Typically the application will compile a list of phone device names (e.g.' SEP123456789012') that it is interested in getting status on - i.e. via the AXL interface.  The application then creates a <selectCmDevice> request by specifying (for example) the first 500 device names in the <SelectItems> array (this becomes a relatively large SOAP request!) - CUCM will return the status on those 500 devices (note, you may be more than 500 results back if devices if registered to multiple CUCM nodes, or less if the devices have never registered).  The application would store those results and create a second request with the next 500 device names from its compiled list, and so on...

 

Note, the behaviour of the API is exactly the same whether you specify a max returned devices of 1000 or something smaller - you can test your app's 'paging' capability by just artificially restricting the max returned devices.
