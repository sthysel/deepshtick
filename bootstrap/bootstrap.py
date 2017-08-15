import os
import sys
from pprint import pformat

import click
import requests

SDK_FOLDER = '1_07_07'
SDK_VERSION = '1.07.07'
SDK_DEST = './movidius/sdk/'
DOCS_DEST = './movidius/docs/'


def get_sources(folder=SDK_FOLDER, version=SDK_VERSION, sdk_destination=SDK_DEST, docs_destination=DOCS_DEST):
    sources = {
        'SDK': {
            'source': 'https://ncs-forum-uploads.s3.amazonaws.com/ncsdk/MvNC_SDK_{folder}/MvNC_SDK_{version}.tgz'.format(folder=folder, version=version),
            'dest': sdk_destination
        },
        'Release Notes': {
            'source': 'https://ncs-forum-uploads.s3.amazonaws.com/ncsdk/MvNC_SDK_{folder}/MvNC_SDK_{version}_ReleaseNotes.txt'.format(folder=folder, version=version),
            'dest': docs_destination
        },
        'API Documentation': {
            'source': 'https://ncs-forum-uploads.s3.amazonaws.com/ncsdk/MvNC_SDK_{folder}/NCS_API_{version}.pdf'.format(folder=folder, version=version),
            'dest': docs_destination
        },
        'Toolkit Documentation': {
            'source': 'https://ncs-forum-uploads.s3.amazonaws.com/ncsdk/MvNC_SDK_{folder}/NCS_Toolkit_1.07.06.pdf'.format(folder=folder),
            'dest': docs_destination
        },
        'SDK Getting Started Guide': {
            'source': 'https://ncs-forum-uploads.s3.amazonaws.com/ncsdk/MvNC_SDK_{folder}/NCS_Getting_Started_{version}.pdf'.format(folder=folder, version=version),
            'dest': docs_destination
        }
    }

    return sources


def get_filename_from_response(response, verbose=0):
    """
    :param response: The response object from requests
    :param verbose: Chattiness
    :return:
    """

    if verbose >= 2:
        click.echo(pformat(dict(**response.headers)))
        for r in response.history:
            click.echo(pformat(dict(**r.headers)))

    try:
        location = response.history[0].headers.get('Location')
        filename = location.split('/')[-1]
    except:
        raise ValueError('Could not find a filename')
    else:
        return filename


def get_filesize(response):
    try:
        return int(response.headers.get('Content-Length'))
    except ValueError:
        return -1


def remove_existing_file(cache_file_name, overwrite):
    if os.path.isfile(cache_file_name):
        if overwrite:
            os.remove(cache_file_name)
        else:
            click.secho('{} already exists. Use the --override option to re-download'.format(cache_file_name), fg='red')
            sys.exit()


def fetch(source, dest, overwrite=False):
    """ Fetch sources """

    os.makedirs(dest, exist_ok=True)

    click.echo('Contacting server...')
    response = requests.get(source, stream=True)

    fname = get_filename_from_response(response)
    file_size = get_filesize(response)
    cache_file_name = os.path.join(dest, fname)
    remove_existing_file(cache_file_name, overwrite)

    click.echo('Fetching {}'.format(cache_file_name))
    if response.status_code == 200:
        with open(cache_file_name, 'wb') as f:
            with click.progressbar(length=file_size) as bar:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
                    bar.update(len(chunk))


@click.command()
@click.option('--version', default=SDK_VERSION, help='The movidius SDK version', show_default=True)
@click.option('--folder', default=SDK_FOLDER, help='The movidius SDK folder on server', show_default=True)
@click.option('--sdk-destination', default=SDK_DEST, help='The movidius SDK target folder here', show_default=True)
@click.option('--docs-destination', default=DOCS_DEST, help='The movidius SDK documentation folder here', show_default=True)
def cli(version, folder, sdk_destination, docs_destination):
    """ bootstrap deepshtick development environment"""

    for name, info in get_sources(
            version=version,
            folder=folder,
            sdk_destination=sdk_destination,
            docs_destination=docs_destination).items():
        click.echo('Fetching {}'.format(name))
        fetch(info['source'], info['dest'])
