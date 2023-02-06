import requests
import re
import json
import time
import subprocess

_EQ_FIELDS = [
    'Status',
    'StatusStr',
    'FileSize',
    'DurationMs',
    'InputWidth',
    'InputHeight',
    'HasAudioStream',
    'PreviewStatus',
    'PreviewStatusStr',
    'SignatureStatus',
    'SignatureStatusStr',
    'Framerate',
    'SpeechToTextStatus',
    'SpeechToTextStatusStr',
    'MD5',
    'Silence',
]

_HAS_FIELDS = [
    'FirstFrameUrl',
    'StartedAt',
    'SpeechToTextReadyAt',
    'SignaturesReadyAt',
    'LowResReadyAt',
    'AllResReadyAt',
    'GraphBuild',
    'CreatedAt',
    'ChangedAt',
    'SignaturesUrl',
    'SpeechToTextUrl',
]

_LIST_LEN_FIELDS = [
    'Thumbnails',
    'Streams',
    'Previews',
]


def _download_json(url):
    for a in range(5):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if a == 4:
                raise
            time.sleep(1)


def _get_canon_info(canon_task_id):
    return _download_json('http://video-faas.n.yandex-team.ru/get-task?id=' + canon_task_id)['Info']


def canon_assert(info, canon_task_id, ffmpeg_bin, ffprobe_bin):
    canon_info = _get_canon_info(canon_task_id)

    problems = []

    for field in _EQ_FIELDS:
        if field in canon_info:
            if field in info:
                if info[field] != canon_info[field]:
                    problems.append('wrong {} value {}, expected {}'.format(field, info[field], canon_info[field]))
            else:
                problems.append('no {} in task info'.format(field))
        elif field in info:
            problems.append('{} in task info, but not in canon'.format(field))

    for field in _HAS_FIELDS:
        if field in canon_info:
            if field not in info:
                problems.append('no {} in task info'.format(field))
        elif field in info:
            problems.append('{} in task info, but not in canon'.format(field))

    for field in _LIST_LEN_FIELDS:
        if field in canon_info:
            if field in info:
                if len(info[field]) != len(canon_info[field]):
                    problems.append('wrong {} length {}, expected {}'.format(field, len(info[field]), len(canon_info[field])))
            else:
                problems.append('no {} in task info'.format(field))
        elif field in info:
            problems.append('{} in task info, but not in canon'.format(field))

    problems.extend(_check_signatures(info, canon_info, 'SignaturesUrl'))
    problems.extend(_check_signatures(info, canon_info, 'SpeechToTextUrl'))
    problems.extend(_check_streams(info, canon_info, ffmpeg_bin))
    return problems


def _check_signatures(info, canon_info, f):
    canon_sigs_url = canon_info.get(f)
    sigs_url = info.get(f)
    if not canon_sigs_url or not sigs_url:
        return []
    problems = []
    canon_sigs = _download_json(canon_sigs_url)
    sigs = _download_json(sigs_url)
    if len(canon_sigs) != len(sigs):
        problems.append('unexpected signatures count {}, expected {}'.format(len(sigs), len(canon_sigs)))
    for key in canon_sigs:
        if key not in sigs:
            problems.append('no signature {}'.format(key))
    return problems


def _check_streams(info, canon_info, ffmpeg_bin):
    def stream_key(s):
        return ' '.join(map(str, [s['FormatStr'],
                        s.get('Width'),
                        s.get('Height'),
                        s.get('VideoCodecStr'),
                        s.get('AudioCodecStr'),
                        s.get('TagsStr')]))

    canon_streams = {}
    for s in canon_info['Streams']:
        canon_streams[stream_key(s)] = s
    streams = {}
    for s in info['Streams']:
        streams[stream_key(s)] = s

    problems = []
    for key in canon_streams:
        if key not in streams:
            problems.append('no stream {}'.format(key))
            continue

        canon = canon_streams[key]
        current = streams[key]
        if canon['FormatStr'] in ['EMp4', 'EWebm']:
            if 'ByteSize' in canon:
                if abs(canon['ByteSize'] - current['ByteSize']) > 0.02 * canon['ByteSize']:
                    problems.append('large stream size diff. expected {}, was {} for {}'.format(canon['ByteSize'], current['ByteSize'], key))
            if 'Bitrate' in canon:
                if abs(canon['Bitrate'] - current['Bitrate']) > 0.02 * canon['Bitrate']:
                    problems.append('large stream bitrate diff. expected {}, was {} for {}'.format(canon['Bitrate'], current['Bitrate'], key))
            if 'RfcCodecs' in canon:
                if canon['RfcCodecs'] != current['RfcCodecs']:
                    problems.append('RfcCodecs diff. expected {}, was {} for {}'.format(canon['RfcCodecs'], current['RfcCodecs'], key))
        elif canon['FormatStr'] == 'EKaltura':
            problems.extend(_check_kaltura(current, canon, ffmpeg_bin))

    return problems


