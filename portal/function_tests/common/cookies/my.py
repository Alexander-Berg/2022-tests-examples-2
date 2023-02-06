# -*- coding: utf-8 -*-

"""
Модуль парсинга куки My
"""
from __future__ import print_function
from common.languages import LANG_CODES
import base64
import json


class CookieMyException(BaseException):
    def __init__(self, message):
        self.message = message


class CookieMyBadCookie(CookieMyException):
    pass


class CookieMyBadBlockId(CookieMyException):
    pass


class CookieMyBadBlockData(CookieMyException):
    pass


class CookieMy(object):
    START_BYTE = 0x63
    END_BYTE = 0x00

    def __init__(self, value=None):
        self.blocks = {}
        if value is not None:
            self.parse(value)

    @staticmethod
    def _is_valid_block_id(block_id):
        if 0 < block_id < 255:
            return True
        else:
            raise CookieMyBadBlockId('block: {}'.format(block_id))

    def parse(self, cookie_string):
        """
        Парсит куку "my" и сохраняет ее содержимое в своей внутренней структуре.
        Кука подается на вход в виде строкового параметра. Метод ничего не возвращает.
        В случае неправильного формата куки, поданной на вход, метод кинет исключение CookieMyBadCookie.
        """
        cookie_content = base64.b64decode(cookie_string)

        content = list(reversed(map(ord, cookie_content)))
        result = {}
        first_byte = content.pop()

        if first_byte != CookieMy.START_BYTE:
            raise CookieMyBadCookie('bad staring byte')

        while len(content) > 1:
            block_id = content.pop()
            if block_id == 0x00:
                continue
            options_count = content.pop()
            options = []
            for option in range(options_count):
                option_value = content.pop()
                if option_value >> 7 == 1:
                    # Значение двух- или четырех- байтовое
                    option_value = (option_value << 8) | content.pop()
                    if option_value >> 14 == 3:
                        # значение четырехбайтовое
                        option_value = (option_value << 8) | content.pop()
                        option_value = (option_value << 8) | content.pop()
                        option_value = option_value & 0x0FFFFFFF
                    elif option_value >> 14 == 2:
                        # значение двухбайтовое
                        option_value = option_value & 0x7FFF
                    else:
                        raise CookieMyBadCookie('bad option bits')
                options.append(option_value)
            result[block_id] = options

        if content[0] != CookieMy.END_BYTE:
            raise CookieMyBadCookie('bad trailing byte')
        self.blocks = result
        return self

    def insert(self, block_id, block):
        """
        Вставляет блок в описание cookie "my".
        Принимает на вход id блока и массив целых чисел. Метод ничего не возвращает.
        Id блока может принимать значения от 0 до 255. Вектор, описывающий блок,
        не должен содержать отрицательные числа. В противном случае объект не сможет выполнить сериализацию.
        """
        if self._is_valid_block_id(block_id):
            if any(element < 0 for element in block):
                raise CookieMyBadBlockData('block data: {}'.format(block))
            self.blocks[block_id] = block
        return self

    def find(self, block_id):
        """
        Производит поиск блока в куке "my". Принимает на вход id блока.
        Id блока может принимать значения от 0 до 255. Возвращает описание блока - вектор целых чисел.
        В случае отсутствия запрашиваемого блока в куке "my", возвращается None.
        """
        if self._is_valid_block_id(block_id):
            return self.blocks.get(block_id, None)

    def keys(self):
        """
        Возвращает вектор id блоков, содержащихся в описании куки my.
        """
        return self.blocks.keys()

    def erase(self, block_id):
        """
        Удаляет блок из куки "my". Принимает на вход id блока. Id блока может принимать значения от 0 до 255.
        Метод ничего не возвращает."""
        if self._is_valid_block_id(block_id):
            if block_id in self.blocks:
                del self.blocks[block_id]
        return self

    def to_string(self):
        """
        Выполняет сериализацию объекта. Возвращает куку "my" в виде строки.
        """
        result = [CookieMy.START_BYTE]

        for block_id, options in self.blocks.items():
            result.append(block_id)
            result.append(len(options))
            for option in options:
                if option > 0x3FFF:
                    # четырехбайтовая опция - два первых бита должны быть равны 11
                    option = option | 0xC0000000
                    result.append((option & 0xFF000000) >> 24)
                    result.append((option & 0xFF0000) >> 16)
                    result.append((option & 0xFF00) >> 8)
                    result.append(option & 0xFF)
                elif option > 0x7F:
                    # двухбайтовая опция - первые два бита 10
                    option = option & 0xBFFF
                    option = option | 0x8000
                    result.append((option & 0xFF00) >> 8)
                    result.append(option & 0xFF)
                else:
                    # Однобайтовая опция
                    result.append(option)

        result.append(CookieMy.END_BYTE)
        return base64.b64encode(''.join(map(chr, result)))

    def set_lang(self, lang):
        """
        helper для установки значения в блок языка
        :param lang: string|int
        :return: None
        """
        code = LANG_CODES[lang] if lang in LANG_CODES else lang
        self.insert(0x27, [0, code])
        return self

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return 'CookieMy: {} {}'.format(json.dumps(self.blocks), self.to_string())
