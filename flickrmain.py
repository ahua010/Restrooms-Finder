'''
Created on Nov 29, 2015

@author: hcde310
'''
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, urllib, urllib2, json
import jinja2

import os
import logging

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        #print statements don't work well
        #print "In MainHandler"
        logging.info("In MainHandler")
        template_values={}
        template = JINJA_ENVIRONMENT.get_template('start.html')
        self.response.write(template.render(template_values))

def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
        return None

def flickrREST(baseurl = 'https://api.flickr.com/services/rest/',
    method = 'flickr.photos.search',
    api_key = '281bf37efa94002223c0dc4d072837c4',
    format = 'json',
    params={},
    ):
    params['method'] = method
    params['api_key'] = api_key
    params['format'] = format
    if format == "json": params["nojsoncallback"]=True
    url = baseurl + "?" + urllib.urlencode(params)
    return safeGet(url)

## Building block 1 ###
# Define a function called get_photo_lst() which uses the flickr API to search
# for photos with a given tag, and add a 'fat' prefix and return a list of photos
# Use a list comprehension to generate the list.
# Hints: Use flickrREST(). 
#       flickrREST() defaults to the flickr.photos.search method, documented
#       at https://www.flickr.com/services/api/flickr.photos.search.html
#
# Inputs:
#   tag: a tag to search for
#   n: the number of search results per page (default value should be 100)
# Returns: a list of (at most) n photo dicts, or None if an error occurred
def get_photos_lst(tag, n = 100):
#     photo_ids = []
    fattag = 'fat ' + tag
#     printflickrREST(params={"tags":tag,"per_page":n})
    result = flickrREST(params={"tags":fattag,"per_page":n})
    json_result = result.read()
    photos_dict = json.loads(json_result)
#     print pretty(photos_dict)
    if photos_dict['photos']['pages'] == 0:
        return None
    return photos_dict['photos']['photo']

## Building block 2 ###
## Make a function to construct uniformed size of photos using the dictionary
# of photos passed in with this skeletal url:
# https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{o-secret}_q.jpg
# Input:  list with photos' dict
# Output: list of urls for uniformly sized photos 
#         (currently size q - large square 150x150)

def get_sized_photos(photolst):
    base = 'https://farm'
    base1 = '.staticflickr.com/'
    end = '_q.jpg'
    sized = []
    if photolst is not None:
        for photo in photolst:
            farm = str(photo['farm'])
            server = photo['server']
            p_id = photo['id']
            secret = photo['secret']        
            photo_url = base + farm + base1 + server + '/' + p_id + '_' + secret + end
            print photo_url
            sized.append(photo_url.encode('utf-8'))
        return sized
    return None

class FatAnimalHandler(webapp2.RequestHandler):
    def post(self):
        
        #URL format 
        #https://api.spotify.com/v1/search?q=code&type=track
        
        vals = {}
        vals['page_title']="Fat Animal Search Result"
        animal = self.request.get('animal')
        go = self.request.get('gobtn')
        vals['animal'] = animal 
        logging.info(animal)
        logging.info(go)
        if animal:
            # if form filled in, greet them using this data
            # get list of photos
            lst = get_photos_lst(animal)
            # get url list
            if lst is not None:
                url_lst = get_sized_photos(lst)
                logging.info(url_lst)
             
                vals['urls']= url_lst
                
                template = JINJA_ENVIRONMENT.get_template('result.html')
                self.response.write(template.render(vals))
            else:
                vals['prompt'] = "We can't find any pictures. Seems like the animal you entered isn't fat."
                template = JINJA_ENVIRONMENT.get_template('start.html')
                self.response.write(template.render(vals))
        else:
            #if not, then show the form again with a correction to the user
            vals['prompt'] = "Enter an animal to search"
            template = JINJA_ENVIRONMENT.get_template('start.html')
            self.response.write(template.render(vals))
    

# for all URLs except alt.html, use MainHandler
application = webapp2.WSGIApplication([ \
                                      ('/getfat', FatAnimalHandler),
                                      ('/.*', MainHandler)
                                      ],
                                     debug=True)
