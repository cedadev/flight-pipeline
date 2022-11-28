def jsonWrite(path, file, content):
    if not os.path.exists(path):
        os.makedirs(path)

    g = open(path + '/' + file,'w')
    g.write(json.dumps(content))
    g.close()
