import sys
import sqlite3
from urllib2 import HTTPError
import requests
import csv
from bs4 import BeautifulSoup

# Output a big file (csv) or a database where documents
# are neatly separated, and the following information is available:
# 1) URL of the document, 2) title of the document.

drows = []

def extract_from_url(url_str):
    url = url_str[1]
    if url.startswith('https'):
        print url
    else:
        return

    try:
        req = requests.get(url, allow_redirects=False)
        req.encoding = 'utf-8'
        # print str(req.status_code) + ' - ' + str(req.url)

        if req.status_code is not 200:
            print str(req.url) + ' has a status code of: ' \
                + str(req.status_code) + ' omitted from database.'

        bs_obj = BeautifulSoup(req.text)

        if hasattr(bs_obj.title, 'string') \
                & (req.status_code == requests.codes.ok):
            try:
                title = unicode(bs_obj.title.string)
                if url.startswith('https'):
                    if title is None:
                        title = u'Untitled'
                    drows.append([title, url])
                    checks = ['script', 'style', 'meta', '<!--']
                    for chk in bs_obj.find_all(checks):
                        chk.extract()
                    body = bs_obj.get_text()
                    body_str = body.strip()


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

    with open('documents.csv', 'wb') as csvfile:
        documentswriter = csv.writer(csvfile, delimiter=',')
        documentswriter.writerow(["Title", "Url"])
        for s in drows:
            stra = unicode(s).encode("ascii", 'ignore')
            title = str(stra.split(",")[0]).strip("[")
            url = str(stra.split(",")[1]).strip("]")
            print title, url
            documentswriter.writerow([title, url])

    db.close()
