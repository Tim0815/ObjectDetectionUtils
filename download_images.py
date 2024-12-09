"""
Beschreibung:
Dieses Skript lädt Bilder von DuckDuckGo basierend auf einem Suchbegriff herunter. 
Die Bilder werden entweder in einem angegebenen Zielverzeichnis oder im aktuellen Arbeitsverzeichnis gespeichert. 
Das Skript unterstützt sowohl Einzel- als auch parallele Downloads von Bildern und bietet eine Möglichkeit, die Anzahl der heruntergeladenen Bilder zu begrenzen.

Funktionsweise:
1. Das Skript verwendet die DuckDuckGo Search API (via `duckduckgo_search`), um eine Bildersuche basierend auf einem Suchbegriff (`query`) durchzuführen.
2. Die URLs der gefundenen Bilder werden extrahiert und die Bilder werden in einem angegebenen Zielverzeichnis gespeichert.
3. Es gibt die Möglichkeit, die maximale Anzahl der herunterzuladenden Bilder zu begrenzen.
4. Das Skript kann sowohl im Einzel- als auch im parallelen Download-Modus ausgeführt werden, wobei parallele Downloads schneller sind.

Verwendung:
1. Stelle sicher, dass die benötigten Bibliotheken installiert sind:
   - `duckduckgo_search`: Installierbar via `pip install duckduckgo_search`.
   - `joblib`, `tqdm`, `requests`, `PIL`, `mimetypes`, `urllib`, etc. (werden automatisch installiert).
2. Führe das Skript mit den folgenden Argumenten aus:
   - `-q` oder `--query`: (Erforderlich) Der Suchbegriff, nach dem die Bilder gesucht werden sollen.
   - `-o` oder `--output`: (Optional) Der Pfad, in dem die Bilder gespeichert werden. Standardmäßig wird das aktuelle Verzeichnis verwendet.
   - `-l` oder `--limit`: (Optional) Die maximale Anzahl der herunterzuladenden Bilder. Standardwert ist 50.
   
   Beispiel:
      python download_images_from_ddgs.py -q "cat" -o "/pfad/zum/verzeichnis" -l 20

Ausgabe:
- Das Skript zeigt die Anzahl der erfolgreich heruntergeladenen Bilder an und speichert sie im angegebenen Zielverzeichnis.

Hinweise:
- Es werden nur Bilder heruntergeladen, die mit der ModifyCommercially-Lizenz versehen sind.
- Das Skript verwendet parallele Downloads, um die Geschwindigkeit zu erhöhen (optional).
- Fehler werden protokolliert, aber das Skript fährt mit den verbleibenden Downloads fort.

Abhängigkeiten:
- Python 3.x
- duckduckgo_search
- joblib
- tqdm
- requests
- PIL
- mimetypes
- urllib

"""


from duckduckgo_search import DDGS
import os, sys
import argparse
from pathlib import Path
import uuid
import requests
import joblib
import contextlib
from tqdm.auto import tqdm
import mimetypes
import urllib.request
import errno
import tempfile


ERROR_INVALID_NAME = 123

def is_pathname_valid(pathname: str) -> bool:
    '''
    `True` if the passed pathname is a valid pathname for the current OS;
    `False` otherwise.
    '''
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        _, pathname = os.path.splitdrive(pathname)
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    except TypeError as exc:
        return False
    else:
        return True

def is_path_creatable(pathname: str) -> bool:
    '''
    `True` if the current user has sufficient permissions to create the passed
    pathname; `False` otherwise.
    '''
    dirname = os.path.dirname(pathname) or os.getcwd()
    return os.access(dirname, os.W_OK)

def is_path_exists_or_creatable(pathname: str) -> bool:
    '''
    `True` if the passed pathname is a valid pathname for the current OS _and_
    either currently exists or is hypothetically creatable; `False` otherwise.

    This function is guaranteed to _never_ raise exceptions.
    '''
    try:
        return is_pathname_valid(pathname) and (
            os.path.exists(pathname) or is_path_creatable(pathname))
    except OSError:
        return False

def is_path_sibling_creatable(pathname: str) -> bool:
    '''
    `True` if the current user has sufficient permissions to create **siblings**
    (i.e., arbitrary files in the parent directory) of the passed pathname;
    `False` otherwise.
    '''
    dirname = os.path.dirname(pathname) or os.getcwd()

    try:
        with tempfile.TemporaryFile(dir=dirname): pass
        return True
    except EnvironmentError:
        return False

