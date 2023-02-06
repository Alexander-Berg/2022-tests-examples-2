# -*- coding: utf-8 -*-
import logging
import os.path

from lxml import etree

logger = logging.getLogger(__name__)


class Plural(object):
    ONE = 'one'
    SOME = 'some'
    MANY = 'many'
    NONE = 'none'


class TankerFileNotFoundError(Exception):
    pass


class TankerTranslationNotFoundError(Exception):
    pass


def _get_xpath(keyset, key, lang, plural=None):
    xpath = '/tanker/project/keyset[@id="{}"]/key[@id="{}" and @is_plural="{}"]/value[@language="{}"]' \
        .format(keyset, key, str(plural is not None), lang)

    if not plural:
        xpath += '/text()'
    else:
        xpath += '/plural/{}/text()'.format(plural)

    return xpath


def get_translation(project, keyset, key, lang, plural=None, fallback=None):
    xml_file = '../tanker/{}.xml'.format(project)

    if not os.path.isfile(xml_file):
        raise TankerFileNotFoundError('Tanker file "{}" not found'.format(xml_file))

    xpath = _get_xpath(keyset, key, lang, plural)
    logger.debug('Getting "{}" from {}'.format(xpath, xml_file))
    tree = etree.parse(xml_file.format(project))
    results = tree.xpath(xpath)

    if not results and fallback:
        xpath = _get_xpath(keyset, key, fallback, plural)
        results = tree.xpath(xpath)

    if not results:
        raise TankerTranslationNotFoundError('No "{}" translation found for {} -> {} -> {}'
                                             .format(lang, project, keyset, key))
    return results[0]
