import base64
import collections
import datetime
import enum
import hashlib
import json
import random
import uuid

import dateutil.parser
import ecdsa  # pylint: disable=E0401
import jwt
import psycopg2
import pytz

JWT_HEADER = """{
  "alg": "ES256",
  "typ": "JWT"
}"""
JWT_QUERY_HASH_KEY = 'query_hash'
JWT_BODY_HASH_KEY = 'body_hash'
JWT_HEADER_NAME = 'X-JWT-Signature'
DEVICE_ID = '13c140cb-7dde-499c-be6e-57c010a45299'
GNSS = {  # wrong special for test
    'lat': -99,
    'lon': 199,
    'speed_kmph': -4.4,
    'accuracy_m': -3.3,
    'direction_deg': -5.5,
}
GPS = {'lat': 54.9885, 'lon': 73.3242}

TZ_INFO = psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)

MISSING_JWT_HEADER_FOR_UNREGISTERED = {
    JWT_HEADER_NAME: 'invalid JWT, but no public key anyway',
}
INVALID_SIGNATURE_MESSAGE = 'Failed to verify JWT'
RESPONSE_403_INVALID_SIGNATURE = {
    'code': '403',
    'message': INVALID_SIGNATURE_MESSAGE,
}
VERY_OLD_DATETIME = '1999-09-05T14:09:03Z'
RECOMMENDED_CHUNK_SIZE = 8388608

SIMPLE_CONFIG = {'info': {'key': 'value'}}
SIMPLE_CONFIG2 = {'info': {'key': 'value2'}}
SIMPLE_CONFIG3 = {'info': {'key': 'value3'}}
COMPLEX_CONFIG = {
    'info': {
        'str_key': 'str_val',
        'num_key': 123,
        'dict_key': {'in_key': 'in_val'},
        'bool_key': True,
    },
}


def make_ok_json_body(status, device_id=DEVICE_ID):
    return {
        'device_id': device_id,
        'timestamp': '2019-04-19T13:40:00Z',
        'status': status,
    }


def make_ok_status(
        is_gps_included=True,
        is_gnss_included=True,
        states_id=None,
        status_at='2019-04-19T13:37:00Z',
        sim_imsi='123456789',
        lte_traffic=None,
):
    status = {
        'status_at': status_at,
        'cpu_temperature': 32,
        'disk_bytes_free_space': 96929567296,
        'disk_bytes_total_space': 96929567297,
        'root_bytes_free_space': 96929567290,
        'root_bytes_total_space': 96929567291,
        'ram_bytes_free_space': 478150656,
        'software_version': '1.0-2',
        'sim_iccid': '90310410106543789301',
        'sim_imsi': sim_imsi,
        'sim_phone_number': '+7 (916) 617-82-58',
        'uptime_ms': 94608000000,
        'states_id': states_id,
    }
    if is_gps_included:
        status['gps_position'] = GPS
    if is_gnss_included:
        status['gnss'] = GNSS
    if lte_traffic:
        status['lte_traffic'] = lte_traffic
    return status


def response_400_not_registered(device_id):
    return {
        'code': '400',
        'message': f'Device with id {device_id} is not registered',
    }


def response_400_not_alive(device_id):
    return {
        'code': '400',
        'message': f'Device with id {device_id} is not alive',
    }


def str_to_bytes(str_):
    return bytes(str_, 'utf-8')


def bytes_to_str(bytes_):
    return str(bytes_)[2:-1].replace('\\n', '\n')


def datetime_to_timestring(datetime_):
    return '{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z'.format(
        datetime_.year,
        datetime_.month,
        datetime_.day,
        datetime_.hour,
        datetime_.minute,
        datetime_.second,
    )


def check_field(field_name, db_value, expected_value):
    if isinstance(db_value, datetime.datetime):
        expected_value = dateutil.parser.parse(expected_value)
    assert db_value == expected_value, field_name


def generate_key_pair():
    private_key = ecdsa.SigningKey.generate(
        curve=ecdsa.NIST256p, hashfunc=hashlib.sha256,
    )
    public_key = private_key.get_verifying_key()
    return private_key, public_key


def generate_mac():
    return '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def generate_version():
    return '{:1d}.{:03d}'.format(random.randint(1, 9), random.randint(0, 999))


def generate_imei():
    return '{:015d}'.format(random.randint(10 ** 14, 10 ** 15 - 1))


def generate_serial():
    return '{:010d}'.format(random.randint(0, 10 ** 10 - 1))


def generate_total_ram():
    return random.randint(262144, 1048576 * 6)  # 256 MiB to 6 GiB


