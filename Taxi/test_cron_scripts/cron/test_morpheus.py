import json
import typing
import xml.etree.ElementTree as etree

import pytest
import requests

from infranaim.models.configs import external_config


PATH_MONGO_DRIVERS_TO_ADD = 'mongo_drivers_to_add.json'


def test_empty_queue(
        run_morpheus_cron,
        get_mongo,
):
    external_config.INFRANAIM_MORPHEUS_ENABLE = True
    mongo = get_mongo
    mongo.drivers_to_add.delete_many({})
    run_morpheus_cron(mongo)


def _find_field_value(fields, id_):
    return next(
        (
            field['value']
            for field in fields
            if field['id'] == id_
        ),
        None,
    )


@pytest.fixture
def _check_sms(_load):
    def _do_it(
            language: str,
            sms_type: str,
            sms_docs: typing.List[dict],
            driver_doc: dict,
    ):
        if sms_type != 'ok':
            assert not sms_docs
            return
        template_id = 'rent'
        if driver_doc.get('model_full'):
            template_id = 'private_owners'
        true_sms = _load('tanker', 'sms_text_id')[language][template_id]
        assert true_sms.format(
            **driver_doc['processing_data']) == sms_docs[0]['text']
    return _do_it


@pytest.fixture
def _check_email(_load, personal_imitation):
    def _do_it(
            language: str,
            email_type: str,
            email_docs: typing.List[dict],
            driver_doc: dict,
    ):
        template_id = 'rent'
        if driver_doc.get('model_full'):
            template_id = 'private_owners'
        data = driver_doc['processing_data']
        doc = {
            'driver_license': personal_imitation(data['personal_license_id']),
            'name': data['name'],
            'phone': personal_imitation(data['personal_phone_id']),
        }
        if email_type != 'ok':
            assert not email_docs
            return
        true_email = _load(
            'tanker',
            'email_text_id')[language][template_id]
        true_subj = _load(
            'tanker',
            'email_subject_id')[language][template_id]
        assert true_email.format(**doc) == email_docs[0]['text']
        assert true_subj.format(**doc) == email_docs[0]['subject']
    return _do_it


@pytest.fixture
def assertion(load_json, _check_email, _check_sms):
    def _do_it(
            mongo,
            doc_type: str,
            driver_ownership: str,
            personal: str,
            sms_email_type: str,
            language: str,
    ):
        assert not list(mongo.drivers_to_add.find())
        processed = next(mongo.drivers_to_add_processed.find())
        doc = next(
            mongo.zendesk_tickets_to_update.find()
        )['upd_data'][0]['data']
        assert processed
        assert doc
        sms_docs = list(mongo.sms_pending.find())
        email_docs = list(mongo.email_pending.find())
        comment = doc['comment']['body']
        if driver_ownership == 'lock_stock_barrel':
            assert not sms_docs
            assert not email_docs
            assert 'Успех' in comment
        elif doc_type == 'valid' and personal == 'valid':
            _check_sms(
                language,
                sms_email_type,
                sms_docs,
                processed
            )
            _check_email(
                language,
                sms_email_type,
                email_docs,
                processed,
            )
            status = _find_field_value(doc['custom_fields'], 123)
            if driver_ownership == 'rent':
                assert status == 'поедет_в_таксопарк'
            else:
                assert status == 'заведен_в_таксометр'
        else:
            assert not sms_docs
            assert not email_docs
            assert (
                'Ошибка!\n\nНекорректный номер телефона!' in comment
            )
    return _do_it


@pytest.fixture
def _load(load_json):
    def _do_it(service: str, name: str, subname: str = ''):
        file = load_json('{}_{}.json'.format(service, name))
        if subname:
            file = file[subname]
        return file
    return _do_it


@pytest.fixture
def mocked_service(_load):
    def _do_it(service: str, name: str, subname: str = ''):
        data = _load(service, name, subname)
        result = requests.Response()
        result._content = bytes(json.dumps(data), encoding='utf8')
        result.status_code = 200
        return result
    return _do_it


