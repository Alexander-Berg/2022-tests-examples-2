import numpy as np

from taxi_pyml.remote_quality_control import logic_applier
from taxi_pyml.remote_quality_control import processor


def test_license_plate_processor(load_json):
    settings = load_json('settings.json')
    thresholds = settings['thresholds']
    proc = processor.LicensePlateProcessor(
        thresholds['license_plate']['lower_bound'],
        thresholds['license_plate']['upper_bound'],
        settings['lp_exam_countries'],
        settings['reg_exps']['license_plate_patterns'],
    )

    data = {
        'car_license_plate_number': 'X666XX66',
        'exam_country': 'россия',
        'recognized_license_plates': {
            'front': ['X666XX66'],
            'back': ['X666XX66'],
        },
    }

    result = proc.check(data)
    recognition = result['prediction']['license_plate_recognition']

    assert recognition['front'] == ['X666XX66']
    assert recognition['back'] == ['X666XX66']
    assert recognition['editdistance_front'] == [0]
    assert recognition['editdistance_back'] == [0]
    assert recognition['decision'] == 'success'

    data = {
        'car_license_plate_number': 'X666XX66',
        'exam_country': 'казахстан',
        'recognized_license_plates': {
            'front': ['X666XX66'],
            'back': ['X666XX66'],
        },
    }

    result = proc.check(data)
    recognition = result['prediction']['license_plate_recognition']

    assert recognition['front'] == []
    assert recognition['back'] == []
    assert recognition['editdistance_front'] == []
    assert recognition['editdistance_back'] == []
    assert recognition['decision'] == 'unknown'

    data = {
        'car_license_plate_number': 'X666YY66',
        'exam_country': 'россия',
        'recognized_license_plates': {
            'front': ['X666XX66'],
            'back': ['X999XX99'],
        },
    }

    result = proc.check(data)
    recognition = result['prediction']['license_plate_recognition']

    assert set(result['unknown']) == {'NO_NUMBER_VIEW', 'NO_NUMBER'}
    assert recognition['editdistance_front'] == [2]
    assert recognition['editdistance_back'] == [7]
    assert recognition['decision'] == 'unknown'

    data = {
        'car_license_plate_number': 'X666XX66',
        'exam_country': 'россия',
        'recognized_license_plates': {
            'front': ['X999XX99', 'X999XX97'],
            'back': ['X999XX99'],
        },
    }

    result = proc.check(data)
    recognition = result['prediction']['license_plate_recognition']

    assert result['incorrect'] == ['NO_NUMBER']
    assert result['correct'] == ['NO_NUMBER_VIEW']
    assert recognition['editdistance_front'] == [5, 5]
    assert recognition['editdistance_back'] == [5]
    assert recognition['decision'] == 'block'


def test_brand_processor(load_json):
    settings = load_json('settings.json')
    thresholds = settings['thresholds']

    id_to_brands_mapping = logic_applier.generate_mapping(
        load_json('id_to_brands.json'),
    )
    reasonable_brand_mapping = logic_applier.generate_mapping(
        load_json('reasonable_brands.json'),
    )

    proc = processor.BrandProcessor(
        thresholds['brand']['soft_threshold'],
        thresholds['brand']['hard_threshold'],
        id_to_brands_mapping,
        reasonable_brand_mapping,
    )

    index = 0
    brand_score = np.zeros(len(id_to_brands_mapping))
    brand_score[index] = 1
    data = {
        'brand_score': brand_score,
        'car_brand': 'hyundai',
        'car_model': 'solaris',
    }

    result = proc.check(data)
    recognition = result['prediction']['brand_recognition']

    assert 'hyundai solaris' in recognition['probable_brands']
    assert (
        recognition['reasonable_brands']
        == reasonable_brand_mapping['hyundai solaris']
    )
    assert recognition['confidence'] == 1
    assert recognition['decision'] == 'success'

    index = 100
    brand_score = np.zeros(len(id_to_brands_mapping))
    brand_score[index] = 1
    data = {
        'brand_score': brand_score,
        'car_brand': 'nissan',
        'car_model': '350z',
    }

    result = proc.check(data)
    recognition = result['prediction']['brand_recognition']

    assert recognition['probable_brands'] == ['other']
    assert recognition['reasonable_brands'] == ['other']
    assert recognition['confidence'] == 1
    assert recognition['decision'] == 'unknown'


