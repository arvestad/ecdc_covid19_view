import hashlib
import wget
import os
import sys
import tempfile

data_filename='COVID-19-geographic-disbtribution-worldwide.xlsx'
ecdc_url = f'https://www.ecdc.europa.eu/sites/default/files/documents/{data_filename}'

# Memory efficient way. Looks like overkill here though... 
def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()



def main():

    md5_current = ''
    try:
        if os.path.isfile(data_filename):
            md5_current = md5(data_filename)
    except:
        print('Could not compute MD5 on local download', file=sys.stderr)
        sys.exit(1)

    try:
        tmpdir = tempfile.gettempdir()
    except:
        print('Could not figure out a temporary directory to put download in.', file=sys.stderr)
        sys.exit(2)

    try:
        filename = wget.download(ecdc_url, out=tmpdir)
        print(f'\nDownloaded datafile as {tmpdir}', file=sys.stderr)
    except Exception as e:
        print(f'Could not download {ecdc_url}', file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(3)


    md5_new = md5(filename)
    if md5_new == md5_current:
        print('File has not been updated at ECDC. Try again later.')
    else:
        try:
            os.replace(filename, data_filename) # Move from temporary directory to "standard" location.
            print(f'{data_filename} has been updated')
        except:
            print(f'Could not move {filename} to {data_filename}', file=sys.stderr)
            sys.exit(4)
            
                        
