import os
import sys
import wget

import click

SDK_FOLDER = '01_07_07'
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


def fetch(source_url, dest_directory, dest_filename, overwrite=False):
    """ Fetch sources """

    click.echo('Fetching {}'.format(source_url))
    os.makedirs(dest_directory, exist_ok=True)

    _file_name = os.path.join(dest_directory, dest_filename)
    remove_existing_file(_file_name, overwrite)
    wget.download(source_url, _file_name)


@click.command()
@click.option('--sdk-version', default=SDK_VERSION, help='The movidius SDK version', show_default=True)
@click.option('--folder', default=SDK_FOLDER, help='The movidius SDK folder on server', show_default=True)
@click.option('--sdk-destination', default=SDK_DEST, help='The movidius SDK target folder here', show_default=True)
@click.option('--docs-destination', default=DOCS_DEST, help='The movidius SDK documentation folder here', show_default=True)
@click.option('--overwrite', is_flag=True, default=False, help='Overwrite existing files', show_default=True)
def cli(sdk_version, folder, sdk_destination, docs_destination, overwrite):
    """ bootstrap deepshtick development environment"""

    for name, info in get_sources(
            version=sdk_version,
            folder=folder,
            sdk_destination=sdk_destination,
            docs_destination=docs_destination).items():
        click.echo('Fetching {}'.format(name))
        source = info['source']
        dest = info['dest']

        filename = source.split('/')[-1]

        fetch(source_url=source, dest_directory=dest, dest_filename=filename, overwrite=overwrite)


if __name__ == '__main__':
    cli()