def generate_cons_timestrings(quantity):
    datetime_ = datetime.datetime(2019, 10, 4, 4, 20, tzinfo=TZ_INFO)
    result = []
    for _ in range(quantity):
        step = datetime.timedelta(
            hours=random.randint(0, 100),
            minutes=random.randint(0, 60),
            seconds=random.randint(0, 60),
        )
        datetime_ += step
        result.append(datetime_to_timestring(datetime_))
    return result


def generate_timestring():
    return generate_cons_timestrings(1)[0]


def add_declared_device(
        pgsql,
        aes_key,
        serial_number,
        imei=generate_imei(),
        mac_wlan0=generate_mac(),
        mac_bluetooth=generate_mac(),
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        """
INSERT INTO signal_device_api.declared_devices
(
  serial_number,
  aes_key,
  imei,
  mac_wlan0,
  mac_bluetooth,
  created_at,
  updated_at)
VALUES
  ('{}', '{}', '{}', '{}', '{}',
   current_timestamp, current_timestamp)
RETURNING
  id;""".format(
            serial_number, aes_key, imei, mac_wlan0, mac_bluetooth,
        )
    )
    db.execute(query_str)
    db_notes = list(db)
    assert len(db_notes) == 1


def add_device_pg(
        pgsql,
        public_key_pem,
        device_primary_key,
        serial_number,
        public_id=None,
        is_alive=True,
        aes_key=None,
        is_drive_device=False,
):
    imei = generate_imei()
    mac_wlan0 = generate_mac()
    mac_bluetooth = generate_mac()
    if aes_key:
        add_declared_device(
            pgsql, aes_key, serial_number, imei, mac_wlan0, mac_bluetooth,
        )
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        """
WITH inserted_in_declared_devices AS (
  INSERT INTO signal_device_api.declared_devices
  (
    serial_number,
    aes_key,
    imei,
    mac_wlan0,
    mac_bluetooth,
    created_at,
    updated_at
  )
  VALUES
  (
    '{serial_number}', '{aes_key}', '{imei}', '{mac_wlan0}',
    '{mac_bluetooth}', current_timestamp, current_timestamp
  )
  ON CONFLICT DO NOTHING
)

INSERT INTO signal_device_api.devices
(
  id,
  is_alive,
  mac_wlan0,
  mac_eth0,
  mac_usb_modem,
  public_key,
  user_password,
  wifi_password,
  bluetooth_password,
  hardware_version,
  imei,
  serial_number,
  total_ram_bytes,
  public_id,
  created_at,
  updated_at,
  is_drive_device)
VALUES
  ({id}, {is_alive}, '{mac_wlan0}', '{mac_eth0}', '{mac_usb_modem}',
  '{public_key}', '{user_password}', '{wifi_password}',
  '{bluetooth_password}', '{hardware_version}', '{imei}', '{serial_number}',
  {total_ram_bytes}, '{public_id}', current_timestamp, current_timestamp,
  {is_drive_device})
RETURNING
  id;""".format(
            aes_key=uuid.uuid4().hex.upper(),
            mac_bluetooth=generate_mac(),
            id=device_primary_key,
            is_alive='TRUE' if is_alive else 'FALSE',
            mac_wlan0=generate_mac(),
            mac_eth0=generate_mac(),
            mac_usb_modem=generate_mac(),
            public_key=public_key_pem,
            user_password='user.p.a.s.s.w',
            wifi_password='wifi.p.a.s.s.w',
            bluetooth_password='bt.p.a.s.s.w',
            hardware_version=generate_version(),
            imei=generate_imei(),
            serial_number=serial_number,
            total_ram_bytes=generate_total_ram(),
            public_id=uuid.uuid4() if not public_id else public_id,
            is_drive_device=is_drive_device,
        )
    )
    db.execute(query_str)
    db_notes = list(db)
    assert len(db_notes) == 1
    return db_notes[0][0]


def add_device_return_private_key(
        pgsql,
        device_primary_key,
        device_id=None,
        is_alive=True,
        serial_number=generate_serial(),
        aes_key=None,
        is_drive_device=False,
):
    private_key, public_key = generate_key_pair()
    public_key_pem = bytes_to_str(public_key.to_pem())
    add_device_pg(
        pgsql,
        public_key_pem,
        device_primary_key,
        serial_number,
        device_id,
        is_alive,
        aes_key,
        is_drive_device,
    )
    return private_key


