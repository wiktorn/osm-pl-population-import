import overpass
import osmapi
from bs4 import BeautifulSoup

def getTag(node, tag):
    n = node.find('tag', k=tag)
    if n:
        return n['v']
    else:
        return None

def updateTag(node, tag, value):
    n = node.find('tag', k=tag)
    if n:
        n['v'] = value
    else:
        n = BeautifulSoup().new_tag('tag', k=tag, v=value)
        node.append(n)

def main():
    qry = """
[out:xml]
[timeout:600]
[maxsize:1073741824]
;
area
  ["boundary"="administrative"]
  ["admin_level"="2"]
  ["name"="Polska"]
  ["type"="boundary"]
->.boundryarea;
(
  relation
    (area.boundryarea)
    (user:"WiktorN-import")
    ["boundary"="administrative"]
    ["admin_level"="8"]
    ["type"="boundary"]  
);
out meta;
"""
    ret = BeautifulSoup(overpass.query(qry), "xml")
    api = osmapi.OsmApi()

    for i in ret.find_all('relation'):
        if getTag(i, 'population') and getTag(i, 'source:population').startswith('http://stat.gov.pl/obszary-tematyczne/ludnosc/ludnosc/ludnosc-stan-i-struktura-ludnosci-oraz-ruch-naturalny-'):
            hist = api.RelationHistory(i['id'])
            version_before = hist[max(hist.keys())-1]

            if 'population' in version_before:
                updateTag(i, 'population', version_before['tag']['population'])
            else:
                i.find('tag', k='population').extract()

            if 'source:population' in version_before:
                updateTag(i, 'source:population', version_before['tag']['population'])
            else:
                i.find('tag', k='source:population').extract()

            i['action'] = 'modify'
    
    with open("result.osm", "w+") as f:
        f.write(ret.prettify())
                
if __name__ == '__main__':
    main()
