import json
import logging
import os
import subprocess as sb
import tempfile


logging.basicConfig(level=logging.INFO)
Log = logging.getLogger(__name__)


class MediaStreamValidatorFailed(Exception):

    def __init__(self, description, error_counts={}):
        self.description = description
        self.error_counts = error_counts


def validate_output_playlist(hls_validator_bin, output_url):
    try:
        exec_log, errors = get_validator_result(hls_validator_bin, output_url)
    except sb.CalledProcessError as err:
        msg = 'playlist validation failed: {}'.format(err)
        Log.info(msg)
        raise MediaStreamValidatorFailed(msg)

    if exec_log.lower().find('error') != -1:
        Log.error('invalid playlist: {}'.format(output_url))
        Log.error('validator log:\n' + exec_log)
        raise MediaStreamValidatorFailed('validation errors', errors)

    Log.info('plyalist is valid')


def get_validator_result(hls_validator_bin, playlist_url):
    _, output_file_name = tempfile.mkstemp(suffix='.json')
    try:
        exec_log = sb.check_output([hls_validator_bin, '-O', output_file_name, playlist_url], stderr=sb.STDOUT).decode('utf-8')
        with open(output_file_name, 'r') as f:
            output = json.load(f)
            errors = {}
            if 'messages' in output:
                for m in output['messages']:
                    comment = m['errorComment']
                    errors[comment] = errors.get(comment, 0) + 1
            else:
                Log.info('validator output: ' + str(output))
    finally:
        os.remove(output_file_name)
    return exec_log, errors