def add_log(
        pgsql,
        device_primary_key,
        file_id,
        size_bytes,
        is_uploaded,
        updated_at=None,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        """
INSERT INTO signal_device_api.logs (
  device_id,
  file_id,
  size_bytes,
  is_uploaded,
  updated_at)
VALUES
  ({}, '{}', {}, {}, {})
RETURNING
  id;""".format(
            device_primary_key,
            file_id,
            size_bytes,
            is_uploaded,
            '\'' + updated_at + '\''
            if updated_at is not None
            else 'CURRENT_TIMESTAMP',
        )
    )
    db.execute(query_str)
    db_notes = list(db)
    assert len(db_notes) == 1
    return db_notes[0][0]


def add_file(
        pgsql,
        serial_number,
        file_id,
        size_bytes,
        taken_at,
        is_uploaded,
        updated_at=None,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        """
INSERT INTO signal_device_api.files (
  serial_number,
  file_id,
  size_bytes,
  taken_at,
  is_uploaded,
  s3_path,
  created_at,
  updated_at)
VALUES
  ('{}', '{}', {}, '{}', {}, {}, CURRENT_TIMESTAMP, {})
RETURNING
  id;""".format(
            serial_number,
            file_id,
            size_bytes,
            taken_at,
            is_uploaded,
            '\'some_path\'' if is_uploaded else 'NULL',
            '\'' + updated_at + '\''
            if updated_at is not None
            else 'CURRENT_TIMESTAMP',
        )
    )
    db.execute(query_str)
    db_notes = list(db)
    assert len(db_notes) == 1
    return db_notes[0][0]


def add_photo(
        pgsql,
        device_primary_key,
        file_id,
        size_bytes,
        taken_at,
        is_uploaded,
        updated_at=None,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        """
INSERT INTO signal_device_api.photos (
  device_id,
  file_id,
  size_bytes,
  taken_at,
  is_uploaded,
  s3_path,
  created_at,
  updated_at)
VALUES
  ({}, '{}', {}, '{}', {}, {}, CURRENT_TIMESTAMP, {})
RETURNING
  id;""".format(
            device_primary_key,
            file_id,
            size_bytes,
            taken_at,
            is_uploaded,
            '\'some_path\'' if is_uploaded else 'NULL',
            '\'' + updated_at + '\''
            if updated_at is not None
            else 'CURRENT_TIMESTAMP',
        )
    )
    db.execute(query_str)
    db_notes = list(db)
    assert len(db_notes) == 1
    return db_notes[0][0]


def add_video(
        pgsql,
        device_primary_key,
        file_id,
        size_bytes,
        is_uploaded,
        started_at,
        finished_at,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        """
INSERT INTO signal_device_api.videos (
  device_id,
  file_id,
  size_bytes,
  started_at,
  finished_at,
  s3_path)
VALUES
  ({}, '{}', {}, '{}', {}, '{}')
RETURNING
  id;""".format(
            device_primary_key,
            file_id,
            size_bytes,
            started_at,
            '\'' + finished_at + '\'' if finished_at else 'NULL',
            '/some/path' if is_uploaded else None,
        )
    )
    db.execute(query_str)
    db_notes = list(db)
    assert len(db_notes) == 1
    return db_notes[0][0]


def check_log_in_db(
        pgsql,
        device_id,
        file_id,
        size_bytes,
        is_uploaded=False,
        updated_at_old=VERY_OLD_DATETIME,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        'SELECT '
        '  size_bytes, '
        '  is_uploaded,'
        '  updated_at AT TIME ZONE \'UTC\' '
        'FROM signal_device_api.logs '
        'WHERE device_id={} AND file_id=\'{}\';'.format(
            str(device_id), str(file_id),
        )
    )
    db.execute(query_str)
    db_result = [x for x in db][0]
    assert db_result[0] == size_bytes
    assert db_result[1] == is_uploaded
    assert db_result[2].replace(tzinfo=pytz.UTC) > dateutil.parser.parse(
        updated_at_old,
    )


def check_photo_in_db(
        pgsql,
        device_id,
        file_id,
        size_bytes,
        taken_at,
        is_uploaded=False,
        updated_at_old=VERY_OLD_DATETIME,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        'SELECT '
        '  size_bytes, '
        '  is_uploaded,'
        '  taken_at,   '
        '  s3_path,    '
        '  updated_at AT TIME ZONE \'UTC\' '
        'FROM signal_device_api.photos '
        'WHERE device_id={} AND file_id=\'{}\';'.format(
            str(device_id), str(file_id),
        )
    )
    db.execute(query_str)
    db_result = [x for x in db][0]
    assert db_result[0] == size_bytes
    assert db_result[1] == is_uploaded
    assert db_result[2] == dateutil.parser.parse(taken_at)
    assert is_uploaded is (db_result[3] is not None)
    assert db_result[4].replace(tzinfo=pytz.UTC) > dateutil.parser.parse(
        updated_at_old,
    )


