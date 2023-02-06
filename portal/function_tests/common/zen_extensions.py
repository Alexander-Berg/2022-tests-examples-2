# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

# Общие проверки для old_format и zen_id_format
def base_check(item):
    if item.get('heavy_id') is not None:
        assert item.get('block') is None, 'Block has heavy_id and block at the same time'
    elif item.get('block') is not None:
        assert item.get('heavy_id') is None, 'Block has heavy_id and block at the same time'
    else:
        assert 0, 'Missed heavy_id or block'

# Проверка наличия zen_id
def zen_id_check(item):
    assert item.get('zen_id') is not None, 'Missed zen_id'

# Проверка отсутствия zen_id
def no_zen_id_check(item):
    assert item.get('zen_id') is None, 'There should be no zen_id'

# Проверка position
def position_check(item):
    assert item.get('position') >= 0, 'Bad block position'

# Проверка короткого формата ответа
def short_format_check(item):
    assert item.get('type') is not None, 'Missed type for short_format'
    assert item.get('heavy') is not None, 'Missed heavy for short_format'
    assert item.get('id') is not None, 'Missed id for short_format'
    assert 'block' not in item, 'Key block is forbidden in short answer'

# Проверка наличия data в block
def block_data_check(item):
    if item.get('heavy_id') is None:
        block = item.get('block')
        assert block.get('data') is not None, 'Bad block data'