def test_color_processor(load_json):
    settings = load_json('settings.json')
    thresholds = settings['thresholds']

    id_to_colors_mapping = logic_applier.generate_mapping(
        load_json('id_to_colors.json'),
    )
    reasonable_color_mapping = logic_applier.generate_mapping(
        load_json('reasonable_colors.json'),
    )

    proc = processor.ColorProcessor(
        thresholds['color']['soft_threshold'],
        thresholds['color']['hard_threshold'],
        id_to_colors_mapping,
        reasonable_color_mapping,
    )

    index = 6
    color_score = np.zeros(len(id_to_colors_mapping))
    color_score[index] = 1
    data = {'color_score': color_score, 'car_color': 'белый'}

    result = proc.check(data)
    recognition = result['prediction']['color_recognition']

    assert 'белый' in recognition['probable_colors']
    assert (
        recognition['reasonable_colors'] == reasonable_color_mapping['белый']
    )
    assert recognition['confidence'] == 1
    assert recognition['decision'] == 'success'

    index = 8
    color_score = np.zeros(len(id_to_colors_mapping))
    color_score[index] = 1
    data = {'color_score': color_score, 'car_color': 'серобуромалиновый'}

    result = proc.check(data)
    recognition = result['prediction']['color_recognition']

    assert recognition['probable_colors'] == ['other']
    assert recognition['reasonable_colors'] == ['other']
    assert recognition['confidence'] == 1
    assert recognition['decision'] == 'unknown'


def test_dirt_processor(load_json):
    settings = load_json('settings.json')
    thresholds = settings['thresholds']

    proc = processor.DirtProcessor(
        thresholds['dirt']['threshold_success'],
        thresholds['dirt']['threshold_block'],
    )

    result = proc.check(data={'dirt_score': 0.1})
    recognition = result['prediction']['dirt_recognition']

    assert recognition['score'] == 0.1
    assert recognition['decision'] == 'success'

    result = proc.check(data={'dirt_score': 0.99})
    recognition = result['prediction']['dirt_recognition']

    assert recognition['score'] == 0.99
    assert recognition['decision'] == 'block'

    result = proc.check(data={'dirt_score': 0.8})
    recognition = result['prediction']['dirt_recognition']

    assert recognition['score'] == 0.8
    assert recognition['decision'] == 'unknown'


def test_damage_processor(load_json):
    settings = load_json('settings.json')
    thresholds = settings['thresholds']

    proc = processor.DamageProcessor(
        thresholds['damage']['threshold_success'],
        thresholds['damage']['threshold_block'],
    )

    result = proc.check(data={'damage_score': 0.1})
    recognition = result['prediction']['damage_recognition']

    assert recognition['score'] == 0.1
    assert recognition['decision'] == 'success'

    result = proc.check(data={'damage_score': 0.99})
    recognition = result['prediction']['damage_recognition']

    assert recognition['score'] == 0.99
    assert recognition['decision'] == 'block'

    result = proc.check(data={'damage_score': 0.8})
    recognition = result['prediction']['damage_recognition']

    assert recognition['score'] == 0.8
    assert recognition['decision'] == 'unknown'


