# How to return Cisco RIS with more than 1000 results

***This script grabs all device names from CUCM AXL, then splits them into chunks of 900, and then makes requests to RIS for each chunk in order to avoid the 1000 record limit.***

From what I've gathered, there is no pagination built into Cisco's RISport70 API. I wrote a Python script to gather devices names from AXL, and create batched requests to get registration info on them 900 at a time. With a limit of 15 requests per minute, this will give a max of 13,500 device registrations checks in a minute.

References:
https://developer.cisco.com/site/sxml/documents/api-reference/risport/ --
"<soap:MaxReturnedDevices>1000</soap:MaxReturnedDevices>"

https://cisco-marketing.hosted.jivesoftware.com/thread/78105 --
"Unfortunately there is no 'paging' capability built in to the API..."
