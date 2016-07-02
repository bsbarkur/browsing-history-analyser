import sqlite3
import requests
import sys
from urllib2 import HTTPError
from bs4 import BeautifulSoup

# Output a big file (csv) or a database where documents
# are neatly separated, and the following information is available:
# 1) URL of the document, 2) title of the document.
def extract_from_url(Url_str):
    Url = Url_str[1]
    if Url.startswith('http'):
        print Url
    else:
        return

    try:
        r = requests.get(Url, allow_redirects=False)
        r.encoding = 'utf-8'
        print str(r.status_code) + ' - ' + str(r.url)

        if r.status_code is not 200:
            print str(r.url) + ' has a status code of: ' + \
                str(r.status_code) +  ' omitted from database.'

        bs_obj = BeautifulSoup(r.text)

        if hasattr(bs_obj.title, 'string') & (r.status_code == requests.codes.ok):
            try:
                title = unicode(bs_obj.title.string)
                if Url.startswith('http'):
                    if title is None:
                        title = u'Untitled'
                    for x in bs_obj.find_all(['script', 'style', 'meta', '<!--', ]):
                        x.extract()
                    body = bs_obj.get_text()
                    title_str = title
                    body_str = body.strip()

                    print str(r.status_code) + ' - ' + title + ' - Committed.'

                if title is None:
                    title = u'Untitled'
            except HTTPError as e:
                title = u'Untitled'
            except None:
                title = u'Untitled'
    # can't connect to the host
    except:
        e = sys.exc_info()[0]
        print "Error - %s" % e

if __name__ == '__main__':
    # [TODO] Set the firefox path here via config file
    
    # set the profiles path to the Firefox directory
    profiles_path = ''
    HISTORY_DB = profiles_path + "places.sqlite"

    # connect to the sqlite history database
    db = sqlite3.connect(HISTORY_DB)
    cursor = db.cursor()

    # get the list of all visited places via firefox browser
    cursor.execute("SELECT * FROM 'moz_places';")
    rows = cursor.fetchall()

    map(extract_from_url, rows)

    db.close()