from flightpipe.elastic_client import resolve_link
import json

def update_moles(client, thorough=False, cache=True):
    # Get list of all ids
    # Find catalogue link for each
    # Add catalogue link or replace value in existing field.

    push_records = []

    stable, updated_link = 0, 0

    attempted = {}

    if False:
        records = client.obtain_ids()

        for x, r in enumerate(records):
            new_link = None
            if thorough or 'catalogue_link' not in r['_source']:
                dpath = r['_source']['description_path']
                if dpath not in attempted:
                    print(dpath)
                    new_link = resolve_link(r['_source']['description_path'])
                    attempted[dpath] = new_link
                else:
                    new_link = attempted[dpath]

            if new_link:
                updated_link += 1
                r['_source']['catalogue_link'] = f'https://catalogue.ceda.ac.uk/uuid/{new_link}'
                push_records.append(r['_source'])
                # Cache new record
                if cache:
                    with open(f'{x}.json','w') as f:
                        f.write(json.dumps(r))
            else:
                stable += 1
        
    if True:
        with open('1624.json') as f:
            r = json.load(f)
        push_records = [r]
        updated_link = 1

    print(f'Links updated: {updated_link}, Stable: {stable}')
    if updated_link > 0:
        proceed = input('Proceed to update? (y/n): ')
        if proceed == 'y':
            client.bulk_push(push_records)
    else:
        print('No links updated')
    

        