@pytest.fixture
def exp3(_load):
    def _do_it(data: dict, attrs: dict):
        consumer = data['consumer']
        filename = consumer.replace('/', '_')
        case = attrs.get(filename)
        if filename in [
            'infranaim_morpheus_email_attributes',
            'infranaim_morpheus_sms_attributes',
        ]:
            rent = next(
                (
                    item['value']
                    for item in data['args']
                    if item['name'] == 'rent'
                ),
                None
            )
            assert isinstance(rent, bool)
            case = 'private_owners'
            if rent:
                case = 'rent'
        return _load('exp3', filename, case)
    return _do_it


def _convert_xml_part(group, name: str) -> dict:
    result = {}
    for unit in list(group):
        if unit.tag == name:
            for item in list(unit):
                key = item.tag
                value = item.text
                if key in result:
                    current_value = result[key]
                    if not isinstance(current_value, list):
                        result[key] = [current_value]
                    result[key].append(value)
                else:
                    result[key] = value
    return result


def _convert_xml_to_dict(xml: bytes) -> dict:
    root = etree.fromstring(xml)
    result = {
        'driver': {},
        'car': {},
    }
    for group in list(root):
        if group.tag == 'Drivers':
            result['driver'] = _convert_xml_part(group, 'Driver')
        elif group.tag == 'Cars':
            result['car'] = _convert_xml_part(group, 'Car')
    return result


def _check_xml(xml: bytes, exp3_attrs: dict, driver_ownership: str):
    xml = _convert_xml_to_dict(xml)
    if exp3_attrs['infranaim_morpheus_xml_find_balance'] == 'default':
        assert xml['driver']['BalanceLimit'] == '-50'
    else:
        assert xml['driver']['BalanceLimit'] == '5000'

    if driver_ownership == 'rent':
        assert not xml['car']
    else:
        if exp3_attrs['infranaim_morpheus_xml_find_categories'] == 'default':
            for category in [
                "ЭКОНОМ",
                "КОМФОРТ",
                "КОМФОРТ+",
                "БИЗНЕС",
                "МИНИВЭН",
                "УНИВЕРСАЛ"
            ]:
                assert category in xml['car']['Category']
        else:
            for category in [
                "СТАРТ",
                "ЭКОНОМ",
                "КОМФОРТ",
                "КОМФОРТ+",
                "БИЗНЕС",
                "МИНИВЭН",
                "УНИВЕРСАЛ"
            ]:
                assert category in xml['car']['Category']

    if exp3_attrs['infranaim_morpheus_xml_required_hiring_source'] == 'true':
        if exp3_attrs['infranaim_morpheus_xml_find_hiring_source'] == 'scouts':
            assert xml['driver']['HiringSource'] == 'scouts'
        else:
            assert xml['driver']['HiringSource'] == 'agents'
    else:
        assert not xml['driver'].get('HiringSource')

    if exp3_attrs['infranaim_morpheus_xml_required_hiring_type'] == 'true':
        if exp3_attrs['infranaim_morpheus_xml_find_hiring_type'] == 'paid_private':
            assert xml['driver']['HiringType'] == 'paid_private'
        else:
            assert xml['driver']['HiringType'] == 'paid_rent'
    else:
        assert not xml['driver'].get('HiringType')

    if exp3_attrs['infranaim_morpheus_xml_find_status'] == 'working':
        assert xml['driver']['Status'] == 'Работает'
    else:
        assert xml['driver']['Status'] == 'Не работает'

    if exp3_attrs['infranaim_morpheus_xml_required_algorithm'] == 'true':
        assert xml['driver']['RuleId']
    else:
        assert not xml['driver'].get('RuleId')


