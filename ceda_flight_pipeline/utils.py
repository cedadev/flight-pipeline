import os, sys
import json
import numpy as np

import logging
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.WARNING)
logstream = logging.StreamHandler()

formatter = logging.Formatter('%(levelname)s [%(name)s]: %(message)s')
logstream.setFormatter(formatter)

STAC_TEMPLATE = {
    "id": None,
    "es_id": None,
    "type" : "Feature",
    "stac_version": "1.0.0",
    "stac_extensions":[""],
    "description_path":None,
    "collection":None,
    "geometry": None,
    "properties":None,
    "assets":{},
    "links":[]
}

def jsonWrite(path, file, content):
    if not os.path.exists(path):
        os.makedirs(path)

    g = open(path + '/' + file,'w')
    g.write(json.dumps(content))
    g.close()

def jsonRead(path, file):
    g = open(path + '/' + file, 'r')
    content = json.load(g)
    g.close()
    return content

def recursiveList(obj, lv):
    for element in obj:
        for x in range(lv):
            print(' - ',end='')
        if type(element) == list:
            print('list')
            recursiveList(element, lv+1)
        else:
            print(type(element))

def recursiveConvert(obj):
    # Returns a complete numpy array from a ragged list
    out_arr = None
    is_init = False
    for element in obj:
        if element != []:
            if type(element) == list and len(element) != 2:
                coord = recursiveConvert(element)
            else:
                coord = np.array(element)

            if not is_init:
                out_arr = coord
                is_init = True
            else:
                out_arr = np.vstack((out_arr, coord))
    return out_arr

def forceSearch(obj, maxs, mins, depth):
    perform_checks = False
    if len(obj) == 2 and type(obj) == list:
        if type(obj[0]) != list:
            perform_checks = True

    if perform_checks:
        if obj[0] > maxs[0]:
            maxs[0] = obj[0]
        if obj[0] < mins[0]:
            mins[0] = obj[0]

        if obj[1] > maxs[1]:
            maxs[1] = obj[1]
        if obj[1] < mins[1]:
            mins[1] = obj[1]
        return [maxs, mins]
    else:
        for ob in obj:
            [maxs, mins] = forceSearch(ob, maxs, mins, depth+1)
    return [maxs, mins]
            
def genID():
    import random
    chars = [*'0123456789abcdefghijklmnopqrstuvwxyz']
    id = ''
    for i in range(39):
        j = random.randint(0,len(chars)-1)
        id += chars[j]

    os.system(f'grep {id} python_scripts/cache/id_history > python_scripts/cache/matches')
    with open('python_scripts/cache/matches') as f:
        content = f.readlines()
        if len(content) > 0:
            print("""
CONGRATULATIONS!!! If you are reading this message you have just computed a flight index number
that matches 39 out of the 40 characters of at least one other flight index number, the probability of which was
                  1 in 4.9 x 10^60
Meaning that unless you've broken the randomiser function you're extremely lucky today and should immediately go buy a lottery ticket!
                  
So lucky in fact that if you'd been running this program non-stop since the beginning of the universe on 10 billion computers, 
generating a flight ID every nano second, the probability of what just occurred is about as likely as you winning the EuroMillions 
                  lottery every day for 5 days
                  """)
            raise ValueError('Probabilty Factor Exceeds human tolerances, please rerun program')
        else:
            id += chars[random.randint(0, len(chars))]
    with open('python_scripts/cache/id_history', 'a') as f:
        f.write(id + '\n')
    print(id)
    return id