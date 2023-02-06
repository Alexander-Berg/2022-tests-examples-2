# -*- coding: utf-8 -*-

from sandbox.sandboxsdk.parameters import (
    SandboxStringParameter,
    ResourceSelector
)

from sandbox.projects import resource_types


class ImageReduceRes(ResourceSelector):
    name = 'imagereduce_binary'
    description = 'Бинарник imagereduce'
    resource_type = resource_types.CVDUP_IMAGEREDUCE


class TestToolRes(ResourceSelector):
    name = 'testtool_binary'
    description = 'Бинарник testtool'
    resource_type = resource_types.CVDUP_TESTTOOL


class TransformSpec(SandboxStringParameter):
    name = 'transform_spec'
    description = 'Image transformation to generate duplicates (see testtool help)'
    default_value = 'crop,0.6|resize,0.5,0.75|quality,20,90'


class GroupSizeSpec(SandboxStringParameter):
    name = 'group_size_spec'
    description = 'Group size specification (see testtool help)'
    default_value = 'geom,0.25'


class ImageSetRes(ResourceSelector):
    name = 'image_set'
    description = 'Archive of JPEG images'
    resource_type = resource_types.CVDUP_TEST_IMAGE_SET
    default_value = '190542095'


class ImageParserRes(ResourceSelector):
    name = 'imparser_binary'
    description = 'Бинарник imparsertest'
    resource_type = resource_types.CV_IMAGEPARSER


class ImageParserConfig(ResourceSelector):
    name = 'imparser_config'
    description = 'Конфиг для imparsertest'
    resource_type = resource_types.CVDUP_IMAGEPARSER_CONFIG


class MapreduceCluster(SandboxStringParameter):
    name = 'mr_cluster'
    description = 'MR cluster where all jobs will work'
    default_value = 'arnold.yt.yandex.net'


class MapreducePath(SandboxStringParameter):
    name = 'mr_path'
    description = 'Path on MR cluster for tables'
    default_value = 'cvdup/synthetic_test'


class YtToken(SandboxStringParameter):
    name = 'yt_token'
    description = 'YT token (leave empty to use robot-cvdup token)'