def _check_kaltura(stream, canon_stream, ffmpeg_bin):
    current_json = _download_json(stream['Url'].replace('s3://', 'http://s3.mds.yandex.net/') + '.json')
    canon_json = _download_json(canon_stream['Url'].replace('s3://', 'http://s3.mds.yandex.net/') + '.json')

    problems = []
    if current_json.get('version') != canon_json.get('version'):
        problems.append('kaltura version diff. expected {}, was {}'.format(canon_json.get('version'), current_json.get('version')))

    current_vr = sorted(current_json.get('video_rendition_sets') or [], key=lambda x: x['label'])
    canon_vr = sorted(canon_json.get('video_rendition_sets') or [], key=lambda x: x['label'])
    if len(current_vr) != len(canon_vr):
        problems.append('kaltura video renditions count diff. expected {}, was {}'.format(len(canon_vr), len(current_vr)))

    current_ar = sorted(current_json.get('audio_rendition_sets') or [], key=lambda x: x['language'])
    canon_ar = sorted(canon_json.get('audio_rendition_sets') or [], key=lambda x: x['language'])
    if len(current_vr) != len(canon_vr):
        problems.append('kaltura audio renditions count diff. expected {}, was {}'.format(len(canon_ar), len(current_ar)))

    for i in range(len(current_ar)):
        problems.extend(_check_kaltura_audio_rendition(current_ar[i], canon_ar[i], ffmpeg_bin))

    return problems


def _check_kaltura_audio_rendition(audio_rendition, canon_audio_rendition, ffmpeg_bin):
    problems = []
    for field in ['label', 'language']:
        if audio_rendition[field] != canon_audio_rendition[field]:
            problems.append('kaltura audio {} diff. expected {}, was {}'.format(field, canon_audio_rendition[field], audio_rendition[field]))

    current_audios = sorted(audio_rendition['audios'], key=lambda x: x['id'])
    canon_audios = sorted(canon_audio_rendition['audios'], key=lambda x: x['id'])
    if len(current_audios) != len(canon_audios):
        problems.append('kaltura audios count diff. expected {}, was {}'.format(len(current_audios), len(canon_audios)))

    for j in range(len(current_audios)):
        audio_current = current_audios[j]
        audio_canon = canon_audios[j]
        for field in ['id', 'sampling_rate', 'codecs', 'autoselect']:
            if audio_current[field] != audio_canon[field]:
                problems.append('kaltura audio {} diff. expected {}, was {}'.format(field, audio_canon[field], audio_current[field]))
        if abs(audio_canon['bandwidth'] - audio_current['bandwidth']) > 0.02 * audio_canon['bandwidth']:
            problems.append('large kaltura audio bitrate diff. expected {}, was {}'.format(audio_canon['bandwidth'], audio_current['bandwidth']))

        assert len(audio_canon['segments']) == 1
        assert len(audio_current['segments']) == 1

        current_segment = audio_current['segments'][0]
        canon_segment = audio_canon['segments'][0]

        if abs(current_segment['duration'] - canon_segment['duration']) > 0.02 * canon_segment['duration']:
            problems.append('large kaltura audio duration diff. expected {}, was {}'.format(canon_segment['duration'], current_segment['duration']))

        #  current_loudness = _get_loudness(ffmpeg_bin, 'http://s3.mds.yandex.net/' + current_segment['path'])
        #  problems.append('loudness: ' + str(current_loudness))
        # canon_loudness = _get_loudness(ffmpeg_bin, 'http://s3.mds.yandex.net/' + canon_segment['path'])
        # if abs(current_loudness - canon_loudness) > 0.1:
        #     problems.append('large kaltura audio loudness diff. expected {}, was {}'.format(canon_loudness, current_loudness))

    return problems


def _get_loudness(ffmpeg_bin, url):
    out = subprocess.check_output([
        ffmpeg_bin,
        '-xerror',
        '-nostdin',
        '-i', url,
        '-filter_complex', '[0:a]loudnorm=i=-23:lra=7:print_format=json:tp=-1.0',
        '-f', 'null',
        '-'
    ], stderr=subprocess.STDOUT)
    match = re.findall(r'\[Parsed_loudnorm_(\d+).*\]([^\}]+\})', out)
    assert match
    return float(json.loads(match[0])['input_i'])
