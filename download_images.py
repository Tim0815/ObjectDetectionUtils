from duckduckgo_search import DDGS
import os
import argparse
from pathlib import Path
import io
import uuid
import requests
from PIL import Image
import joblib
import contextlib
from tqdm.auto import tqdm
import mimetypes
import urllib.request
import wget


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
    default='capuchin monkey',
    required=False
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
output_path = os.path.join(os.path.join(os.getcwd(), args.output_path), '')
file_limit = args.file_limit

if query is None or query.strip() == '':
    print('Error: A search query must be defined.')
else:
    create_path(output_path)
    query = query.strip()

    print('\nStarting download with following parameters:')
    print('    Query  = ' + query)
    print('    Output = ' + output_path)
    print('    Limit  = ' + file_limit + '\n')
    file_limit = int(file_limit)

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

