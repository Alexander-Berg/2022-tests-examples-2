class RttTaskError():

    @staticmethod
    def WrongStreamsNumber(expected, real):
        return Exception('wrong streams number, expected: {}, real: {}'.format(expected, real))

    @staticmethod
    def WrongSrcDuration(expected, real):
        return Exception('wrong source duration, expected: {}, real: {}'.format(expected, real))

    @staticmethod
    def AbsentTargetStream(exp_width, exp_height):
        return Exception('can not found required stream: {}x{}'.format(exp_width, exp_height))

    @staticmethod
    def WrongTilesInfo(expected, real):
        return Exception('invalid timeline tiles, expected: {}, real: {}'.format(expected, real))

    @staticmethod
    def WrongThumbnailsNumber(expected, real):
        return Exception('wrong thumbnails number, expected: {}, real: {}'.format(expected, real))

    @staticmethod
    def WrongStatus(expected, real):
        return Exception('wrong status, expected: {}, real: {}'.format(expected, real))

    @staticmethod
    def WrongOutputUrl(expected, real):
        return Exception('wrong output url, expected: {}, real: {}'.format(expected, real))

    @staticmethod
    def WrongUrl(expected, real):
        return Exception('wrong url, expected: {}, real: {}'.format(expected, real))

    @staticmethod
    def WrongFormatStr(expected, real):
        return Exception('wrong format, expected: {}, real: {}'.format(expected, real))

    @staticmethod
    def WrongAudioStream():
        return Exception('does not have audio stream')

    @staticmethod
    def WrongVideoQualityStr(expected, real):
        return Exception('wrong video quality, expected: {}, real: {}'.format(expected, real))

    @staticmethod
    def WrongDrmTypeStr(expected, real):
        return Exception('wrong drm type, expected: {}, real: {}'.format(expected, real))

    @staticmethod
    def WrongTaskMeta():
        return Exception('wrong task meta')


class RttTask():

    def __init__(self, name, data, assert_func=None, canon_task_id=None, large=False):
        self.name = name
        self.data = data
        self.assert_func = assert_func
        self.large = large
        self.canon_task_id = canon_task_id


