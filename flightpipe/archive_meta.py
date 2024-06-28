'''
 --- Get Archive Metadata ---
  - Extract data from archive files
  - Copied from elastic_scrapers/scraper_code
'''

import os, sys
import json

IS_WRITE=False
VERBOSE=False

class ArchiveMeta:
    def __init__(self, path, org_name='arsf'):
        self.path = path
        self.org_name = org_name

        self.metadata = {}
        
        if VERBOSE:
            print(' --- Starting archive metadata')

        if os.path.exists(self.path):
            self.getArchiveMetadata()

    def concatInfo(self, template):
        template['properties'].update(self.getArchiveMetadata())

    def rmWhiteSpace(word):
        isword = False
        new_word = ''
        for char in word:
            if isword and char != '\n':
                new_word += char
            elif char != ' ' and char != '\t':
                isword = True
                new_word += char
            else:
                pass
        return new_word

    def getContents(file):
        try:
            f=open(file,'r')
            contents = f.readlines()
            f.close()
        except:
            contents = False
            if VERBOSE:
                print(file,'not found')
        return contents

    def getReadmeData(path):
        import re
        
        files = os.listdir(path)
        
        pattern = '.*[Rr][Ee][Aa][Dd].*[Mm][Ee].*'

        extract_from = []
        principle = False
        for f in files:
            if re.search(pattern, f):
                extract_from.append(path + '/' + f)

        if len(extract_from) > 0:
            counter = 0
            while not principle and counter < len(extract_from):
                content = getContents(extract_from[counter])
                if content:
                    try:
                        PI = content[3]
                        if 'Principle' in PI:
                            principle = rmWhiteSpace(PI.split('-')[1])
                    except:
                        pass
                counter += 1
        return principle

    def getHDFVars(path):
        from pyhdf.SD import SD, SDC

        files = os.listdir(path)
        rfiles = []
        for f in files:
            if f.endswith('.hdf'):
                rfiles.append(path + '/' + f)

        variables = []
        for f in rfiles:
            try:
                f1 = SD(f,SDC.READ)
                for value in f1.datasets().keys():
                    if value == 'ATdata':
                        if 'ATM 0.42-13.5mm' not in variables:
                            variables.append('ATM 0.42-13.5mm')
                    elif value not in variables:
                        variables.append(value)
                f1.end()
            except:
                pass
        return variables

    def getNCVars(path):
        # Import netcdf python reader
        from netCDF4 import Dataset

        files = os.listdir(path)
        rfiles = [] # Files that are netCDF readable
        for f in files:
            if f.endswith('.nc'):
                rfiles.append(path + '/' + f)
        for f in rfiles:
            file = Dataset(f)
            unique_vars = {}
            for var in file.variables:
                lname = var
                sname = var.split('_')[0]
                
                try:
                    unique_vars[sname].append(lname)
                except:
                    unique_vars[sname] = [lname]

            for noint_name in unique_vars.keys():
                uvars = unique_vars[noint_name]
                if len(uvars) > 1:
                    print('{}: {}'.format(
                                        noint_name, len(uvars)
                    ))
                else:
                    print(noint_name, 1)
            x=input()

    def getFaamProcessedVars(path):
        if VERBOSE:
            print(' --- Retrieving processed nc data')
        vars = False
        if os.path.exists(path + '/core_processed'):
            vars = getNCVars(path + '/core_processed')
        elif os.path.exists(path + '/core_raw'):
            vars = ['Old']
        else:
            pass
        return vars

    def getArsfL1bVars(path):
        if VERBOSE:
            print(' --- Retrieving L1b data')
        skip_l1b = False
        vars = False
        if not skip_l1b:
            if os.path.exists(path + '/L1b'):
                vars = getHDFVars(path + '/L1b')
            elif os.path.exists(path + '/ATM'):
                vars = ['Old']
            else:
                pass
        return vars
        
    def getArchiveMetadata():
        # try to access a l1b file via jasmin connection
        # read parameters and return as metadata dict

        # l1b files - contain no useful metadata
        # 00readme - contains no useful metadata
        # catalogue_and_license - ATM/CASI search? (one method of instrument search)

        # flight plane - scrape from catalogue_and_license (check Piper)
        # variables    - l1b hdf files
        # geoinfo      - scrape from readme (vague info)
        # platform     - None
        # instrument   - scrape from catalogue_and_license (check Photographic Camera=Camera
        #                                                         ATM, CASI)

        cat_log_file = "00README_catalogue_and_licence.txt"
        readme = "00README"

        metadata = {
            'aircraft':'',
            'variables':'',
            'location':'',
            'platform':'',
            'instruments':[],
            'pi':''
        }

        ## -------------- Catalogue and License Search --------------

        if VERBOSE:
            print(' --- Retrieving Catalogue Licence data')

        catalogue = getContents(self.path + '/' + cat_log_file)
        if catalogue: ## arsf specific
            if type(catalogue) == list:
                catalogue = catalogue[1]

            if 'Photographic Camera' in catalogue:
                metadata['instruments'].append('Camera')
            is_recording = False
            buffer = ''
            for x in range(len(catalogue)):

                ## ----------- Instrument -------------
                if catalogue[x:x+3] == 'ATM':
                    metadata['instruments'].append('ATM')
                elif catalogue[x:x+4] == 'CASI':
                    metadata['instruments'].append('CASI')

                ## ----------- Flight Plane -----------
                elif catalogue[x:x+5] == 'Piper' or catalogue[x+8:x+16] == 'aircraft':
                    is_recording = True

                elif catalogue[x+1:x+7] == 'during':
                    is_recording = False
                    metadata['aircraft'] = buffer
                    buffer = ''
                elif is_recording and x == len(catalogue)-1:
                    is_recording - False
                    metadata['aircraft'] = buffer # but remove end spaces
                    buffer = ''
                else:
                    pass

                if is_recording:
                    buffer += catalogue[x]

        ## FAAM:
        ## Catalogue - BAE-146 Aircraft

        ## -------------- 00README Search --------------

        if VERBOSE:
            print(' --- Retrieving Readme data')

        readme_outer = getContents(self.path + '/' + readme)
        if readme_outer:
            try:
                metadata['location'] = readme_outer[0].replace('\n','').replace(',',' -')
            except:
                metadata['location'] = ''

        ## -------------- README Extra Search --------------
        # Try in order: path + docs, path + * + docs

        if VERBOSE:
            print(' --- Retrieving Readme Docs data')

        data = False
        dirpath1 = self.path + '/Docs/'
        if os.path.isdir(dirpath1):
            data = getReadmeData(dirpath1)
        else:
            dirpath2 = ''
            for xf in os.listdir(self.path):
                xfile = self.path + '/' + xf
                if os.path.isdir(xfile):
                    for yf in os.listdir(xfile):
                        yfile = xfile + '/' + yf
                        if 'Docs' in yfile:
                            # Location of docs folder identified
                            dirpath2 = yfile
            if dirpath2 != '':
                data = getReadmeData(dirpath2)

        if data:
            metadata['pi'] = data

        ## -------------- L1B Variable Search -------------- 

        if self.org_name == 'arsf': 
            vars = getArsfL1bVars(self.path)
        elif org_name == 'faam':
            vars = getFaamProcessedVars(self.path)
        else:
            vars = False
        
        if vars:
            metadata['variables'] = vars

        # retrieve l1b variable names

        
        return metadata

if __name__ == '__main__':
    print(__file__)
    getArchiveMetadata('/home/dwest77/Documents/cedadev')