def is_path_exists_or_creatable_portable(pathname: str) -> bool:
    '''
    `True` if the passed pathname is a valid pathname on the current OS _and_
    either currently exists or is hypothetically creatable in a cross-platform
    manner optimized for POSIX-unfriendly filesystems; `False` otherwise.

    This function is guaranteed to _never_ raise exceptions.
    '''
    try:
        return is_pathname_valid(pathname) and (
            os.path.exists(pathname) or is_path_sibling_creatable(pathname))
    except OSError:
        return False



def getExtFromMimetype(url):
    response = requests.get(url)
    content_type = response.headers['content-type']
    return mimetypes.guess_extension(content_type)



@contextlib.contextmanager
def tqdm_parallel(tqdm_object):
    """Context manager to patch joblib to display tqdm progress bar"""

    def tqdm_print_progress(self):
        if self.n_completed_tasks > tqdm_object.n:
            n_completed = self.n_completed_tasks - tqdm_object.n
            tqdm_object.update(n=n_completed)

    original_print_progress = joblib.parallel.Parallel.print_progress
    joblib.parallel.Parallel.print_progress = tqdm_print_progress

    try:
        yield tqdm_object
    finally:
        joblib.parallel.Parallel.print_progress = original_print_progress
        tqdm_object.close()



def download(urls, folder, parallel=False):
    if parallel:
        return _parallel_download_urls(urls, folder)
    else:
        return _download_urls(urls, folder)


def _download(url, folder):
        try:
            ext = getExtFromMimetype(url)
            if (ext is None or len(ext) < 2):
                ext = '.jpg'
            filename = str(uuid.uuid4().hex)
            filepath = folder + filename + ext
            while os.path.exists(filepath):
                filename = str(uuid.uuid4().hex)
                filepath = folder + filename + ext

            # Option 1:
            urllib.request.urlretrieve(url, filepath)
            return True
        
            # Option 2:
            # wget.download(url, filepath)
            # return True

            # Option 3:
            # response = requests.get(url, stream=True, timeout=5.0, allow_redirects=True)
            # with Image.open(io.BytesIO(response.content)) as im:
            #     with open(filepath, 'wb') as out_file:
            #         im.save(out_file)
            #         out_file.close()
            #         return True

            # Option 4:
            # response = requests.get(url, stream=True, timeout=5.0, allow_redirects=True)
            # f = open(filepath,'wb')
            # f.write(response.content)
            # f.close()
            # return True
        except Exception as error:
            print(error)
            return False


def _download_urls(urls, folder):
    downloaded = 0
    for url in tqdm(urls):
        if _download(url, folder):
            downloaded += 1
    return downloaded


def _parallel_download_urls(urls, folder):
    downloaded = 0
    with tqdm_parallel(tqdm(total=len(urls))):
        with joblib.Parallel(n_jobs=os.cpu_count()) as parallel:
            results = parallel(joblib.delayed(_download)(url, folder) for url in urls)
            for result in results:
                if result:
                    downloaded += 1
    return downloaded



def create_path(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)




parser = argparse.ArgumentParser()

parser.add_argument(
    '-q',
    '--query',
    dest='query',
    help='The query string.',
    default='',
    required=True
)
parser.add_argument(
    '-o',
    '--output',
    dest='output_path',
    help='Path where the images will be saved. Default is current working directory.',
    default='',
    required=False
)
parser.add_argument(
    '-l',
    '--limit',
    dest='file_limit',
    help='Max number of images to be downloaded. Default is 50.',
    default='50',
    required=False
)

args = parser.parse_args()

query = args.query
output_path = os.path.join(args.output_path, '')
if (not ':' in output_path):
    output_path = os.path.join(os.getcwd(), output_path)
file_limit = int(args.file_limit)

if query is None or query.strip() == '':
    print('Error: A search query must be defined.')
else:
    create_path(output_path)
    query = query.strip()

    print('\nStarting download with following parameters:')
    print('    Query  = ' + query)
    print('    Output = ' + output_path)
    print('    Limit  = ' + str(file_limit) + '\n')

    results = DDGS().images(
        keywords=query,
        region='wt-wt',
        safesearch='off',
        size=None,
        color=None,
        type_image='photo',
        layout=None,
        license_image='ModifyCommercially',
        max_results=file_limit,
    )
    
    urls = [result.get("image") for result in results[:file_limit]]
    count = download(urls, output_path)

    print('\n' + str(count) + ' images downloaded.')