def test_exterior_trash_processor(load_json):
    queue_settings = load_json('queue_settings.json')
    queue_configs = logic_applier.create_queue_configs(
        queue_settings['default_config'],
        queue_settings['queue_configs_override'],
        queue_settings['queues'],
    )
    settings = load_json('settings.json')
    thresholds = settings['thresholds']

    proc = processor.ExtTrashProcessor(
        thresholds['exterior_trash']['threshold_success'],
        thresholds['exterior_trash']['threshold_block'],
        queue_configs['default']['block_tolerance_trash'],
    )

    result = proc.check(data={'exterior_trash_score': 0.1})
    recognition = result['prediction']['exterior_trash_recognition']

    assert recognition['score'] == 0.1
    assert recognition['decision'] == 'success'

    result = proc.check(data={'exterior_trash_score': 0.99})
    recognition = result['prediction']['exterior_trash_recognition']

    assert recognition['score'] == 0.99
    assert recognition['decision'] == 'block'

    result = proc.check(data={'exterior_trash_score': 0.8})
    recognition = result['prediction']['exterior_trash_recognition']

    assert recognition['score'] == 0.8
    assert recognition['decision'] == 'unknown'


def test_interior_trash_processor(load_json):
    settings = load_json('settings.json')
    thresholds = settings['thresholds']

    proc = processor.IntTrashProcessor(
        thresholds['interior_trash']['threshold_success'],
        thresholds['interior_trash']['threshold_block'],
    )

    result = proc.check(data={'interior_trash_score': 0.1})
    recognition = result['prediction']['interior_trash_recognition']

    assert recognition['score'] == 0.1
    assert recognition['decision'] == 'success'

    result = proc.check(data={'interior_trash_score': 100.0})
    recognition = result['prediction']['interior_trash_recognition']

    assert recognition['score'] == 100.0
    assert recognition['decision'] == 'block'

    result = proc.check(data={'interior_trash_score': 50.0})
    recognition = result['prediction']['interior_trash_recognition']

    assert recognition['score'] == 50.0
    assert recognition['decision'] == 'unknown'


def test_rugs_processor(load_json):
    settings = load_json('settings.json')
    thresholds = settings['thresholds']

    proc = processor.RugsProcessor(
        thresholds['rugs']['threshold_success'],
        thresholds['rugs']['threshold_block'],
    )

    result = proc.check(data={'rugs_score': 0.1})
    recognition = result['prediction']['rugs_recognition']

    assert recognition['score'] == 0.1
    assert recognition['decision'] == 'success'

    result = proc.check(data={'rugs_score': 100.0})
    recognition = result['prediction']['rugs_recognition']

    assert recognition['score'] == 100.0
    assert recognition['decision'] == 'block'

    result = proc.check(data={'rugs_score': 50.0})
    recognition = result['prediction']['rugs_recognition']

    assert recognition['score'] == 50.0
    assert recognition['decision'] == 'unknown'


def test_seats_processor(load_json):
    settings = load_json('settings.json')
    thresholds = settings['thresholds']

    proc = processor.SeatsProcessor(
        thresholds['seats']['threshold_success'],
        thresholds['seats']['threshold_block'],
    )

    result = proc.check(data={'seats_score': 0.1})
    recognition = result['prediction']['seats_recognition']

    assert recognition['score'] == 0.1
    assert recognition['decision'] == 'success'

    result = proc.check(data={'seats_score': 100.0})
    recognition = result['prediction']['seats_recognition']

    assert recognition['score'] == 100.0
    assert recognition['decision'] == 'block'

    result = proc.check(data={'seats_score': 50.0})
    recognition = result['prediction']['seats_recognition']

    assert recognition['score'] == 50.0
    assert recognition['decision'] == 'unknown'


def test_seatcase_processor(load_json):
    settings = load_json('settings.json')
    thresholds = settings['thresholds']

    proc = processor.SeatcaseProcessor(
        thresholds['seatcase']['threshold_success'],
        thresholds['seatcase']['threshold_block'],
    )

    result = proc.check(data={'seatcase_score': 0.1})
    recognition = result['prediction']['seatcase_recognition']

    assert recognition['score'] == 0.1
    assert recognition['decision'] == 'success'

    result = proc.check(data={'seatcase_score': 100.0})
    recognition = result['prediction']['seatcase_recognition']

    assert recognition['score'] == 100.0
    assert recognition['decision'] == 'block'

    result = proc.check(data={'seatcase_score': 50.0})
    recognition = result['prediction']['seatcase_recognition']

    assert recognition['score'] == 50.0
    assert recognition['decision'] == 'unknown'
