import os

import pytest
import yatest.common as yatest
from utils import get_absolute_path, file_ends_with, get_s3_path


class TestGetAbsolutePath():
    def setup_class(self):
        self.current_dir = yatest.work_path('current_path')
        self.current_packaged_dir = os.path.join(self.current_dir, 'packaged')
        self.file_name = 'file.temp'

        os.makedirs(self.current_dir)
        os.makedirs(self.current_packaged_dir)

    @staticmethod
    def touch(file_path):
        """create empty file"""
        with open(file_path, 'w+') as f:
            f.write('')

    def test_simple(self):
        absolute_path = os.path.join(self.current_dir, self.file_name)
        self.touch(absolute_path)

        actual = get_absolute_path(self.file_name, self.current_dir)
        assert actual == absolute_path

    def test_when_packaged(self):
        absolute_path = os.path.join(self.current_packaged_dir, self.file_name)
        self.touch(absolute_path)

        actual = get_absolute_path(self.file_name, self.current_dir)
        assert actual == absolute_path

    def test_packaged_first(self):
        absolute_path = os.path.join(self.current_dir, self.file_name)
        self.touch(absolute_path)

        absolute_packaged_path = os.path.join(self.current_packaged_dir, self.file_name)
        self.touch(absolute_packaged_path)

        actual = get_absolute_path(self.file_name, self.current_dir)
        assert actual == absolute_packaged_path

    @pytest.mark.xfail(raises=ValueError)
    def test_raise_when_file_not_exist(self):
        get_absolute_path('not_existed.file', self.current_dir)


def test_file_ends_with():
    file_path = yatest.work_path('5858722529390400248_169_1080p.mp4')

    assert file_ends_with(file_path, 'mp4')
    assert not file_ends_with(file_path, 'mp3')


def test_file_ends_with_when_file_no_extension():
    file_path = yatest.work_path('QualityLevels(6757641)/Fragments(audio_ru=0)')
    assert file_ends_with(file_path, None)
    assert file_ends_with(file_path, '')

    assert not file_ends_with(file_path, 'mp4')


def test_file_ends_with_multiple_extensions():
    file_path = yatest.work_path('5858722529390400248_169_1080p.jpg')

    assert file_ends_with(file_path, ('jpg', 'mp4', 'mp3'))
    assert not file_ends_with(file_path, ('mov', 'mkv', 'png'))


def test_get_s3_path_trailers():
    # https://nda.ya.ru/3UWbtV
    expected = 'ott-content/315146076-4f5308e9f0a24427bf8461e0b7863c70/master.m3u8'
    actual = get_s3_path('ott-content/', '315146076-4f5308e9f0a24427bf8461e0b7863c70',
                         '315146076/4f5308e9-f0a2-4427-bf84-61e0b7863c70.ism/',
                         'master.m3u8', False, True, True)

    assert actual == expected


def test_get_s3_path_fairplay_master_playlist():
    # https://nda.ya.ru/3UWbu3
    expected = 'ott-content/334270867-4fd6870f2e9ba4f392ba9bdb9b03e900/master.hd.m3u8'
    actual = get_s3_path('ott-content/', '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900',
                         '334270867/4fd6870f-2e9b-a4f3-92ba-9bdb9b03e900.ism/',
                         '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900/master.hd.m3u8',
                         True, False, False)

    assert actual == expected


def test_get_s3_path_fairplay_sub_playlist():
    # https://nda.ya.ru/3UWbu3
    expected = 'ott-content/334270867-4fd6870f2e9ba4f392ba9bdb9b03e900/0-audio_ru_48000.m3u8'
    actual = get_s3_path('ott-content/', '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900',
                         '334270867/4fd6870f-2e9b-a4f3-92ba-9bdb9b03e900.ism/',
                         '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900/0-audio_ru_48000.m3u8',
                         True, False, False)

    assert actual == expected


def test_get_s3_path_fairplay_sub_ts():
    # https://nda.ya.ru/3UWbu3
    expected = 'ott-content/334270867-4fd6870f2e9ba4f392ba9bdb9b03e900/0-audio_ru_48000-0.ts'
    actual = get_s3_path('ott-content/', '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900',
                         '334270867/4fd6870f-2e9b-a4f3-92ba-9bdb9b03e900.ism/',
                         '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900/0-audio_ru_48000-0.ts',
                         True, False, False)

    assert actual == expected


def test_get_s3_path_fairplay_vtt():
    # https://nda.ya.ru/3UWbu3
    expected = 'ott-content/334270867-4fd6870f2e9ba4f392ba9bdb9b03e900/sub-rus-0-stream.vtt'
    actual = get_s3_path('ott-content/', '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900',
                         '334270867/4fd6870f-2e9b-a4f3-92ba-9bdb9b03e900.ism/',
                         '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900/sub-rus-0-stream.vtt',
                         True, False, False)

    assert actual == expected


def test_get_s3_path_thumbnails():
    # https://nda.ya.ru/3UWbu3
    expected = 'ott-content/10115585257425869475_001.jpg'
    actual = get_s3_path('ott-content/', '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900',
                         '334270867/4fd6870f-2e9b-a4f3-92ba-9bdb9b03e900.ism/',
                         '10115585257425869475_001.jpg',
                         True, False, False)

    assert actual == expected


def test_get_s3_path_dash_mss_subtitles():
    # https://nda.ya.ru/3UWbu3
    expected = 'ott-content/334270867/4fd6870f-2e9b-a4f3-92ba-9bdb9b03e900.ism/subtitles/ru/sub-rus-0-stream.vtt'
    actual = get_s3_path('ott-content/', '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900',
                         '334270867/4fd6870f-2e9b-a4f3-92ba-9bdb9b03e900.ism/',
                         'subtitles/ru/sub-rus-0-stream.vtt',
                         True, False, False)

    assert actual == expected


def test_get_s3_path_dash_fragment():
    # https://nda.ya.ru/3UWbu3
    expected = 'ott-content/334270867/4fd6870f-2e9b-a4f3-92ba-9bdb9b03e900.ism/QualityLevels(2133110)/Fragments(video=11040195833)'
    actual = get_s3_path('ott-content/', '334270867-4fd6870f2e9ba4f392ba9bdb9b03e900',
                         '334270867/4fd6870f-2e9b-a4f3-92ba-9bdb9b03e900.ism/',
                         'QualityLevels(2133110)/Fragments(video=11040195833)',
                         True, False, False)

    assert actual == expected


def test_get_s3_path_youtube_dl_naver():
    # https://nda.ya.ru/3UWcvF
    expected = 'vod-content/8967576414959421514'
    actual = get_s3_path('vod-content/', '', '334852687/.ism/',
                         '8967576414959421514', False, False, False)

    assert actual == expected
