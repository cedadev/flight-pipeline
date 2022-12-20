import os, sys
import json
import numpy as np

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
            