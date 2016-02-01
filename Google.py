import urllib, urllib2, webbrowser, json

import os
import logging
from _dbus_bindings import String

### Utility functions you may want to use
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        print "The server couldn't fulfill the request." 
        print "Error code: ", e.code
    except urllib2.URLError, e:
        print "We failed to reach a server"
        print "Reason: ", e.reason
    return None

#### Main Assignment ##############

## Don't forget, you need to get your own api_key from Flickr, following the
#procedure in session 10 slides. Put it in the file flickr_key.py
# Then, UNCOMMENT the api_key line AND the params['api_key'] line in the function below.


def googleREST(address = '1600 Amphitheatre Parkway, Mountain View, CA'):
    params = {}
    api_key = 'AIzaSyC5GSGKfO66jFfdjBVE-QNd0c8tKYPBMQU'
    params['address'] = address
    params['key']=api_key
    baseurl = 'https://maps.googleapis.com/maps/api/geocode/json?'
    url = baseurl+urllib.urlencode(params)
    print url
    return safeGet(url)

#print googleREST()

print '\n=========== Break 1 ===========\n'

def searchGeocode(address = '1600 Amphitheatre Parkway, Mountain View, CA'):
    result = googleREST(address)
    jsresult = result.read()
    dict = json.loads(jsresult)
    print pretty(dict)
    if dict['status'] == 'OK':
        lat =  dict['results'][0]['geometry']['location']['lat']
        long = dict['results'][0]['geometry']['location']['lng']
        location = {'lat':lat,'long':long}
        return location
    return dict['status']

# print pretty(searchGeocode("nonexistent address"))
result = searchGeocode('11657 14th Ave SW, Burien, WA')
if type(result) is not dict:
    print "can't find that address"
else:
    print "result is: " + str(type(result))
    print pretty(result) 

print '\n========== Break 2 =============\n'

def refugeREST(location_dict, ada='false'):
    params={}
    params['lat'] = location_dict['lat']
    params['lng'] = location_dict['long']
    params['ada'] = ada
    baseurl = 'http://www.refugerestrooms.org:80/api/v1/restrooms/by_location.json?'
    url = baseurl + urllib.urlencode(params)
    print url
    return safeGet(url)
location_dict = searchGeocode()
# print refugeREST(location_dict)



print '\n========== Break 3 ============\n'

def searchRefuge():
    result = refugeREST(location_dict, ada='true')
    jresult = result.read()
    wc_list = json.loads(jresult)
    return wc_list

wc_list = searchRefuge()
print pretty(wc_list)
print len(wc_list)

#filter restroom within 5 miles
short_list = []
for wc in wc_list:
    if wc['distance'] < 5:
        short_list.append(wc)

print pretty(short_list)
print "there are " + str(len(short_list)) + " restrooms in 5 miles radius of your search"

def writeFile():
    f = open('myRestrooms.csv', 'w')
    f.write ('name, latitude, longitude, directions\n')
    rest = searchRefuge()
    for rs in rest:
        f.write('"%s","%s",%s,"%s"\n'%(rs['name'], rs['latitude'], rs['longitude'], rs['directions']))
    f.close()
