import os, sys
import json

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