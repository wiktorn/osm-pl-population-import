from bs4 import BeautifulSoup

query = """
<osm-script output="xml">
  <query into="boundryarea" type="area">
    <has-kv k="boundary" v="administrative"/>
    <has-kv k="admin_level" v="2"/>
    <has-kv k="name" v="Polska"/>
    <has-kv k="type" v="boundary"/>
  </query>
  <union>
    <query type="node">
      <area-query from="boundryarea"/>
      <has-kv k="place" modv="" v=""/>
      <has-kv k="teryt:terc" modv="" v=""/>
    </query>
  </union>
  <print mode="meta"/>
  <recurse type="down"/>
</osm-script>
"""

url = "http://overpass-api.de/api/interpreter?data=%5Bout%3Axml%5D%3Barea%5B%22boundary%22%3D%22administrative%22%5D%5B%22admin%5Flevel%22%3D%222%22%5D%5B%22name%22%3D%22Polska%22%5D%5B%22type%22%3D%22boundary%22%5D%2D%3E%2Eboundryarea%3B%28node%28area%2Eboundryarea%29%5B%22place%22%5D%5B%22teryt%3Aterc%22%5D%3B%29%3Bout%20meta%3B%3E%3B"

# relacje

query = """
<osm-script output="xml">
  <query into="boundryarea" type="area">
    <has-kv k="boundary" v="administrative"/>
    <has-kv k="admin_level" v="2"/>
    <has-kv k="name" v="Polska"/>
    <has-kv k="type" v="boundary"/>
  </query>
  <union>
    <query type="relation">
      <area-query from="boundryarea"/>
      <has-kv k="boundary" v="administrative"/>
    </query>
  </union>
  <recurse type="down-rel"/>
  <print mode="meta" order="id"/>
</osm-script>
"""

url = "http://overpass-api.de/api/interpreter?data=%5Bout%3Axml%5D%3Barea%5B%22boundary%22%3D%22administrative%22%5D%5B%22admin%5Flevel%22%3D%222%22%5D%5B%22name%22%3D%22Polska%22%5D%5B%22type%22%3D%22boundary%22%5D%2D%3E%2Eboundryarea%3B%28relation%28area%2Eboundryarea%29%5B%22boundary%22%3D%22administrative%22%5D%3B%29%3B%3E%3E%3Bout%20meta%3B"

# powiaty
query = """
<osm-script output="xml">
  <query into="boundryarea" type="area">
    <has-kv k="boundary" v="administrative"/>
    <has-kv k="admin_level" v="2"/>
    <has-kv k="name" v="Polska"/>
    <has-kv k="type" v="boundary"/>
  </query>
  <union>
    <query type="relation">
      <area-query from="boundryarea"/>
      <has-kv k="teryt:terc" modv="" v=""/>
      <has-kv k="admin_level" v="6" />
    </query>
  </union>
  <print mode="meta"/>
  <recurse type="down"/>
</osm-script>
"""

url ="http://overpass-api.de/api/interpreter?data=%5Bout%3Axml%5D%3Barea%5B%22boundary%22%3D%22administrative%22%5D%5B%22admin%5Flevel%22%3D%222%22%5D%5B%22name%22%3D%22Polska%22%5D%5B%22type%22%3D%22boundary%22%5D%2D%3E%2Eboundryarea%3B%28relation%28area%2Eboundryarea%29%5B%22teryt%3Aterc%22%5D%5B%22admin%5Flevel%22%3D%226%22%5D%3B%29%3Bout%20meta%3B%3E%3B"


def getGminy():
    ret = {}
    with open("gus - 2014-01-01.csv", encoding='cp1250') as f:
        for line in f:
            (terc, name, population) = line.strip().split(';')
            if terc and population:
                ret[terc.replace(" ", '')] = (population, name)
    return ret

def getGminyTer():
    ret = {}
    with open("gus.csv", encoding='cp1250') as f:
        for line in f:
            (name, terc, population) = line.strip().split(';')
            if terc and population:
                ret[terc.replace(" ", '')] = (population, name)
    return ret

def getPowiatyTer():
    ret = {}
    with open("gus-powiaty.csv", encoding='cp1250') as f:
        for line in f:
            try:
                (name, terc, population, rest) = line.strip().split(';',3)
                if terc and population:
                    ret[terc.replace(" ", '')] = (population, name)
            except: pass
    return ret
    


def makeFinder(key):
    return lambda tag: tag.get('k') == key

def getTag(node, tag):
    try:
        return node.find(makeFinder(tag))['v']
    except:
        return None

def getName(node):
    return getTag(node, 'name')

def setTagVal(node, tagname, val):
    child = node.find(makeFinder(tagname))
    if child:
        #print("Setting %s from %s to %s for %s" % (tagname, child['v'], val, getName(node)))
        child['v'] = val
    else:
        #print("Adding tag %s with value %s for %s" % (tagname, val, getName(node)))
        new = node.parent.parent.new_tag(name='tag', k=tagname, v=val) # brzydkie
        node.append(new)

def main():
    gminy = getPowiatyTer()
    soup = BeautifulSoup(open("powiaty.osm"))
    for place in soup.find_all('relation'):
        modify = False
        terc = place.find(makeFinder('teryt:terc'), recursive=False)
        target_popul = gminy.get(terc['v'])
        name = getName(place)

        # admin_level = 8 == cities, towns, villages, admin_level = 7 - gminy
        if target_popul and getTag(place, 'admin_level') and int(getTag(place, 'admin_level')) < 8 and getTag(place, 'population') != target_popul[0]:
            modify = True
            print("Setting value for %s: %s -> %s from: %s (terc: %s, admin_level: %s, id: %s)" % (name, getTag(place,'population'),  target_popul[0], target_popul[1], getTag(place, 'teryt:terc'), getTag(place, 'admin_level'), place['id']))
            setTagVal(place, 'population', target_popul[0])
            setTagVal(place, 'source:population', 'http://stat.gov.pl/obszary-tematyczne/ludnosc/ludnosc/ludnosc-stan-i-struktura-ludnosci-oraz-ruch-naturalny-w-przekroju-terytorialnym-w-2013-r-stan-w-dniu-31-xii,6,12.html Tabela07.xls')

        is_in = list(map(lambda x: x.extract(), place.find_all(makeFinder('is_in'))))
        if any(is_in):
            #print("Removed is_in %s for %s" % (", ".join(x['k'] for x in is_in), name,))
            modify = True

        is_in_country = any(map(lambda x: x.extract(), place.find_all(makeFinder('is_in:country'))))
        if is_in_country:
            #print("Removed is_in:country for %s" % (name,))
            modify = True
    
        addr = list(map(lambda x: x.extract(), place.find_all(lambda tag: tag.get('k', '').startswith('addr:') and tag.get('k') != 'addr:postcode' )))
        if any(addr):
            #print("Removed tags %s from %s" % (", ".join(x['k'] for x in addr), name))
            modify = True

        if modify:
            place['action'] = 'modify'

    with open("output.osm", "w+") as f:
        f.write(str(soup))

if __name__ == '__main__':
    main()