@pytest.mark.parametrize(
    'exp3_attrs',
    [
        {
            'infranaim_morpheus_choose_language': 'ru',
            'infranaim_morpheus_decision_choose_park': 'true',
            'infranaim_morpheus_decision_create_account': 'true',
            'infranaim_morpheus_xml_required_algorithm': 'false',
            'infranaim_morpheus_xml_required_hiring_source': 'true',
            'infranaim_morpheus_xml_required_hiring_type': 'true',
            'infranaim_morpheus_xml_find_balance': 'default',
            'infranaim_morpheus_xml_find_categories': 'default',
            'infranaim_morpheus_xml_find_hiring_source': 'scouts',
            'infranaim_morpheus_xml_find_hiring_type': 'paid_private',
            'infranaim_morpheus_xml_find_status': 'working',
        },
        {
            'infranaim_morpheus_choose_language': 'en',
            'infranaim_morpheus_decision_choose_park': 'true',
            'infranaim_morpheus_decision_create_account': 'true',
            'infranaim_morpheus_xml_required_algorithm': 'false',
            'infranaim_morpheus_xml_required_hiring_source': 'true',
            'infranaim_morpheus_xml_required_hiring_type': 'true',
            'infranaim_morpheus_xml_find_balance': '5000',
            'infranaim_morpheus_xml_find_categories': 'start',
            'infranaim_morpheus_xml_find_hiring_source': 'agents',
            'infranaim_morpheus_xml_find_hiring_type': 'paid_rent',
            'infranaim_morpheus_xml_find_status': 'not_working',
        },
        {
            'infranaim_morpheus_choose_language': 'ru',
            'infranaim_morpheus_decision_choose_park': 'true',
            'infranaim_morpheus_decision_create_account': 'true',
            'infranaim_morpheus_xml_required_algorithm': 'true',
            'infranaim_morpheus_xml_required_hiring_source': 'false',
            'infranaim_morpheus_xml_required_hiring_type': 'false',
            'infranaim_morpheus_xml_find_balance': '5000',
            'infranaim_morpheus_xml_find_categories': 'default',
            'infranaim_morpheus_xml_find_hiring_source': 'agents',
            'infranaim_morpheus_xml_find_hiring_type': 'paid_rent',
            'infranaim_morpheus_xml_find_status': 'working',
        }
    ]
)
@pytest.mark.parametrize('sms_email_type', ['ok', 'fail'])
@pytest.mark.parametrize('personal_response', ['valid', 'invalid'])
@pytest.mark.parametrize(
    'doc_type, driver_ownership',
    [
        ('valid', 'private_owner'),
        ('valid', 'rent'),
        ('valid', 'lock_stock_barrel'),
    ]
)
def test_full_process(
        mock_external_config,
        run_morpheus_cron,
        get_mongo,
        patch,
        load_json,
        personal,
        _load,
        mocked_service,
        exp3,
        assertion,
        exp3_attrs,
        sms_email_type,
        personal_response,
        doc_type,
        driver_ownership,
):
    @patch('infranaim.clients.personal.PreparedRequestMain._generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.experiments.ExperimentV2._prepare_headers')
    def _headers():
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal(personal_response, *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    @patch('infranaim.clients.gambling.Gambling._request')
    def _gambling(*args, **kwargs):
        assert args[1]
        assert isinstance(args[1], dict)
        return mocked_service('gambling', 'ok_park')

    @patch('infranaim.clients.experiments.ExperimentV2._post')
    def _exp3(data: dict):
        return exp3(data, exp3_attrs)

    @patch('infranaim.clients.taximeter.Taximeter._request')
    def _taximeter(*args, **kwargs):
        file = 'ok_driver_ok_vehicle'
        if driver_ownership == 'rent':
            file = 'ok_driver_rent'
        xml = args[2]
        _check_xml(xml, exp3_attrs, driver_ownership)
        return mocked_service('taximeter', file)

    @patch('infranaim.clients.morpheus.Morpheus._request_tanker')
    def _tanker(*args, **kwargs):
        if sms_email_type == 'fail':
            return {}
        keyset_id = kwargs['params']['keyset-id']
        return _load('tanker', keyset_id)

    mock_external_config(load_json('configs.json'))
    mongo = get_mongo
    doc = load_json(PATH_MONGO_DRIVERS_TO_ADD)[doc_type][driver_ownership]
    mongo.drivers_to_add.insert_one(doc)
    run_morpheus_cron(mongo)
    if driver_ownership == 'lock_stock_barrel':
        assert not _tanker.calls
        assert not _gambling.calls
        assert not _exp3.calls
    assertion(
        mongo,
        doc_type,
        driver_ownership,
        personal_response,
        sms_email_type,
        exp3_attrs['infranaim_morpheus_choose_language'],
    )
