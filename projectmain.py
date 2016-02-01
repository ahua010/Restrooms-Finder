'''
Created on Dec 14, 2015

@author: hcde310
'''
import webapp2, urllib, urllib2, webbrowser, json
import jinja2

import os
import logging

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

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

# Pass in address, returns latitude and longitude of an area
def geocodingREST(address = '1600 Amphitheatre Parkway, Mountain View, CA'):
    params = {}
    api_key = 'AIzaSyC5GSGKfO66jFfdjBVE-QNd0c8tKYPBMQU'
    params['address'] = address
    params['key']=api_key
    baseurl = 'https://maps.googleapis.com/maps/api/geocode/json?'
    url = baseurl + urllib.urlencode(params)
    print url
    return safeGet(url)

def searchGeocode(address = '1600 Amphitheatre Parkway, Mountain View, CA'):
    result = geocodingREST(address)
    jsresult = result.read()
    dict = json.loads(jsresult)
    if dict['status'] == 'OK':
        lat =  dict['results'][0]['geometry']['location']['lat']
        lng = dict['results'][0]['geometry']['location']['lng']
        coordinates = {'lat':lat,'lng':lng}
        return coordinates
    return dict['status']
#     lat =  result_dict['results'][0]['geometry']['location']['lat']
#     lng = result_dict['results'][0]['geometry']['location']['lng']
#     coordinates = {'lat':lat,'lng':lng}
#     return coordinates

# Use latitude and longitude information to search for restrooms closeby
def refugeREST(location_dict, ada='false'):
    params={}
    params['lat'] = location_dict['lat']
    params['lng'] = location_dict['lng']
    params['ada'] = ada
    baseurl = 'http://www.refugerestrooms.org:80/api/v1/restrooms/by_location.json?'
    url = baseurl + urllib.urlencode(params)
    print url
    return safeGet(url)

def searchRestrooms(location_dict, ada='false'):
    result = refugeREST(location_dict, ada)
    jresult = result.read()
    wc_list = json.loads(jresult)
    return wc_list

# Show info from main html file
class MainHandler(webapp2.RequestHandler):
    def get(self):
        #print statements don't work well
        print "In MainHandler"
        logging.info("In MainHandler")
        template_values={}
        template = JINJA_ENVIRONMENT.get_template('wcstart.html')
        self.response.write(template.render(template_values))
        
class WCHandler(webapp2.RequestHandler):
    def post(self):
         
        #URL format 
        #https://api.spotify.com/v1/search?q=code&type=track
         
        vals = {}
        vals['page_title']="Restrooms Search Result"
        address = self.request.get('address')
        
        # Assign boolean value for accessible restrooms
        accessible = self.request.get('ada')
        if accessible == 'on':
            ada = 'true'
        else:        
            ada = 'false'
        
        go = self.request.get('gobtn')
        print "Address: " + address
        print "Accessible: " + str(ada)
        vals['address'] = address
        vals['ada'] = ada
        logging.info(address)
        logging.info(ada)
        logging.info(go)
        
        #pass address into geocoding method to get out latitude and longitude
        coordinates = searchGeocode(address)
        if type(coordinates) is not dict:
            vals['prompt'] = coordinates + ".\nPlease try again."
            template = JINJA_ENVIRONMENT.get_template('wcstart.html')
            self.response.write(template.render(vals))
        else:
            lat = coordinates['lat']
            lng = coordinates['lng']
            vals['lat'] = lat
            vals['long'] = lng
        
            # Use latitude and longitude to search for restrooms, return a list of
            # restrooms
            wc_list = searchRestrooms(coordinates, ada=ada)
            #filter restrooms within 5 miles
            
            
            vals['wc_list'] = wc_list
            vals['wc_num'] = len(wc_list)
#             print wc_list
        
            template = JINJA_ENVIRONMENT.get_template('wcmap.html')
            self.response.write(template.render(vals))

        
# for all URLs except alt.html, use MainHandler
application = webapp2.WSGIApplication([ \
                                    ('/getwc', WCHandler),
                                    ('/.*', MainHandler)
                                      ],
                                     debug=True)