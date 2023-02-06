import json
import io
import types
from StringIO import StringIO

import pytest

from pymlaas.util import request_helpers


def validate_rqc_response(response):
    req_fields = {
        'actual_result': (unicode, str),
        'bad_photos': [(unicode, str)],
        'exterior_result': (unicode, str),
        'interior_result': (unicode, str),
        'correct': [(unicode, str)],
        'exam_inspector': (unicode, str),
        'experiments_list': [(unicode, str)],
        'queue_name': (str, unicode),
        'incorrect': [(unicode, str)],
        'message_keys': [(unicode, str)],
        'result': (unicode, str),
        'result_mismatch_reason': ((unicode, str), types.NoneType),
        'unknown': [(unicode, str)],
        'prediction': {
            'block_tolerance': int,
            'success_result_flag': bool,
            'brand_color_recognition': {
                'brand': (unicode, str),
                'brand_confidence': float,
                'color': (unicode, str),
                'color_confidence': float,
                'confidence_threshold_brand': float,
                'confidence_threshold_color': float,
                'decision_brand': (unicode, str),
                'decision_color': (unicode, str)
            },
            'branding_recognition': {
                'branding_enabled_flag': bool,
                'decision': (unicode, str),
                'score': float,
                'threshold_success': float
            },
            'damage_recognition': {
                'decision': (unicode, str),
                'score': float,
                'threshold_block': float,
                'threshold_success': float
            },
            'interior_trash_recognition': {
                'decision': (unicode, str),
                'score': float,
                'threshold_block': float,
                'threshold_success': float
            },
            'seats_recognition': {
                'decision': (unicode, str),
                'score': float,
                'threshold_block': float,
                'threshold_success': float
            },
            'dirt_recognition': {
                'decision': (unicode, str),
                'score': float,
                'threshold_block': float,
                'threshold_success': float
            },
            'license_plate_recognition': {
                'back': (unicode, str),
                'decision': (unicode, str),
                'front': (unicode, str),
                'lower_bound': int,
                'upper_bound': int,
                'editdistance_back': int,
                'editdistance_front': int
            },
            'reason_enabled_flag_block': {
                'NO_BRANDING': bool,
                'NO_COLOR': bool,
                'NO_HARD_DEFECT': bool,
                'NO_MODEL': bool,
                'NO_NUMBER': bool,
                'NO_NUMBER_VIEW': bool,
                'NO_PHOTO': bool,
                'NO_QUALITY': bool,
                'YES_DIRTY': bool
            },
            'reason_enabled_flag_success': {
                'NO_BRANDING': bool,
                'NO_COLOR': bool,
                'NO_HARD_DEFECT': bool,
                'NO_MODEL': bool,
                'NO_NUMBER': bool,
                'NO_NUMBER_VIEW': bool,
                'NO_PHOTO': bool,
                'NO_QUALITY': bool,
                'YES_DIRTY': bool
            },
            'enabled_checks': {
                'brand_color': bool,
                'branding': bool,
                'damage': bool,
                'dirt': bool,
                'exterior_trash': bool,
                'interior_trash': bool,
                'license_plate': bool,
                'rugs': bool,
                'seatcase': bool,
                'seats': bool
            },
            'exterior_trash_recognition': {
                'block_tolerance': int,
                'decision': (unicode, str),
                'overall_trash_score': float,
                'probabilities': {
                    'back': {
                        'blurry': float,
                        'cropped': float,
                        'missType': float,
                        'trash': float
                    },
                    'front': {
                        'blurry': float,
                        'cropped': float,
                        'missType': float,
                        'trash': float
                    },
                    'left': {
                        'blurry': float,
                        'cropped': float,
                        'missType': float,
                        'trash': float
                    },
                    'right': {
                        'blurry': float,
                        'cropped': float,
                        'missType': float,
                        'trash': float
                    }
                },
               'threshold_block': float,
               'threshold_success': float
            },
            'meta_scores': {
                'meta_score_exterior': (float, types.NoneType),
                'meta_score_full_exam': (float, types.NoneType),
                'meta_score_interior': (float, types.NoneType)
            },
        }
    }
    request_helpers.validate_type(response, req_fields)


def test_empty_request(taxi_pyml):
    response = taxi_pyml.post('remote_quality_control', data={})
    assert response.status_code == 400


def test_good_response(taxi_pyml, load_json):
    data = {
        'exam_info': (StringIO(json.dumps(load_json('exam_info.json'))),
                      'exam_info.json')
    }
    response = taxi_pyml.post(
        'models/remote_quality_control',
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    validate_rqc_response(data)
