import os
import json

word = ''

fileset = os.listdir('../stac-flightfinder-items')
for fname in fileset:
    with open(f'../stac-flightfinder-items/{fname}') as f:
        refs = json.load(f)
        try:
            word += refs['_id'] + '\n'
        except:
            try:
                word += refs['es_id'] + '\n'
            except:
                pass

with open('id_history','w') as f:
    f.write(word)