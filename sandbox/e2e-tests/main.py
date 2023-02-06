import time
import logging
import requests
from requests.exceptions import RequestException

from concurrent.futures import ThreadPoolExecutor

from rtt_tasks import BuildRttTestsSuite
from hls_validator import validate_output_playlist, MediaStreamValidatorFailed
from canon_check import canon_assert


logging.basicConfig(level=logging.INFO)
Log = logging.getLogger(__name__)


def create_rtt_task(rtt_host, rtt_token, task):
    url = 'http://{}/create-task'.format(rtt_host)
    headers = {'Authorization': rtt_token}

    resp = None
    while True:
        try:
            resp = requests.post(url, json=task, headers=headers, timeout=25)
            resp.raise_for_status()
            break
        except RequestException as ex:
            Log.info('/create-task request error: {}'.format(ex))
            time.sleep(1)
            continue

    assert 'TaskId' in resp.json(), 'unexpected response: %s' % resp.json()

    return resp


def send_wait(rtt_host, rtt_token, run_cmd, ffprobe_bin, rtt_task):
    task = rtt_task.data
    Log.info('[{}] send task to the transcoder'.format(rtt_task.name))
    rs = create_rtt_task(rtt_host, rtt_token, task)

    rtt_id = rs.json()['TaskId']
    Log.info('[{}] task id: {}, input_url: {}'.format(rtt_task.name, rtt_id, task['InputVideoUrl']))

    last_warn_at = int(time.time())
    url = 'http://{}/get-task?id={}'.format(rtt_host, rtt_id)
    while True:
        try:
            rs = requests.get(url, timeout=25)
            rs.raise_for_status()
        except RequestException as ex:
            Log.info('/get-task request error: {}'.format(ex))
            time.sleep(1)
            continue

        assert 'Info' in rs.json(), 'unexpected {} response: {}'.format(url, rs.text)
        info = rs.json()['Info']

        now = int(time.time())
        if 'StartedAt' not in info:
            if now - info['CreatedAt'] > 30 * 60:
                raise Exception('task was not started {}'.format(url))
            if now - last_warn_at > 5 * 60:
                Log.info('[{}] still not started, id {}'.format(rtt_task.name, rtt_id))
                last_warn_at = now

        if info['StatusStr'] != 'ETSDone':
            assert info['StatusStr'] != 'ETSError', 'task %s failed: %s' % (rtt_id, info.get('Error'))
            time.sleep(5)
            continue

        checkable_urls = []
        for stream in info['Streams']:
            if stream['FormatStr'] == 'EHls' and ('DrmTypeStr' not in stream or stream['DrmTypeStr'] == 'EDT_NONE'):
                checkable_urls.append(stream['Url'])
            elif stream['FormatStr'] == 'EKaltura':
                checkable_urls.append(stream['Url'].replace('s3://', 'http://int.strm.yandex.net/vod/') + '/-/master.m3u8')

        return info, {}, []


def run_task(rtt_host, rtt_token, run_cmd, ffmpeg_bin, ffprobe_bin, validator_bin, task):
    Log.info('sending test: {} to transcoder'.format(task.name))
    start = int(time.time())
    info, ffp, checkable_urls = send_wait(rtt_host, rtt_token, run_cmd, ffprobe_bin, task)

    problems = []
    Log.info('check assertions for {}'.format(task.name))
    if task.assert_func:
        task.assert_func(info, ffp)
    elif task.canon_task_id:
        problems = canon_assert(info, task.canon_task_id, ffmpeg_bin, ffprobe_bin)
    else:
        raise Exception('no checks set')

    if validator_bin:
        for each in checkable_urls:
            Log.info('validating hls playlist for {}'.format(task.name))
            validate_output_playlist(validator_bin, each)
    proc_time = int(time.time()) - start
    Log.info('{}: took {} sec'.format(task.name, proc_time))
    return info['TaskId'], problems


def main(sandbox_task, config, run_cmd):
    Log.info('RTT host: {}'.format(config.rtt_host))
    Log.info('Ffprobe bin path: {}'.format(config.ffprobe_bin))
    Log.info('HLS validator bin path: {}'.format(config.validator_bin))
    results = []
    RttTestsSuite = BuildRttTestsSuite(config.rtt_host)
    with ThreadPoolExecutor(max_workers=32) as executor:
        tasks = []
        for rtt_task in RttTestsSuite:
            if not rtt_task.large or config.all_tests:
                tasks.append((executor.submit(run_task, config.rtt_host, config.rtt_token, run_cmd, config.ffmpeg_bin, config.ffprobe_bin, config.validator_bin, rtt_task), rtt_task))

        for ftr, rtt_task in tasks:
            try:
                task_id, problems = ftr.result()
                results.append({
                    'name': rtt_task.name,
                    'task': 'https://{}/get-task?id={}'.format(config.rtt_host, task_id),
                })
                if problems:
                    results[-1]['problems'] = problems
            except MediaStreamValidatorFailed as ex:
                Log.error('output stream validation failed {}: {}'.format(rtt_task.name, ex))
                results.append({
                    'name': rtt_task.name,
                    'mediastreamvalidator': ex.error_counts,
                })
            except Exception as ex:
                Log.exception('error while processing task {}'.format(rtt_task.name))
                results.append({
                    'name': rtt_task.name,
                    'error': str(ex),
                })

        sandbox_task.Parameters.test_results = sorted(results, key=lambda x: x['name'])
