# -*- coding: utf-8 -*-

from nose.tools import raises
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import (
    Hostname,
    IPAddress,
)
import pytest


VALID_IP = [
    '127.0.0.1',
    '8.8.8.8',
    '255.255.255.254',
    '::1',
    '::ffff:127.0.0.1',
    '2a02:6b8:0:101:6267:20ff:fe63:7af4',
]

INVALID_IP = [
    'blabla',
    'a.0.0.0',
    '1.2.3.4"; rm -rf / #',
    'asd1.2.3.4',
    '2aa02:6b8:0:101:6267:20ff:fe63:7af4',
]


@pytest.mark.parametrize('addr', VALID_IP)
def test_ipaddress(addr):
    check_equality(IPAddress(), (addr, str(addr)))


@pytest.mark.parametrize('key', INVALID_IP)
def test_ipaddress_invalid(key):
    check_raise_error(IPAddress(), key)


VALID_HOSTNAME = [
    u'Yandex.ru',
    u'1-bla-bla.q1w2e3.com',
    u'1.2.3.4',
    u'окна.рф',
    u'ёлки.палки.ру',
    u'天津風.moe',
    u'är.fi',
    u'парітет.укр',
    u'aupairmädchen.club',
    u'trườngvinhhino.vn',
    u'ツ.club',
    # По RFC каждая секция не больше 63 символов в ASCII представлении,
    # в сумме меньше 255:
    # https://stackoverflow.com/questions/8717378/what-is-the-maximum-length-of-an-idna-converted-domain-name
    u'{}.{}.{}.{}'.format(u'a' * 63, u'b' * 63, u'c' * 63, u'd' * 63),
    # добавится 6 лишних символов: xn--4c
    u'{}.omg'.format(u'ä' * 57),
    u'i̇stanbul.generation.bz',
    u'i\u0307stanbul.generation.bz',
]

INVALID_HOSTNAME = [
    u'zxc!*(&@^#',
    u'!*(&@^#zxc',
    u'!*(&@^#zxc.zxc*&(^(*!@',
    u'-bla-bla.qwe.com',
    u'asd.com-',
    u'zxcv; "; rm -rf / #',
    # Случай с кривым кодированием punycode
    u'a' * 64,
    u'💔.cf',
    'foo_bar.wer.com',
    '!@#$%^&*()`~',
    '<>?:\"{}|_+',
    ',./;\'[]\\-=',
    'Thequic\b\b\b\b\b\bkbrownfo\u0007\u0007\u0007\u0007\u0007\u0007\u0007'
    '\u0007\u0007\u0007\u0007x...[Beeeep].ru',
    '<fooval=`bar\'/>.ru',
    'Ifyou\'rereadingthis,you\'vebeeninacomaforalmost20yearsnow.'
    'We\'retryinganewtechnique.Wedon\'tknowwherethismessagewillendupinyourdream,'
    'butwehopeitworks.Pleasewakeup,wemissyou..ru',
    '(){_;}>_[$($())]{touch/tmp/blns.shellshock2.fail;}',
    'Rosesare\u001B[0;31mred\u001B[0m,violetsare\u001B[0;34mblue.Hopeyouenjoyterminalhue',
    '<ahref=\"\\x04javascript:javascript:alert(1)\"id=\"fuzzelement1\">test</a>',
    '`\"\'><imgsrc=xxx:x\\x0Aonerror=javascript:alert(1)>',
    '<ahref=java&#1&#2&#3&#4&#5&#6&#7&#8&#11&#12script:javascript:alert(1)>XXX</a>',
    '0000039&#0000088&#0000083&#0000083&#0000039&#0000041>',
    # в сумме больше 255
    '{}.{}.{}.{}.{}.com'.format('a' * 63, 'b' * 63, 'c' * 63, 'd' * 63, 'e' * 63),
    u'{}.com'.format(u'a' * 64),
    # после конвертации в пуникод в сумме больше 255 символов
    u'{}.{}.{}.{}.{}'.format(u'ä' * 57, u'i' * 63, u'ф' * 57, u'ц' * 57, u'f' * 30),
]


@pytest.mark.parametrize('name', VALID_HOSTNAME)
def test_hostname(name):
    check_equality(Hostname(), (name, name))


@pytest.mark.parametrize('name', INVALID_HOSTNAME)
def test_hostname_invalid(name):
    check_raise_error(Hostname(), name)


@pytest.mark.parametrize(('original', 'decoded'), [
    (u'xn--80atjc.xn--p1ai', u'окна.рф'),
    (u'yandex.ru', u'yandex.ru'),
    (u'окна.рф', u'окна.рф'),
    (u'hello.xn--h1ahn', u'hello.мир'),
    ])
def test_punycode_handling(original, decoded):
    check_equality(Hostname(decode_punycode=True), (original, decoded))


@pytest.mark.parametrize('malformed', [
    u'xn--a',
    u'hello.xn--a',
    u'xn--80atjc.xn--p1',
    ])
def test_punycode_handling_invalid(malformed):
    check_raise_error(Hostname(decode_punycode=True), malformed)


@pytest.mark.parametrize(('charset', 'host'), [
    ('default', host) for host in VALID_HOSTNAME
    ] + [
    ('strict', host) for host in [
        u'xn--80atjc.xn--p1',
        u'hello-world.ru',
        u'okna.ru',
        ]
    ])
def test_alternate_charset(charset, host):
    check_equality(Hostname(character_set=charset), (host, host))


@pytest.mark.parametrize(('charset', 'host'), [
    ('default', host) for host in INVALID_HOSTNAME
    ] + [
    ('strict', host) for host in INVALID_HOSTNAME
    ] + [
    ('strict', host) for host in [
        u'здравствуй-мир.рф',
        u'hello.мир',
        u'здравствуй.world',
        ]
    ])
def test_alternate_charset_invalid(charset, host):
    check_raise_error(Hostname(character_set=charset), host)


@with_settings(
    NATIVE_EMAIL_DOMAINS=('yandex.ru', 'yandex.com', 'yandex.co.il', u'яндекс.рф', 'ya.ru', 'narod.ru'),
)
@pytest.mark.parametrize('host', [
    'new-yandex.ru',
    'naydex.ru',
    'yandex.example',
    'yandex.ru.com',
    'new.yandex.ru',
    ])
def test_yandex_native_hostname(host):
    check_equality(Hostname(reject_native=True), (host, host))


@with_settings(
    NATIVE_EMAIL_DOMAINS=('yandex.ru', 'yandex.com', 'yandex.co.il', u'яндекс.рф', 'ya.ru', 'narod.ru'),
)
@pytest.mark.parametrize('native_host', [
    'yandex.ru',
    'yandex.co.il',
    'ya.ru',
    u'яндекс.рф',
    'narod.ru',
    ])
def test_yandex_native_hostname_invalid(native_host):
    check_raise_error(Hostname(reject_native=True), native_host)


@raises(ValueError)
def test_invalid_charset():
    Hostname(character_set='asdf')


def test_min_levels():
    check_raise_error(Hostname(character_set='default'), 'foo')
    check_raise_error(Hostname(character_set='default', min_levels=3), 'foo.bar')

    check_equality(Hostname(character_set='default', min_levels=1), ('foo', 'foo'))
    check_equality(Hostname(character_set='default', min_levels=3), ('foo.bar.zar', 'foo.bar.zar'))
