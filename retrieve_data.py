import sys
import sqlite3
from urllib2 import HTTPError
import requests
from bs4 import BeautifulSoup

# Output a big file (csv) or a database where documents
# are neatly separated, and the following information is available:
# 1) URL of the document, 2) title of the document.


def extract_from_url(url_str):
    url = url_str[1]
    if url.startswith('http'):
        print url
    else:
        return

    try:
        req = requests.get(url, allow_redirects=False)
        req.encoding = 'utf-8'
        print str(req.status_code) + ' - ' + str(req.url)

        if req.status_code is not 200:
            print str(req.url) + ' has a status code of: ' \
                + str(req.status_code) + ' omitted from database.'

        bs_obj = BeautifulSoup(req.text)

        if hasattr(bs_obj.title, 'string') \
                & (req.status_code == requests.codes.ok):
            try:
                title = unicode(bs_obj.title.string)
                if url.startswith('http'):
                    if title is None:
                        title = u'Untitled'
                    checks = ['script', 'style', 'meta', '<!--']
                    for chk in bs_obj.find_all(checks):
                        chk.extract()
                    body = bs_obj.get_text()
                    body_str = body.strip()

                    print str(req.status_code) + ' - ' + title + ' - Committed.'

                if title is None:
                    title = u'Untitled'
            except HTTPError as error:
                title = u'Untitled'
            except None:
                title = u'Untitled'
    # can't connect to the host
    except:
        error = sys.exc_info()[0]
        print "Error - %s" % error

if __name__ == '__main__':
    # [TODO] Set the firefox path here via config file

    # set the profiles path to the Firefox directory
    PROFILES_PATH = ''
    HISTORY_DB = PROFILES_PATH + "places.sqlite"

    # connect to the sqlite history database
    db = sqlite3.connect(HISTORY_DB)
    cursor = db.cursor()

    # get the list of all visited places via firefox browser
    cursor.execute("SELECT * FROM 'moz_places';")
    rows = cursor.fetchall()

    map(extract_from_url, rows)

    db.close()
