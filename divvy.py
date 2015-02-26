import urllib
import cookielib
import json
import urllib2
import pprint
import os
import cgi

from lxml import etree

class Divvy(object):
    def __init__(self):
        self.cookie_jar = cookielib.LWPCookieJar()
        self.pages = 1;
    def _post_with_cookie_jar(self, url, params):
        cookie = urllib2.HTTPCookieProcessor(self.cookie_jar)
        opener = urllib2.build_opener(cookie)
        req = urllib2.Request(url, urllib.urlencode(params))
        res = opener.open(req)
        return res

    def _get_with_cookie_jar(self, url):
        cookie = urllib2.HTTPCookieProcessor(self.cookie_jar)
        opener = urllib2.build_opener(cookie)
        req = urllib2.Request(url)
        res = opener.open(req)
        return res

    def login(self, username, password):
        post_data = dict(
            subscriberUsername=username,
            subscriberPassword=password
        )
        html_fl = self._post_with_cookie_jar('https://www.divvybikes.com/login', post_data)

        parser = etree.HTMLParser()
        tree = etree.parse(html_fl, parser)

        error_box = tree.xpath('//*[@id="content"]/div/div[1]/div')

    def get_rides(self, page = 1):

        html_fl = self._get_with_cookie_jar('https://www.divvybikes.com/account/trips/' + str(page))
        parser = etree.HTMLParser()
        tree = etree.parse(html_fl, parser)

        table_rows = tree.xpath('//*[@id="content"]/div/table/tbody/tr')
        
        if(page == 1):
            pagination = tree.xpath('//*[@class="pagination"]/a')
            page_attrs = pagination[len(pagination) - 1].xpath('@data-ci-pagination-page')
            self.pages = int(page_attrs[0])
        res = []

        if table_rows and len(table_rows) == 1 and table_rows[0].xpath('td') and table_rows[0].xpath('td')[0].text.find("any bikes yet"):
            res = []
        else:
            res = []
            for row in table_rows:
                tds = row.xpath('td')

                if(tds[5].text != None):
                    duration_parts = tds[5].text.split(' ')
                    if len(duration_parts) == 1:
                        seconds = int(duration_parts[0][:-1])
                    elif len(duration_parts) == 2:
                        seconds = int(duration_parts[0][:-1])*60 + int(duration_parts[1][:-1])

                    res.append({
                        "trip_id": tds[0].text,
                        "start_station": tds[1].text,
                        "start_date": tds[2].text,
                        "end_station": tds[3].text,
                        "end_date": tds[4].text,
                        "duration": seconds
                    })
        return res

def application(req):
    d = Divvy()
    d.login('', '')

    res = {}
    rides = []

    rides = d.get_rides(1)
    for p in range(2, d.pages + 1):
        rides = rides + d.get_rides(p)

    res['rides'] = rides
    return json.dumps(res);
