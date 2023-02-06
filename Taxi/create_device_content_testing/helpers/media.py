# pylint: skip-file
# flake8: noqa
import glob
import pathlib
import random


def _photos_dir():
    return pathlib.Path(__file__).parent / 'photos'


def _videos_dir():
    return pathlib.Path(__file__).parent / 'videos'


def read_random_photo():
    photos_paths = glob.glob(str(_photos_dir()) + '/*.*')
    assert len(photos_paths) > 0, 'empty photos dir!'
    photo_path = random.choice(photos_paths)
    with open(photo_path, 'rb') as photo_file:
        return photo_file.read()


def read_random_video():
    videos_paths = glob.glob(str(_videos_dir()) + '/*.*')
    assert len(videos_paths) > 0, 'empty videos dir!'
    video_path = random.choice(videos_paths)
    with open(video_path, 'rb') as video_file:
        return video_file.read()
