from typing import Optional, Dict

from dmp_suite.yt import YTMeta, operation as op


def is_merge_required_by_attrs(
        dmp_content_revision: Optional[int],
        content_revision: int
) -> bool:
    """	
    Делаем мерж, если табличку трогали после последнего мержа	
    Чтобы сделать принудительный merge достаточно
    сдвинуть dmp_content_revision назад (или удалить атрибут)
    """
    if dmp_content_revision is None:
        return True

    return dmp_content_revision < content_revision


def is_compressed(attributes: Dict, meta: Optional[YTMeta] = None) -> bool:
    compression_codec = attributes.get('compression_codec')
    erasure_codec = attributes.get('erasure_codec')

    if meta is not None:
        if not compression_codec:
            compression_codec = op.get_yt_attr(meta, 'compression_codec')
        if not erasure_codec:
            erasure_codec = op.get_yt_attr(meta, 'erasure_codec')

    return compression_codec == 'brotli_8' and erasure_codec == 'lrc_12_2_2'
