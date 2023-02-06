# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from functools import partial

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.common import oauth2
from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import (
    BadParametersProxylibError,
    InvalidTokenProxylibError,
    PermissionProxylibError,
    ProviderTemporaryUnavailableProxylibError,
    UnexpectedResponseProxylibError,
)
from passport.backend.social.common.providers.Google import Google
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    SIMPLE_USERID1,
    UNIXTIME1,
)
from passport.backend.social.common.test.fake_useragent import FakeUseragent
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.test.types import FakeResponse
from passport.backend.social.common.useragent import build_http_pool_manager
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import google as google_test

from . import TestProxy


class TestProxyGoogle(TestProxy):
    provider_code = 'gg'
    error_profile_response = '{"error":"invalid_token","error_description":"Invalid Credentials"}'

    def test_error_response(self):
        decoded_data = '''
        {
          "error": {
           "errors": [
            {
             "domain": "usageLimits",
             "reason": "accessNotConfigured",
             "message": "Access Not Configured. Please use Google Developers Console to activate the API for your project."
            }
           ],
           "code": 403,
           "message": "Access Not Configured. Please use Google Developers Console to activate the API for your project."
          }
         }
        '''
        with self.assertRaises(PermissionProxylibError):
            self._process_single_test(
                'get_profile',
                decoded_data,
            )

    def test_invalid_credentials_response(self):
        decoded_data = '''
        {"error": { "errors": [{"domain": "global","reason": "authError","message": "Invalid Credentials",
        "locationType": "header", "location": "Authorization"}], "code": 401,
        "message": "Invalid Credentials"}}
        '''

        with self.assertRaises(InvalidTokenProxylibError):
            self._process_single_test(
                'get_profile',
                decoded_data,
            )

    def test_profile_1(self):
        decoded_data = (
            '{"sub": "112913562853868378959","name": "Name LName","given_name": "Name",'
            '"family_name": "LName","profile": "https://plus.google.com/112913562853868378959",'
            '"picture": "https://lh5.googleusercontent.com/-yiUV6qCFsco/fySMtH2QNU/photo.jpg",'
            '"email": "user@gmail.com","email_verified": true,"gender": "male","locale": "en"}'
        )

        expected_dict = {
            u'username': u'user', u'firstname': u'Name', u'lastname': u'LName', u'userid': '112913562853868378959',
            u'avatar': {u'0x0': u'https://lh5.googleusercontent.com/-yiUV6qCFsco/fySMtH2QNU/photo.jpg'},
            u'gender': u'm', u'email': u'user@gmail.com',
        }
        self._process_single_test(
            'get_profile',
            decoded_data,
            expected_dict=expected_dict,
        )

    def test_profile_2(self):
        decoded_data = (
            '{"sub": "112913562853868378959","name": "Name LName","given_name": "Name",'
            '"family_name": "LName","profile": "https://plus.google.com/112913562853868378959",'
            '"picture": "https://lh5.googleusercontent.com/-yiUV6qCFsco/fySMtH2QNU/photo.jpg",'
            '"email": "user@gmail.com","email_verified": false,"gender": "","locale": "en"}'
        )

        expected_dict = {u'firstname': u'Name', u'lastname': u'LName', u'userid': '112913562853868378959',
                         u'avatar': {u'0x0': u'https://lh5.googleusercontent.com/-yiUV6qCFsco/fySMtH2QNU/photo.jpg'}}

        self._process_single_test(
            'get_profile',
            decoded_data,
            expected_dict=expected_dict,
        )

    def test_profile_3(self):
        decoded_data = (
            '{"sub": "112913562853868378959","name": "Name LName","given_name": "Name",'
            '"family_name": "LName","profile": "https://plus.google.com/112913562853868378959",'
            '"picture": "https://lh5.googleusercontent.com/-yiUV6qCFsco/fySMtH2QNU/photo.jpg",'
            '"email": "user@example.com","email_verified": true,"gender": "male","locale": "en"}'
        )

        expected_dict = {u'firstname': u'Name', u'lastname': u'LName', u'userid': '112913562853868378959',
                         u'avatar': {u'0x0': u'https://lh5.googleusercontent.com/-yiUV6qCFsco/fySMtH2QNU/photo.jpg'},
                         u'gender': u'm', u'email': u'user@example.com'}

        self._process_single_test(
            'get_profile',
            decoded_data,
            expected_dict=expected_dict,
        )

    def test_profile_error(self):
        self._tst_profile_error()

    def test_get_mails_unread_count_ok(self):
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
            <feed version="0.3" xmlns="http://purl.org/atom/ns#">
            <title>Gmail - Inbox for antony.kirilenko@gmail.com</title>
            <tagline>New messages in your Gmail Inbox</tagline>
            <fullcount>1</fullcount>
            <link rel="alternate" href="http://mail.google.com/mail" type="text/html" />
            <modified>2013-10-28T10:57:04Z</modified>
            </feed>'''

        self._process_single_test(
            'get_mails_unread_count',
            data,
            expected_value=1,
        )

    def test_get_mails_unread_count_error(self):
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
            <feed version="0.3" xmlns="http://purl.org/atom/ns#">
            <modified>2013-10-28T10:57:04Z</modified>
            </feed>'''
        self._process_single_test(
            'get_mails_unread_count',
            data,
            expected_value=0,
        )

    def test_get_profile_links(self):
        proxy = get_proxy(self.provider_code)
        links = proxy.get_profile_links('12345', 'some_user')
        eq_(links, [u'https://plus.google.com/12345'])

    def test_get_photos_with_exif__with_creation_time(self):
        # Не хочу провести свои лучшие годы жизни, сворачивая ЭТО в короткие строчки
        data = b'''<?xml version='1.0' encoding='UTF-8'?><feed xmlns='http://www.w3.org/2005/Atom' xmlns:gd='http://schemas.google.com/g/2005' xmlns:openSearch='http://a9.com/-/spec/opensearch/1.1/' xmlns:gphoto='http://schemas.google.com/photos/2007' xmlns:app='http://www.w3.org/2007/app' xmlns:exif='http://schemas.google.com/photos/exif/2007' xmlns:media='http://search.yahoo.com/mrss/' gd:etag='W/&quot;DUYBQHw6cCp7ImA9XRdRF0o.&quot;'><id>https://picasaweb.google.com/data/feed/user/112913562853868378959/albumid/6067831637300764145</id><updated>2014-10-08T14:05:51.218Z</updated><category scheme='http://schemas.google.com/g/2005#kind' term='http://schemas.google.com/photos/2007#album'/><title>2014-10-08</title><subtitle/><rights>protected</rights><icon>https://lh6.googleusercontent.com/-SSJSqm7-huc/VDVEubIwXfE/AAAAAAAABO8/iaF0bf6IZLE/s160-c/20141008.jpg</icon><link rel='http://schemas.google.com/g/2005#feed' type='application/atom+xml' href='https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/6067831637300764145'/><link rel='http://schemas.google.com/g/2005#post' type='application/atom+xml' href='https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/6067831637300764145'/><link rel='http://schemas.google.com/g/2005#resumable-create-media' type='application/atom+xml' href='https://picasaweb.google.com/data/upload/resumable/media/create-session/feed/api/user/112913562853868378959/albumid/6067831637300764145'/><link rel='alternate' type='text/html' href='https://picasaweb.google.com/112913562853868378959/20141008'/><link rel='http://schemas.google.com/photos/2007#slideshow' type='application/x-shockwave-flash' href='https://photos.gstatic.com/media/slideshow.swf?host=picasaweb.google.com&amp;RGB=0x000000&amp;feed=https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/6067831637300764145?alt%3Drss'/><link rel='http://schemas.google.com/photos/2007#report' type='text/html' href='https://picasaweb.google.com/lh/reportAbuse?uname=112913562853868378959&amp;aid=6067831637300764145'/><link rel='http://schemas.google.com/acl/2007#accessControlList' type='application/atom+xml' href='https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/6067831637300764145/acl'/><link rel='self' type='application/atom+xml' href='https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/6067831637300764145?start-index=1&amp;max-results=500&amp;kind=photo&amp;imgmax=d'/><author><name>Anton Kirilenko</name><uri>https://picasaweb.google.com/112913562853868378959</uri></author><generator version='1.00' uri='http://picasaweb.google.com/'>Picasaweb</generator><openSearch:totalResults>1</openSearch:totalResults><openSearch:startIndex>1</openSearch:startIndex><openSearch:itemsPerPage>500</openSearch:itemsPerPage><gphoto:id>6067831637300764145</gphoto:id><gphoto:name>20141008</gphoto:name><gphoto:location/><gphoto:access>protected</gphoto:access><gphoto:timestamp>1412777145000</gphoto:timestamp><gphoto:numphotos>1</gphoto:numphotos><gphoto:numphotosremaining>1999</gphoto:numphotosremaining><gphoto:bytesUsed>997512</gphoto:bytesUsed><gphoto:user>112913562853868378959</gphoto:user><gphoto:nickname>Anton Kirilenko</gphoto:nickname><gphoto:allowPrints>true</gphoto:allowPrints><gphoto:allowDownloads>true</gphoto:allowDownloads><entry gd:etag='&quot;YD8qeyI.&quot;'><id>https://picasaweb.google.com/data/entry/user/112913562853868378959/albumid/6067831637300764145/photoid/6067831641775680242</id><published>2014-10-08T14:05:46.000Z</published><updated>2014-10-08T14:05:51.177Z</updated><app:edited>2014-10-08T14:05:51.177Z</app:edited><category scheme='http://schemas.google.com/g/2005#kind' term='http://schemas.google.com/photos/2007#photo'/><title>IMAG0340.jpg</title><summary/><content type='image/jpeg' src='https://lh6.googleusercontent.com/-VkP9FovdDh4/VDVEurzqKvI/AAAAAAAABO0/akNHtPm-nBw/I/IMAG0340.jpg'/><link rel='http://schemas.google.com/g/2005#feed' type='application/atom+xml' href='https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/6067831637300764145/photoid/6067831641775680242'/><link rel='alternate' type='text/html' href='https://picasaweb.google.com/112913562853868378959/20141008#6067831641775680242'/><link rel='http://schemas.google.com/photos/2007#canonical' type='text/html' href='https://picasaweb.google.com/lh/photo/QpW5HaLw_JooOUE5g8nqotMTjNZETYmyPJy0liipFm0'/><link rel='self' type='application/atom+xml' href='https://picasaweb.google.com/data/entry/api/user/112913562853868378959/albumid/6067831637300764145/photoid/6067831641775680242'/><link rel='edit' type='application/atom+xml' href='https://picasaweb.google.com/data/entry/api/user/112913562853868378959/albumid/6067831637300764145/photoid/6067831641775680242'/><link rel='edit-media' type='image/jpeg' href='https://picasaweb.google.com/data/media/api/user/112913562853868378959/albumid/6067831637300764145/photoid/6067831641775680242'/><link rel='http://schemas.google.com/photos/2007#report' type='text/html' href='https://picasaweb.google.com/lh/reportAbuse?uname=112913562853868378959&amp;aid=6067831637300764145&amp;iid=6067831641775680242'/><gphoto:id>6067831641775680242</gphoto:id><gphoto:albumid>6067831637300764145</gphoto:albumid><gphoto:access>only_you</gphoto:access><gphoto:width>2048</gphoto:width><gphoto:height>1155</gphoto:height><gphoto:size>997512</gphoto:size><gphoto:checksum/><gphoto:timestamp>1381660758000</gphoto:timestamp><gphoto:imageVersion>1261</gphoto:imageVersion><gphoto:commentingEnabled>true</gphoto:commentingEnabled><gphoto:commentCount>0</gphoto:commentCount><gphoto:streamId>shared_group_6067831641775680242</gphoto:streamId><gphoto:license id='0' name='\u0412\u0441\u0435 \u043f\u0440\u0430\u0432\u0430 \u0437\u0430\u0449\u0438\u0449\u0435\u043d\u044b' url=''>ALL_RIGHTS_RESERVED</gphoto:license><gphoto:shapes faces='done'/><exif:tags><exif:fstop>2.0</exif:fstop><exif:make>HTC</exif:make><exif:model>HTC One XL</exif:model><exif:exposure>0.007363</exif:exposure><exif:flash>false</exif:flash><exif:focallength>3.63</exif:focallength><exif:iso>125</exif:iso><exif:time>1381675158000</exif:time><exif:imageUniqueID>ee3e0ea0e6008fad0000000000000000</exif:imageUniqueID></exif:tags><media:group><media:content url='https://lh6.googleusercontent.com/-VkP9FovdDh4/VDVEurzqKvI/AAAAAAAABO0/akNHtPm-nBw/I/IMAG0340.jpg' height='1155' width='2048' type='image/jpeg' medium='image'/><media:credit>Anton Kirilenko</media:credit><media:description type='plain'/><media:keywords/><media:thumbnail url='https://lh6.googleusercontent.com/-VkP9FovdDh4/VDVEurzqKvI/AAAAAAAABO0/XStyCryMQhc/s72/IMAG0340.jpg' height='41' width='72'/><media:thumbnail url='https://lh6.googleusercontent.com/-VkP9FovdDh4/VDVEurzqKvI/AAAAAAAABO0/XStyCryMQhc/s144/IMAG0340.jpg' height='82' width='144'/><media:thumbnail url='https://lh6.googleusercontent.com/-VkP9FovdDh4/VDVEurzqKvI/AAAAAAAABO0/XStyCryMQhc/s288/IMAG0340.jpg' height='163' width='288'/><media:title type='plain'>IMAG0340.jpg</media:title></media:group></entry></feed>'''  # noqa

        item = {
            'created': 1381660758,
            'images': [
                {
                    'height': 1155,
                    'url': ('https://lh6.googleusercontent.com/-VkP9FovdDh4/VDVEurzqKvI/AAAAAAAABO0/'
                            'akNHtPm-nBw/I/IMAG0340.jpg'),
                    'width': 2048,
                },
            ],
            'pid': '6067831641775680242',
            'photo_creation_time': 1381675158,
        }
        expected_dict = {'result': [item]}
        self._process_single_test(
            'get_photos',
            data,
            expected_dict=expected_dict,
            kwargs=dict(aid='1'),
        )

    def test_get_photos_with_exif__no_creation_time(self):
        # Не хочу провести свои лучшие годы жизни, сворачивая ЭТО в короткие строчки
        data = b'''<?xml version='1.0' encoding='UTF-8'?><feed xmlns='http://www.w3.org/2005/Atom' xmlns:gd='http://schemas.google.com/g/2005' xmlns:openSearch='http://a9.com/-/spec/opensearch/1.1/' xmlns:gphoto='http://schemas.google.com/photos/2007' xmlns:app='http://www.w3.org/2007/app' xmlns:exif='http://schemas.google.com/photos/exif/2007' xmlns:media='http://search.yahoo.com/mrss/' gd:etag='W/&quot;CUACSXk4fCp7ImA9Wh5aGUs.&quot;'><id>https://picasaweb.google.com/data/feed/user/112913562853868378959/albumid/5969843696710124433</id><updated>2014-01-17T13:02:48.734Z</updated><category scheme='http://schemas.google.com/g/2005#kind' term='http://schemas.google.com/photos/2007#album'/><title>2014-01-17</title><subtitle/><rights>protected</rights><icon>https://lh6.googleusercontent.com/-LP6im8hKA2k/UtklNmsDA5E/AAAAAAAAABI/b5BpE_PdyvQ/s160-c/20140117.jpg</icon><link rel='http://schemas.google.com/g/2005#feed' type='application/atom+xml' href='https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/5969843696710124433'/><link rel='http://schemas.google.com/g/2005#post' type='application/atom+xml' href='https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/5969843696710124433'/><link rel='http://schemas.google.com/g/2005#resumable-create-media' type='application/atom+xml' href='https://picasaweb.google.com/data/upload/resumable/media/create-session/feed/api/user/112913562853868378959/albumid/5969843696710124433'/><link rel='alternate' type='text/html' href='https://picasaweb.google.com/112913562853868378959/20140117'/><link rel='http://schemas.google.com/photos/2007#slideshow' type='application/x-shockwave-flash' href='https://photos.gstatic.com/media/slideshow.swf?host=picasaweb.google.com&amp;RGB=0x000000&amp;feed=https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/5969843696710124433?alt%3Drss'/><link rel='http://schemas.google.com/photos/2007#report' type='text/html' href='https://picasaweb.google.com/lh/reportAbuse?uname=112913562853868378959&amp;aid=5969843696710124433'/><link rel='http://schemas.google.com/acl/2007#accessControlList' type='application/atom+xml' href='https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/5969843696710124433/acl'/><link rel='self' type='application/atom+xml' href='https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/5969843696710124433?start-index=1&amp;max-results=500&amp;kind=photo&amp;imgmax=d'/><author><name>Anton Kirilenko</name><uri>https://picasaweb.google.com/112913562853868378959</uri></author><generator version='1.00' uri='http://picasaweb.google.com/'>Picasaweb</generator><openSearch:totalResults>1</openSearch:totalResults><openSearch:startIndex>1</openSearch:startIndex><openSearch:itemsPerPage>500</openSearch:itemsPerPage><gphoto:id>5969843696710124433</gphoto:id><gphoto:name>20140117</gphoto:name><gphoto:location/><gphoto:access>protected</gphoto:access><gphoto:timestamp>1389962550000</gphoto:timestamp><gphoto:numphotos>1</gphoto:numphotos><gphoto:numphotosremaining>1999</gphoto:numphotosremaining><gphoto:bytesUsed>8166</gphoto:bytesUsed><gphoto:user>112913562853868378959</gphoto:user><gphoto:nickname>Anton Kirilenko</gphoto:nickname><gphoto:allowPrints>true</gphoto:allowPrints><gphoto:allowDownloads>true</gphoto:allowDownloads><entry gd:etag='&quot;YD8qeyI.&quot;'><id>https://picasaweb.google.com/data/entry/user/112913562853868378959/albumid/5969843696710124433/photoid/5969843701749731426</id><published>2014-01-17T12:42:31.000Z</published><updated>2014-01-17T12:42:43.503Z</updated><app:edited>2014-01-17T12:42:43.503Z</app:edited><category scheme='http://schemas.google.com/g/2005#kind' term='http://schemas.google.com/photos/2007#photo'/><title>Skachat-trafaret-Snegovik.gif</title><summary/><content type='image/gif' src='https://lh6.googleusercontent.com/-LpZWWnoi5Cg/UtklN5dlUGI/AAAAAAAAABE/mO9JRGyzD5E/I/Skachat-trafaret-Snegovik.gif'/><link rel='http://schemas.google.com/g/2005#feed' type='application/atom+xml' href='https://picasaweb.google.com/data/feed/api/user/112913562853868378959/albumid/5969843696710124433/photoid/5969843701749731426'/><link rel='alternate' type='text/html' href='https://picasaweb.google.com/112913562853868378959/20140117#5969843701749731426'/><link rel='http://schemas.google.com/photos/2007#canonical' type='text/html' href='https://picasaweb.google.com/lh/photo/Q68y7QnrX5HswvjUqvBKwdMTjNZETYmyPJy0liipFm0'/><link rel='self' type='application/atom+xml' href='https://picasaweb.google.com/data/entry/api/user/112913562853868378959/albumid/5969843696710124433/photoid/5969843701749731426'/><link rel='edit' type='application/atom+xml' href='https://picasaweb.google.com/data/entry/api/user/112913562853868378959/albumid/5969843696710124433/photoid/5969843701749731426'/><link rel='edit-media' type='image/jpeg' href='https://picasaweb.google.com/data/media/api/user/112913562853868378959/albumid/5969843696710124433/photoid/5969843701749731426'/><link rel='http://schemas.google.com/photos/2007#report' type='text/html' href='https://picasaweb.google.com/lh/reportAbuse?uname=112913562853868378959&amp;aid=5969843696710124433&amp;iid=5969843701749731426'/><gphoto:id>5969843701749731426</gphoto:id><gphoto:albumid>5969843696710124433</gphoto:albumid><gphoto:access>only_you</gphoto:access><gphoto:width>600</gphoto:width><gphoto:height>785</gphoto:height><gphoto:size>8166</gphoto:size><gphoto:checksum/><gphoto:timestamp>1389962551000</gphoto:timestamp><gphoto:imageVersion>17</gphoto:imageVersion><gphoto:commentingEnabled>true</gphoto:commentingEnabled><gphoto:commentCount>0</gphoto:commentCount><gphoto:streamId>shared_group_5969843701749731426</gphoto:streamId><gphoto:license id='0' name='\u0412\u0441\u0435 \u043f\u0440\u0430\u0432\u0430 \u0437\u0430\u0449\u0438\u0449\u0435\u043d\u044b' url=''>ALL_RIGHTS_RESERVED</gphoto:license><gphoto:shapes faces='done'/><exif:tags><exif:imageUniqueID>c91de7631e1433aa0000000000000000</exif:imageUniqueID></exif:tags><media:group><media:content url='https://lh6.googleusercontent.com/-LpZWWnoi5Cg/UtklN5dlUGI/AAAAAAAAABE/mO9JRGyzD5E/I/Skachat-trafaret-Snegovik.gif' height='785' width='600' type='image/gif' medium='image'/><media:credit>Anton Kirilenko</media:credit><media:description type='plain'/><media:keywords/><media:thumbnail url='https://lh6.googleusercontent.com/-LpZWWnoi5Cg/UtklN5dlUGI/AAAAAAAAABE/HzkHkEEb1-U/s72/Skachat-trafaret-Snegovik.png' height='72' width='56'/><media:thumbnail url='https://lh6.googleusercontent.com/-LpZWWnoi5Cg/UtklN5dlUGI/AAAAAAAAABE/HzkHkEEb1-U/s144/Skachat-trafaret-Snegovik.png' height='144' width='111'/><media:thumbnail url='https://lh6.googleusercontent.com/-LpZWWnoi5Cg/UtklN5dlUGI/AAAAAAAAABE/HzkHkEEb1-U/s288/Skachat-trafaret-Snegovik.png' height='288' width='221'/><media:title type='plain'>Skachat-trafaret-Snegovik.gif</media:title></media:group></entry></feed>'''  # noqa

        item = {
            'created': 1389962551,
            'images': [
                {
                    'height': 785,
                    'url': ('https://lh6.googleusercontent.com/-LpZWWnoi5Cg/UtklN5dlUGI/AAAAAAAAABE/'
                            'mO9JRGyzD5E/I/Skachat-trafaret-Snegovik.gif'),
                    'width': 600,
                },
            ],
            'pid': '5969843701749731426',
        }
        expected_dict = {'result': [item]}
        self._process_single_test(
            'get_photos',
            data,
            expected_dict=expected_dict,
            kwargs=dict(aid='1'),
        )