def check_file_in_db(
        pgsql,
        serial_number,
        file_id,
        size_bytes,
        taken_at,
        is_uploaded=False,
        updated_at_old=VERY_OLD_DATETIME,
        file_info=None,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    if file_info is None:
        query_str = (
            'SELECT '
            '  size_bytes, '
            '  is_uploaded,'
            '  taken_at,   '
            '  s3_path,    '
            '  updated_at AT TIME ZONE \'UTC\' '
            'FROM signal_device_api.files '
            'WHERE serial_number=\'{}\' AND file_id=\'{}\';'.format(
                serial_number, str(file_id),
            )
        )
    else:
        query_str = (
            'SELECT '
            '  size_bytes, '
            '  is_uploaded,'
            '  taken_at,   '
            '  s3_path,    '
            '  updated_at AT TIME ZONE \'UTC\', '
            '  file_info '
            'FROM signal_device_api.files '
            'WHERE serial_number=\'{}\' AND file_id=\'{}\';'.format(
                serial_number, str(file_id),
            )
        )
    db.execute(query_str)
    db_result = [x for x in db][0]
    assert db_result[0] == size_bytes
    assert db_result[1] == is_uploaded
    assert db_result[2] == dateutil.parser.parse(taken_at)
    assert is_uploaded is (db_result[3] is not None)
    assert db_result[4].replace(tzinfo=pytz.UTC) > dateutil.parser.parse(
        updated_at_old,
    )
    if file_info is not None:
        assert db_result[5] == file_info


def check_video_chunk_in_db(
        pgsql,
        device_primary_key,
        file_id,
        size_bytes,
        offset_bytes,
        concat_status=None,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        'SELECT id, concat_status from signal_device_api.video_chunks WHERE '
        'device_id={} '
        'AND file_id=\'{}\' '
        'AND size_bytes={} '
        'AND offset_bytes={}'.format(
            device_primary_key, file_id, size_bytes, offset_bytes,
        )
    )
    db.execute(query_str)
    db_notes = [x for x in db]
    assert len(db_notes) == 1
    if concat_status is not None:
        assert db_notes[0][1] == concat_status


def check_video_in_db(pgsql, device_primary_key, file_id, size_bytes):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        'SELECT s3_path from signal_device_api.videos WHERE '
        'device_id={} '
        'AND file_id=\'{}\' '
        'AND size_bytes={}'.format(device_primary_key, file_id, size_bytes)
    )
    db.execute(query_str)
    db_notes = [x for x in db]
    assert len(db_notes) == 1
    assert db_notes[0][0] is not None


def get_is_tag_active(pgsql, *, park_id, car_id):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        'SELECT is_tag_active FROM signal_device_api.car_device_bindings '
        'WHERE park_id=\'{}\' '
        'AND car_id=\'{}\' '
        'AND detached_at IS NULL'.format(park_id, car_id)
    )
    db.execute(query_str)
    db_result = [x for x in db]
    assert len(db_result) == 1
    return db_result[0][0]


# TODO: add multimap ability
def encode_query(query):
    def _tobytes(value):
        if isinstance(value, bytes):
            return value
        return str(value).encode()

    if not query:
        return b''

    return b'?' + b'&'.join(
        b'='.join(
            base64.urlsafe_b64encode(_tobytes(part)).rstrip(b'=')
            for part in pair
        )
        for pair in collections.OrderedDict(sorted(query.items())).items()
    )


def generate_jwt(private_key, endpoint, query_params, body, is_body_json=True):
    query_encoded = str_to_bytes(endpoint) + encode_query(query_params)
    if is_body_json:
        body = str_to_bytes(json.dumps(body))
    payload = {
        JWT_QUERY_HASH_KEY: hashlib.sha256(query_encoded).hexdigest(),
        JWT_BODY_HASH_KEY: hashlib.sha256(body).hexdigest(),
    }
    # "=" padding is omitted as per RFC7515 section 2
    data_to_sign = (
        base64.urlsafe_b64encode(str_to_bytes(JWT_HEADER)).rstrip(b'=')
        + b'.'
        + base64.urlsafe_b64encode(str_to_bytes(json.dumps(payload))).rstrip(
            b'=',
        )
    )
    signature = base64.urlsafe_b64encode(
        private_key.sign(data_to_sign),
    ).rstrip(b'=')
    token = data_to_sign + str_to_bytes('.') + signature
    return bytes_to_str(token)


