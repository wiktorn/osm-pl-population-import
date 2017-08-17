from urllib.request import urlopen
from urllib.parse import urlencode
import argparse

__overpassurl = "http://overpass-api.de/api/interpreter"
__overpassurl = "http://overpass.osm.rambler.ru/cgi/interpreter"

def query(qry):
    # TODO - check if the query succeeded
    url = __overpassurl + '?' + urlencode({'data': qry.replace('\t', '').replace('\n', '')})
    return urlopen(url).read().decode('utf-8')