def BuildRttTestsSuite(rtt_host):
    RttTestsSuite = (
        RttTask(
            name='browser',
            data={
                'InputVideoUrl': 'https://s3.mdst.yandex.net/bg-store-test/3ef64ae2-85cf-44e1-b4ee-f7073a2a660a.mov',
                'Graph': 'browser',
                'GraphArgs': {
                    'ffmpeg_output_format': 'mp4,webm',
                    'content_version_id': '226308830513091477',
                    'ffpmeg_resolutions':
                    '[["169_1440p",["2560","1440","15000","128"]],["169_1080p",["1920","1080","10000","128"]],["169_768p",["1344","756","5000","128"]]]',
                    'ffpmeg_crossfade_duration': '3'
                },
                'KeepAspectRatio': True,
                'PreviewS3Params': {
                    'DirInsideBucket': 'vh/',
                    'KeyPrefix': '7175474872413375080',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'SegmentLengthSec': 4,
                'S3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'vod-content/e2e_browser/',
                    'KeyPrefix': '%TASK_ID%'
                },
                'OutputFormats': [
                    'EHls'
                ],
                'CaptureSceneChangeThumbs': True
            },
            canon_task_id='1cd2e9a8-92bbe266-cd90036a-b6e06d36',
            large=True,
        ),
        RttTask(
            name='zen_audio_pad',
            data={
                'CreateVideoPreview': True,
                'InputVideoUrl': 'https://vh-tusd.s3.mds.yandex.net/1afda64084d782fc8c7633d92e56b000',
                'Graph': 'regular-fast',
                'GraphArgs': {
                    'auto_subtitles': '1',
                    'max_screenshots_count': '10',
                    'vertical_mode': '1'
                },
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VisWordFeatures',
                    'VideoAdCutDetectionV2',
                    'VideoLogotypes',
                    'VideoToVideoV1CV'
                ],
                'CreateTimelineTiles': True,
                'PreviewS3Params': {
                    'DirInsideBucket': 'preview/',
                    'KeyPrefix': '9144539390680698513',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'S3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'vod-content/e2e_zen_audio_pad/',
                    'KeyPrefix': '%TASK_ID%'
                },
                'ThumbsInAvatars': True,
                'CaptureSceneChangeThumbs': True,
                'SegmentLengthSec': 4,
            },
            canon_task_id='5bbb0c92-57e97ae2-e21c5d43-e5592b90',
            large=True,
        ),
        RttTask(
            name='zen_large_meta_fps',
            data={
                'CreateVideoPreview': True,
                'InputVideoUrl': 'https://vh-tusd.s3.mds.yandex.net/a5d6f0fe3426aaff99b56d2fd41e8e2a',
                'Graph': 'regular-fast',
                'GraphArgs': {
                    'auto_subtitles': '1',
                    'max_screenshots_count': '10',
                    'vertical_mode': '1'
                },
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VisWordFeatures',
                    'VideoAdCutDetectionV2',
                    'VideoLogotypes',
                    'VideoToVideoV1CV'
                ],
                'CreateTimelineTiles': True,
                'PreviewS3Params': {
                    'DirInsideBucket': 'preview/',
                    'KeyPrefix': 'a5d6f0fe3426aaff99b56d2fd41e8e2a',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'S3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'vod-content/e2e_zen_large_meta_fps/',
                    'KeyPrefix': '%TASK_ID%'
                },
                'ThumbsInAvatars': True,
                'CaptureSceneChangeThumbs': True,
                'SegmentLengthSec': 4,
            },
            canon_task_id='9d584097-109633cb-e0546910-522884b7',
            large=True,
        ),
        RttTask(
            name='zen_silence',
            data={
                'CreateVideoPreview': True,
                'InputVideoUrl': 'https://vh-tusd.s3.mds.yandex.net/768ae2dee0c16859dad5a19b8d642dcc',
                'Graph': 'regular-fast',
                'GraphArgs': {
                    'auto_subtitles': '1',
                    'max_screenshots_count': '10',
                    'vertical_mode': '1'
                },
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VideoAdCutDetectionV2',
                    'VideoLogotypes'
                ],
                'CreateTimelineTiles': True,
                'PreviewS3Params': {
                    'DirInsideBucket': 'preview/',
                    'KeyPrefix': 'd32d2d05b1bd5e625a2d1a300e10357c',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'S3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'vod-content/e2e_zen_silence/',
                    'KeyPrefix': '%TASK_ID%'
                },
                'ThumbsInAvatars': True,
                'CaptureSceneChangeThumbs': True,
                'SegmentLengthSec': 4,
            },
            canon_task_id='2c108758-d747b2f8-428b5f9a-bd03cd8e',
            large=True,
        ),
        RttTask(
            name='zen_no_audio_stream',
            data={
                'CreateVideoPreview': True,
                'InputVideoUrl': 'https://vh-tusd.s3.mds.yandex.net/18721a9e1df877969e09dea23ca78d0e',
                'Graph': 'regular-fast',
                'GraphArgs': {
                    'auto_subtitles': '1',
                    'max_screenshots_count': '10',
                    'vertical_mode': '1'
                },
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VideoAdCutDetectionV2',
                    'VideoLogotypes'
                ],
                'CreateTimelineTiles': True,
                'PreviewS3Params': {
                    'DirInsideBucket': 'preview/',
                    'KeyPrefix': 'd32d2d05b1bd5e625a2d1a300e10357c',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'S3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'vod-content/e2e_zen_no_audio_stream/',
                    'KeyPrefix': '%TASK_ID%'
                },
                'ThumbsInAvatars': True,
                'CaptureSceneChangeThumbs': True,
                'SegmentLengthSec': 4,
            },
            canon_task_id='625c6ca0-c0120919-cf63fa6-f46d25e6',
            large=True,
        ),
        RttTask(
            name='adfox',
            data={
                'InputVideoUrl': 'https://adfox-content.s3.yandex.net/video_source/211130/adfox/1759590/4824200_1.cac1e8c5632983eab12d5f117319ca44.mp4',
                'Graph': 'bsvideo',
                'GraphArgs': {
                    'ffmpeg_output_format': 'hls,mp4,webm',
                    'measure_video_quality': '1',
                    'content_version_id': '18177694519744280173',
                    'ffpmeg_loudnorm': 'true',
                    'keep_aspect_ratio': 'true'
                },
                'KeepAspectRatio': True,
                'PreviewS3Params': {
                    'DirInsideBucket': 'vh/',
                    'KeyPrefix': '4829558877517198027',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'SegmentLengthSec': 4,
                'S3Params': {
                    'DirInsideBucket': 'vod-content/e2e-adfox/',
                    'KeyPrefix': '%TASK_ID%',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'OutputFormats': ['EHls'],
                'CaptureSceneChangeThumbs': True
            },
            canon_task_id='665dcd35-b1a5af1e-7b4c5d1f-29055fb1'
        ),
        RttTask(
            name='news',
            data={
                'CreateVideoPreview': True,
                'OutputFormat': 'EHls',
                'InputVideoUrl': 'https://video.inmedis.ru/STORAGE12/clip_bitrates/P0ktGbVgHYSnj6miuntlgYaEqEfrJYnd.mp4',
                'PublishLowResFirst': True,
                'Graph': 'regular-fast',
                'GraphArgs': {
                    'max_screenshots_count': '10'
                },
                'KeepAspectRatio': True,
                'CreateTimelineTiles': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV'
                ],
                'PreviewS3Params': {
                    'DirInsideBucket': 'ugc/',
                    'KeyPrefix': '1647304077815283995',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'SegmentLengthSec': 4,
                'S3Params': {
                    'DirInsideBucket': 'vod-content/e2e_news/',
                    'KeyPrefix': '%TASK_ID%',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'ThumbsInAvatars': True,
                'CaptureSceneChangeThumbs': True
            },
            canon_task_id='921464d9-791e327a-6d7608c7-7f2036c8'
        ),
        RttTask(
            name='canvas',
            data={
                'PreviewS3Params': {
                    'DirInsideBucket': 'ugc/',
                    'KeyPrefix': '3902410363915692888',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'S3Params': {
                    'DirInsideBucket': 'vod-content/canvas/',
                    'KeyPrefix': '%TASK_ID%',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'OutputFormat': 'EHls',
                'Graph': 'ad',
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'CaptureSceneChangeThumbs': True,
                'InputVideoUrl': 'https://storage.mds.yandex.net/get-bstor/5530270/a46e1397-81f3-482a-a36e-3a5316d51165.mp4',
                'GraphArgs': {
                    'vertical_mode': '1',
                    'output_formats': 'kaltura,hls,mp4,webm,webm_vp9',
                    'measure_video_quality': '1',
                    'crf': '19',
                    'thumbs_required': '1',
                    'zero_pass': '1',
                    'max_screenshots_count': '10'

                },
                'CreateVideoPreview': True,
                'KeepAspectRatio': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VisWordFeatures',
                ],
                'CreateTimelineTiles': True,
                'PublishLowResFirst': True,
                'SegmentLengthSec': 4,
                'ThumbsInAvatars': True
            },
            canon_task_id='39b2a93b-bdcc03ef-781390ec-3c75b0de',
        ),
        RttTask(
            name='canvas_no_audio',
            data={
                'PreviewS3Params': {
                    'DirInsideBucket': 'ugc/',
                    'KeyPrefix': '8386892814758191343',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'S3Params': {
                    'DirInsideBucket': 'vod-content/canvas_no_audio/',
                    'KeyPrefix': '%TASK_ID%',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'OutputFormat': 'EHls',
                'Graph': 'ad',
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'CaptureSceneChangeThumbs': True,
                'InputVideoUrl': 'https://storage.mds.yandex.net/get-bstor/5480250/f8799310-8a5e-41d8-a2af-3514265877cc.mp4',
                'GraphArgs': {
                    'vertical_mode': '1',
                    'output_formats': 'kaltura,hls,mp4,webm,webm_vp9',
                    'measure_video_quality': '1',
                    'crf': '19',
                    'thumbs_required': '1',
                    'zero_pass': '1',
                    'max_screenshots_count': '10'
                },
                'CreateVideoPreview': True,
                'KeepAspectRatio': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VisWordFeatures',
                ],
                'CreateTimelineTiles': True,
                'PublishLowResFirst': True,
                'SegmentLengthSec': 4,
                'ThumbsInAvatars': True
            },
            canon_task_id='f46c1445-c77110a3-5a1cd2-12c23317',
            large=True,
        ),
        RttTask(
            name='canvas_interlaced',
            data={
                'OutputFormat': 'EHls',
                'Graph': 'ad',
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'CaptureSceneChangeThumbs': True,
                'InputVideoUrl': 'https://storage.mds.yandex.net/get-bstor/5530270/0518f273-6fdf-4277-9912-5750d422acd0.mp4',
                'GraphArgs': {
                    'output_formats': 'kaltura,hls,mp4,webm,webm_vp9',
                    'zero_pass': '1',
                    'crf': '19',
                    'vertical_mode': '1',
                    'thumbs_required': '1',
                    'measure_video_quality': '1',
                    'max_screenshots_count': '10'
                },
                'CreateVideoPreview': True,
                'KeepAspectRatio': True,
                'PreviewS3Params': {
                    'DirInsideBucket': 'ugc/',
                    'KeyPrefix': '7069680664393175986',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VisWordFeatures'
                ],
                'CreateTimelineTiles': True,
                'S3Params': {
                    'DirInsideBucket': 'vod-content/canvas_interlaced/',
                    'KeyPrefix': '%TASK_ID%',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'PublishLowResFirst': True,
                'SegmentLengthSec': 4,
                'ThumbsInAvatars': True
            },
            canon_task_id='4630de54-efa8734a-bf9fa011-6001842c',
            large=True,
        ),
        RttTask(
            name='music',
            data={
                'CreateVideoPreview': True,
                'InputVideoUrl': 's3://music-videoclips-sources/file/2021-12/03-n/kwpzyayu/sample1/106a79ae879372a75712a1ebeb30c356.mp4',
                'Graph': 'regular',
                'GraphArgs': {
                    'output_formats': 'kaltura',
                    'ott_content_uuid': '4decac235c52b980bbf6e13d85421246',
                    'content_version_id': '4898062243773380400'
                },
                'KeepAspectRatio': True,
                'CreateTimelineTiles': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VideoLogotypes'
                ],
                'PreviewS3Params': {
                    'DirInsideBucket': 'vh/',
                    'KeyPrefix': '1583025538550058717',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'SegmentLengthSec': 4,
                'S3Params': {
                    'DirInsideBucket': 'content/1583025538550058717/',
                    'KeyPrefix': '%TASK_ID%',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'OutputFormats': [
                    'EHls'
                ],
                'CaptureSceneChangeThumbs': True
            },
            canon_task_id='8502775c-e2544de8-779782e6-bc315fde',
        ),
        RttTask(
            name='music_4k',
            data={
                'CreateVideoPreview': True,
                'InputVideoUrl': 's3://music-videoclips-sources/believe/2021-12/03-p/kwqixwyl/3616842482422/resources/86_3616842482422.mp4',
                'Graph': 'regular',
                'GraphArgs': {
                    'ott_content_uuid': '4b8713c32d69933799fccf165769bc97',
                    'content_version_id': '4451458897519843491'
                },
                'KeepAspectRatio': True,
                'CreateTimelineTiles': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VideoLogotypes'
                ],
                'PreviewS3Params': {
                    'DirInsideBucket': 'vh/',
                    'KeyPrefix': '13253045463228523435',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'SegmentLengthSec': 4,
                'S3Params': {
                    'DirInsideBucket': 'content/13253045463228523435/',
                    'KeyPrefix': '%TASK_ID%',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'OutputFormats': [
                    'EHls'
                ],
                'CaptureSceneChangeThumbs': True
            },
            canon_task_id='2dca49e7-5ef03a90-aa6c612c-a56b0df5',
            large=True,
        ),
        RttTask(
            name='q',
            data={
                'CreateVideoPreview': True,
                'OutputFormat': 'EHls',
                'InputVideoUrl': 'https://vh-tusd.s3.mds.yandex.net/8341ce960a69892f285333c6885acf3a',
                'PublishLowResFirst': True,
                'Graph': 'regular-fast',
                'GraphArgs': {
                    'max_screenshots_count': '10',
                    'thumbs_required': '1'
                },
                'KeepAspectRatio': True,
                'CreateTimelineTiles': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV'
                ],
                'PreviewS3Params': {
                    'DirInsideBucket': 'ugc/',
                    'KeyPrefix': '8341ce960a69892f285333c6885acf3a',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'SegmentLengthSec': 4,
                'S3Params': {
                    'DirInsideBucket': 'vod-content/8341ce960a69892f285333c6885acf3a/',
                    'KeyPrefix': '%TASK_ID%',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'ThumbsInAvatars': True,
                'CaptureSceneChangeThumbs': True,
                'WatermarkProps': {
                    'DistanceFromRight': 40,
                    'DistanceFromBottom': 40,
                    'WatermarkUrl': 'https://s3.mds.yandex.net/vh-q-converted/q-mask.png',
                    'DefaultInputWidth': 1920
                }
            },
            canon_task_id='435b884c-ad1ad3f1-94d9e51-713364f6',
        ),
        RttTask(
            name='games',
            data={
                'CreateVideoPreview': True,
                'OutputFormat': 'EHls',
                'InputVideoUrl': 'https://vh-tusd.s3.mds.yandex.net/80b4db4c27c37705a370197c5b5726c8',
                'PublishLowResFirst': True,
                'Graph': 'games',
                'GraphArgs': {
                    'output_formats': 'hls,mp4',
                    'max_screenshots_count': '10',
                    'thumbs_required': '1'
                },
                'KeepAspectRatio': True,
                'CreateTimelineTiles': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV'
                ],
                'PreviewS3Params': {
                    'DirInsideBucket': 'ugc/',
                    'KeyPrefix': '80b4db4c27c37705a370197c5b5726c8',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'SegmentLengthSec': 4,
                'S3Params': {
                    'DirInsideBucket': 'vod-content/',
                    'KeyPrefix': '80b4db4c27c37705a370197c5b5726c8',
                    'Bucket': 'vh-transcoder-test-converted'
                },
                'ThumbsInAvatars': True,
                'ExternalID': '5395507647327728259',
                'CaptureSceneChangeThumbs': True
            },
            canon_task_id='90b4213-d22c4435-a5ffc10d-804811f7',
        ),
        RttTask(
            name='zen_many_audio_streams',
            data={
                'InputVideoUrl': 'https://vh-tusd.s3.mds.yandex.net/3fc123bba01496aef6125de1e0dae081',
                'OutputFormat': 'EHls',
                'SegmentLengthSec': 4,
                'S3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'vod-content/6778970822339274191/',
                    'KeyPrefix': '%TASK_ID%'
                },
                'PublishLowResFirst': True,
                'KeepAspectRatio': True,
                'CaptureSceneChangeThumbs': True,
                'CreateVideoPreview': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VisWordFeatures',
                    'VideoAdCutDetectionV2',
                    'VideoLogotypes',
                    'VideoToVideoV1CV'
                ],
                'CreateTimelineTiles': True,
                'Graph': 'regular-fast',
                'GraphArgs': {
                    'max_screenshots_count': '10',
                    'auto_subtitles': '1',
                    'vertical_mode': '1',
                    'thumbs_required': '1'
                },
                'ExternalID': '6778970822339274191',
                'PreviewS3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'ugc/',
                    'KeyPrefix': '6778970822339274191'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'ThumbsInAvatars': True
            },
            large=True,
            canon_task_id='d8581743-c937370a-8472717f-d18845db'
        ),
        RttTask(
            name='zen_silence_parallel',
            data={
                'InputVideoUrl': 'https://vh-tusd.s3.mds.yandex.net/52fb9358d4bb2787d3a0df1495f4ac58',
                'OutputFormat': 'EHls',
                'SegmentLengthSec': 4,
                'S3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'vod-content/52fb9358d4bb2787d3a0df1495f4ac58/',
                    'KeyPrefix': '%TASK_ID%'
                },
                'PublishLowResFirst': True,
                'KeepAspectRatio': True,
                'CaptureSceneChangeThumbs': True,
                'CreateVideoPreview': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VisWordFeatures',
                    'VideoAdCutDetectionV2',
                    'VideoLogotypes',
                    'VideoToVideoV1CV'
                ],
                'CreateTimelineTiles': True,
                'Graph': 'regular-parallel',
                'GraphArgs': {
                    'executor_type': 'FRONTEND_EXECUTOR',
                    'vertical_mode': '1',
                    'max_screenshots_count': '10',
                    'frontend_url': 'http://video-faas-prestable.n.yandex-team.ru',
                    'auto_subtitles': '1',
                    'thumbs_required': '1'
                },
                'ExternalID': '1638517049060529216',
                'PreviewS3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'ugc/',
                    'KeyPrefix': '52fb9358d4bb2787d3a0df1495f4ac58'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'ThumbsInAvatars': True
            },
            canon_task_id='2c108758-d747b2f8-428b5f9a-bd03cd8e',
            large=True,
        ),
        RttTask(
            name='zen_no_audio_stream_parallel',
            data={
                'InputVideoUrl': 'https://vh-tusd.s3.mds.yandex.net/5313808cf757098ef53230afff781350',
                'OutputFormat': 'EHls',
                'SegmentLengthSec': 4,
                'S3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'vod-content/5313808cf757098ef53230afff781350/',
                    'KeyPrefix': '%TASK_ID%'
                },
                'PublishLowResFirst': True,
                'KeepAspectRatio': True,
                'CaptureSceneChangeThumbs': True,
                'CreateVideoPreview': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VisWordFeatures',
                    'VideoAdCutDetectionV2',
                    'VideoLogotypes',
                    'VideoToVideoV1CV'
                ],
                'CreateTimelineTiles': True,
                'Graph': 'regular-parallel',
                'GraphArgs': {
                    'frontend_url': 'http://video-faas-prestable.n.yandex-team.ru',
                    'executor_type': 'FRONTEND_EXECUTOR',
                    'auto_subtitles': '1',
                    'max_screenshots_count': '10',
                    'thumbs_required': '1',
                    'vertical_mode': '1'
                },
                'ExternalID': '1431481160999856793',
                'PreviewS3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'ugc/',
                    'KeyPrefix': '5313808cf757098ef53230afff781350'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'ThumbsInAvatars': True
            },
            canon_task_id='4acc1ffd-de34de3e-46962495-550296c6',
            large=True,
        ),
        RttTask(
            name='zen_many_audio_streams_parallel',
            data={
                'InputVideoUrl': 'https://vh-tusd.s3.mds.yandex.net/3fc123bba01496aef6125de1e0dae081',
                'OutputFormat': 'EHls',
                'SegmentLengthSec': 4,
                'S3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'vod-content/6778970822339274191/',
                    'KeyPrefix': '%TASK_ID%'
                },
                'PublishLowResFirst': True,
                'KeepAspectRatio': True,
                'CaptureSceneChangeThumbs': True,
                'CreateVideoPreview': True,
                'SignatureAlgo': [
                    'VisWord64v2',
                    'SoundChromaPrint',
                    'VideoPlusQueryV3CV',
                    'VideoClassifiers',
                    'VideoPlusQueryV4CV',
                    'VideoPlusQueryV5CV',
                    'VisWordFeatures',
                    'VideoAdCutDetectionV2',
                    'VideoLogotypes',
                    'VideoToVideoV1CV'
                ],
                'CreateTimelineTiles': True,
                'Graph': 'regular-parallel',
                'GraphArgs': {
                    'frontend_url': 'http://video-faas-prestable.n.yandex-team.ru',
                    'executor_type': 'FRONTEND_EXECUTOR',
                    'max_screenshots_count': '10',
                    'auto_subtitles': '1',
                    'vertical_mode': '1',
                    'thumbs_required': '1'
                },
                'ExternalID': '6778970822339274191',
                'PreviewS3Params': {
                    'Bucket': 'vh-transcoder-test-converted',
                    'DirInsideBucket': 'ugc/',
                    'KeyPrefix': '6778970822339274191'
                },
                'AvatarsParams': {
                    'Namespace': 'vh'
                },
                'ThumbsInAvatars': True
            },
            large=True,
            canon_task_id='d8581743-c937370a-8472717f-d18845db'
        ),
    )
    return RttTestsSuite