def make_jwt_headers(private_key, endpoint, params, body):
    return {JWT_HEADER_NAME: generate_jwt(private_key, endpoint, params, body)}


class JwtError(enum.Enum):
    NO_QUERY_HASH = 1
    NO_BODY_HASH = 2
    BAD_QUERY_HASH = 3
    BAD_BODY_HASH = 4
    INVALID_JWT_HEADER = 5
    INVALID_JWT_SIGNATURE = 6
    INVALID_JWT_STRUCTURE = 7


def generate_invalid_jwt(private_key, endpoint, query_params, body, jwt_error):
    query_encoded = str_to_bytes(endpoint) + encode_query(query_params)
    some_hash = (
        'b794385f2d1ef7ab4d9273d1906381b44f2f6f2588a3efb96a49188331984753'
    )
    payload = {
        JWT_QUERY_HASH_KEY: hashlib.sha256(query_encoded).hexdigest(),
        JWT_BODY_HASH_KEY: hashlib.sha256(body).hexdigest(),
    }
    if jwt_error == JwtError.NO_QUERY_HASH:
        payload = {JWT_BODY_HASH_KEY: hashlib.sha256(body).hexdigest()}
    elif jwt_error == JwtError.NO_BODY_HASH:
        payload = {
            JWT_QUERY_HASH_KEY: hashlib.sha256(query_encoded).hexdigest(),
        }
    elif jwt_error == JwtError.BAD_QUERY_HASH:
        payload = {
            JWT_QUERY_HASH_KEY: some_hash,
            JWT_BODY_HASH_KEY: hashlib.sha256(body).hexdigest(),
        }
    elif jwt_error == JwtError.BAD_BODY_HASH:
        payload = {
            JWT_QUERY_HASH_KEY: hashlib.sha256(query_encoded).hexdigest(),
            JWT_BODY_HASH_KEY: some_hash,
        }
    jwt_header = JWT_HEADER
    if jwt_error == JwtError.INVALID_JWT_HEADER:
        jwt_header = JWT_HEADER.replace('ES256', 'GarbageAlgo')
    data_to_sign = (
        base64.urlsafe_b64encode(str_to_bytes(jwt_header)).rstrip(b'=')
        + b'.'
        + base64.urlsafe_b64encode(str_to_bytes(json.dumps(payload))).rstrip(
            b'=',
        )
    )
    signature = base64.urlsafe_b64encode(
        private_key.sign(data_to_sign),
    ).rstrip(b'=')
    if jwt_error == JwtError.INVALID_JWT_SIGNATURE:
        signature = base64.urlsafe_b64encode(b'garbage_signature').rstrip(b'=')
    token = data_to_sign + str_to_bytes('.') + signature
    if jwt_error == JwtError.INVALID_JWT_STRUCTURE:
        token = str_to_bytes('_just_some_garbage_string_')
    return bytes_to_str(token)


def assert_now(actual):
    assert isinstance(actual, datetime.datetime)
    assert actual.tzinfo is not None
    delta = datetime.datetime.now(datetime.timezone.utc) - actual
    assert (
        datetime.timedelta() <= delta < datetime.timedelta(minutes=1)
    ), f'found too big delta {delta}'


def generate_jwt_aes(endpoint, aes_key, query_params, body, is_body_json=True):
    endpoint = endpoint.lstrip('/')
    query_encoded = endpoint.encode('utf-8') + encode_query(query_params)
    if is_body_json:
        body = json.dumps(body).encode('utf-8')
    query_hash = hashlib.sha256(query_encoded).hexdigest()
    body_hash = hashlib.sha256(body).hexdigest()
    payload = {'query_hash': query_hash, 'body_hash': body_hash}
    return jwt.encode(payload, aes_key, algorithm='HS256')


def check_alr_inserted(pgsql, *, serial_number: str, field_affected: str):
    pg_fields = [
        'v1_events_at',
        'v1_binaries_download_at',
        'v1_binaries_check_at',
        'v1_registration_at',
    ]
    assert field_affected in pg_fields

    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = f"""
        SELECT
          (v1_events_at IS NOT NULL),
          (v1_binaries_download_at IS NOT NULL),
          (v1_binaries_check_at IS NOT NULL),
          (v1_registration_at IS NOT NULL)
        FROM signal_device_api.api_last_responses
        WHERE serial_number = '{serial_number}'
        """
    db.execute(query_str)
    db_result = list(db)
    assert len(db_result) == 1

    db_expected_result = tuple(
        field_affected == pg_field for pg_field in pg_fields
    )
    assert db_result[0] == db_expected_result
