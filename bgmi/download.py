# coding=utf-8
from __future__ import print_function, unicode_literals

import os

from bgmi.config import BGMI_SAVE_PATH, DOWNLOAD_DELEGATE
from bgmi.models import Download, STATUS_DOWNLOADING, STATUS_NOT_DOWNLOAD
from bgmi.services import XunleiLixianDownload
from bgmi.utils.utils import print_error

DOWNLOAD_DELEGATE_DICT = {
    'xunlei': XunleiLixianDownload,
}


def get_download_class(torrent='', overwrite=True, save_path='', instance=True):
    if DOWNLOAD_DELEGATE not in DOWNLOAD_DELEGATE_DICT:
        print_error('unexpected download delegate {0}'.format(DOWNLOAD_DELEGATE))

    delegate = DOWNLOAD_DELEGATE_DICT.get(DOWNLOAD_DELEGATE)

    if instance:
        delegate = delegate(torrent=torrent, overwrite=overwrite, save_path=save_path)

    return delegate


def download_prepare(data):
    queue = save_to_bangumi_download_queue(data)
    for download in queue:
        save_path = os.path.join(os.path.join(BGMI_SAVE_PATH, download.name), str(download.episode))
        # mark as downloading
        download.status = STATUS_DOWNLOADING
        download.save()
        try:
            # start download
            download_class = get_download_class(torrent=download.download, overwrite=True, save_path=save_path)
            download_class.download()

            if not os.path.exists(save_path):
                raise Exception('It seems the bangumi {0} not be downloaded'.format(download.name))

            # mark as downloaded
            download.delete()
        except Exception as e:
            print_error('Error: {0}'.format(e), exit_=False)
            download.status = STATUS_NOT_DOWNLOAD
            download.save()


def save_to_bangumi_download_queue(data):
    queue = []
    for i in data:
        download = Download(status=STATUS_NOT_DOWNLOAD, name=i['name'], title=i['title'],
                            episode=i['episode'], download=i['download'])
        download.save()
        queue.append(download)

    return queue