class TestGoogle(TestCase):
    def setUp(self):
        super(TestGoogle, self).setUp()
        passport.backend.social.proxylib.init()
        self._proxy = google_test.FakeProxy().start()

    def tearDown(self):
        self._proxy.stop()
        super(TestGoogle, self).tearDown()

    def test_token_info__ok(self):
        self._proxy.set_response_value(
            'get_token_info',
            google_test.GoogleApi.get_token_info({'exp': str(UNIXTIME1)}),
        )

        rv = get_proxy().get_token_info()

        eq_(
            rv,
            {
                'userid': SIMPLE_USERID1,
                'scopes': [
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'https://www.googleapis.com/auth/userinfo.email',
                ],
                'client_id': EXTERNAL_APPLICATION_ID1,
                'expires': UNIXTIME1,
            },
        )

    @raises(BadParametersProxylibError)
    def test_token_info__other_app(self):
        self._proxy.set_response_value(
            'get_token_info',
            google_test.GoogleApi.get_token_info({
                'aud': EXTERNAL_APPLICATION_ID2,
            }),
        )

        get_proxy().get_token_info()

    @raises(InvalidTokenProxylibError)
    def test_token_info__fail(self):
        self._proxy.set_response_value(
            'get_token_info',
            google_test.GoogleApi.get_token_info__fail(),
        )

        get_proxy().get_token_info()

    def test_token_info__backend_failed(self):
        self._proxy.set_response_value('get_token_info', google_test.GoogleApi.build_backend_error())
        with self.assertRaises(ProviderTemporaryUnavailableProxylibError):
            get_proxy().get_token_info()

    def test_backend_failed(self):
        self._proxy.set_response_value('get_profile', google_test.GoogleApi.build_backend_error())

        with self.assertRaises(ProviderTemporaryUnavailableProxylibError):
            get_proxy().get_profile()

    def test_refresh_token_server_error(self):
        self._proxy.set_response_value(
            'refresh_token',
            google_test.GoogleApi.build_error(
                error='internal_failure',
                error_description='Backend Error',
            )
        )

        with self.assertRaises(ProviderTemporaryUnavailableProxylibError):
            get_proxy().refresh_token(APPLICATION_TOKEN1)

    def test_not_json(self):
        self._proxy.set_response_value(
            'get_photos',
            FakeResponse('fake xml', 200),
        )

        with self.assertRaises(UnexpectedResponseProxylibError):
            get_proxy().get_photos('aid')


class TestDeepGoogle(TestCase):
    def setUp(self):
        super(TestDeepGoogle, self).setUp()
        self._fake_useragent = FakeUseragent().start()

        LazyLoader.register('http_pool_manager', build_http_pool_manager)

        passport.backend.social.proxylib.init()

    def tearDown(self):
        self._fake_useragent.stop()
        super(TestDeepGoogle, self).tearDown()

    def test_exchange__invalid_grant(self):
        self._fake_useragent.set_response_value(
            oauth2.test.build_error('invalid_grant'),
        )

        with self.assertRaises(InvalidTokenProxylibError):
            get_proxy().exchange_token()


get_proxy = partial(
    get_proxy,
    Google.code,
    {'value': APPLICATION_TOKEN1},
    Application(
        id=EXTERNAL_APPLICATION_ID1,
        secret=APPLICATION_SECRET1,
        request_from_intranet_allowed=True,
    ),
)
