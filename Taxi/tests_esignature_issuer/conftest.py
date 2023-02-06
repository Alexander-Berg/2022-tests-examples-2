# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import datetime
import random
import string
from typing import Optional
import uuid

from esignature_issuer_plugins import *  # noqa: F403 F401
import pytest
import pytz


@pytest.fixture
def get_req_headers():
    def wrapper(locale='en'):
        return {'Accept-Language': locale}

    return wrapper


@pytest.fixture
def mock_ucommunications(mockserver):
    @mockserver.json_handler('/ucommunications/general/sms/send')
    def send_sms(request):
        return {
            'message': 'OK',
            'code': '200',
            'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
            'status': 'sent',
        }

    return send_sms


@pytest.fixture(name='mock_ucommunications_429')
def _mock_ucommunications_429(mockserver):
    @mockserver.json_handler('/ucommunications/general/sms/send')
    def send_sms(request):
        return mockserver.make_response(
            status=429,
            json={
                'message': 'ERROR',
                'code': '429',
                'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
                'status': 'error',
            },
            headers={'X-Error-Reason': 'too-many-requests'},
        )

    return send_sms


@pytest.fixture
def fix_last_sent_at(pgsql):
    def wrapper(signer_id: str):
        cursor = pgsql['esignature_issuer'].conn.cursor()
        cursor.execute(
            f"""
            UPDATE esignature_issuer.signer_sms_counts
            SET sms_last_sent_at = make_timestamptz(2011, 11, 11, 11, 11, 11.0)
            WHERE signer_id = '{signer_id}';
            """,
        )

    return wrapper


@pytest.fixture
def create_signature(pgsql):
    def wrapper(
            *,
            signature_id: Optional[str] = None,
            signer_id: Optional[str] = None,
            signer_type: Optional[str] = None,
            properties: Optional[dict] = None,
            doc_id: Optional[str] = None,
            doc_type: Optional[str] = None,
            idempotency_token: Optional[str] = None,
            validation_id: Optional[str] = None,
            sms_per_signature_count: int = 1,
            sms_today_count: int = 1,
            sms_last_sent_at: Optional[datetime.datetime] = None,
            code: Optional[str] = None,
            check_count: int = 0,
    ) -> dict:
        if signature_id is None:
            signature_id = str(uuid.uuid4()).replace('-', '')
        if signer_id is None:
            signer_id = str(uuid.uuid4()).replace('-', '')
        if signer_type is None:
            signer_type = 'sender_to_driver'
        if properties is None:
            properties = {
                'sign_type': 'confirmation_code',
                'send_properties': [{'send_type': 'ucommunications_sms'}],
            }
        if doc_id is None:
            doc_id = str(uuid.uuid4()).replace('-', '')
        if doc_type is None:
            doc_type = 'cargo_claims'
        if idempotency_token is None:
            idempotency_token = str(uuid.uuid4())
        if validation_id is None:
            validation_id = str(uuid.uuid4()).replace('-', '')
        if sms_last_sent_at is None:
            sms_last_sent_at = datetime.datetime.utcnow() - datetime.timedelta(
                minutes=5,
            )
            sms_last_sent_at = sms_last_sent_at.replace(tzinfo=pytz.UTC)
        if code is None:
            code = ''.join(random.choice(string.digits) for _ in range(6))

        exportable = properties['sign_type'] == 'confirmation_code' and any(
            p['send_type'] == 'api' for p in properties['send_properties']
        )

        cursor = pgsql['esignature_issuer'].conn.cursor()

        cursor.execute(
            f"""
                INSERT INTO esignature_issuer.signatures (
                    signature_id,
                    signer_id,
                    signer_type,
                    sign_type,
                    doc_id,
                    doc_type,
                    idempotency_token,
                    validation_id,
                    sms_per_signature_count
                ) VALUES (
                    '{signature_id}',
                    '{signer_id}',
                    '{signer_type}',
                    '{properties['sign_type']}',
                    '{doc_id}',
                    '{doc_type}',
                    '{idempotency_token}',
                    '{validation_id}',
                    {sms_per_signature_count}
                );
                INSERT INTO esignature_issuer.signer_sms_counts (
                    signer_id, sms_today_count, sms_last_sent_at
                ) VALUES (
                    '{signer_id}',
                    {sms_today_count},
                    '{sms_last_sent_at}'
                ) ON CONFLICT (signer_id) DO UPDATE SET
                   sms_today_count =
                     signer_sms_counts.sms_today_count +
                     EXCLUDED.sms_today_count,
                   sms_last_sent_at =
                     GREATEST(signer_sms_counts.sms_last_sent_at,
                              EXCLUDED.sms_last_sent_at);
                """,
        )
        if properties['sign_type'] == 'confirmation_code':
            cursor.execute(
                f"""
                INSERT INTO esignature_issuer.verification_codes (
                    id,
                    code,
                    exportable,
                    check_count
                ) VALUES (
                    '{validation_id}',
                    '{code}',
                    {exportable},
                    {check_count}
                );
                """,
            )
        result = {
            'signature_id': signature_id,
            'signer_id': signer_id,
            'signer_type': signer_type,
            'properties': properties,
            'doc_id': doc_id,
            'doc_type': doc_type,
            'idempotency_token': idempotency_token,
            'validation_id': validation_id,
            'sms_per_signature_count': sms_per_signature_count,
            'sms_today_count': sms_today_count,
        }
        if properties['sign_type'] == 'confirmation_code':
            result.update({'code': code, 'check_count': check_count})
        return result

    return wrapper


@pytest.fixture
def get_signature(pgsql):
    def wrapper(signature_id: str, doc_type: str, doc_id: str) -> dict:
        si_fields = (
            'signature_id',
            'doc_type',
            'doc_id',
            'signer_id',
            'signer_type',
            'sign_type',
            'idempotency_token',
            'validation_id',
            'signed_at',
            'sms_per_signature_count',
        )
        sc_fields = ('sms_today_count', 'sms_last_sent_at')
        v_fields = ('code', 'exportable', 'check_count')

        fields_string = ','.join(
            [
                *[f'si.{field}' for field in si_fields],
                *[f'sc.{field}' for field in sc_fields],
                *[f'v.{field}' for field in v_fields],
            ],
        )

        cursor = pgsql['esignature_issuer'].conn.cursor()
        cursor.execute(
            f"""
            SELECT {fields_string} FROM esignature_issuer.signatures AS si
            LEFT JOIN esignature_issuer.signer_sms_counts AS sc
            ON si.signer_id = sc.signer_id
            LEFT JOIN esignature_issuer.verification_codes AS v
            ON si.validation_id = v.id
            WHERE si.signature_id = '{signature_id}' AND
                  si.doc_type = '{doc_type}' AND
                  si.doc_id = '{doc_id}';
            """,
        )
        row = list(cursor)[0]
        return {
            field: row[index]
            for index, field in enumerate([*si_fields, *sc_fields, *v_fields])
            if row[index] is not None
        }

    return wrapper


@pytest.fixture
def confirm_signature(pgsql):
    def wrapper(signature_id: str, doc_type: str, doc_id: str) -> None:
        cursor = pgsql['esignature_issuer'].conn.cursor()
        cursor.execute(
            f"""
            UPDATE esignature_issuer.signatures SET
            signed_at = NOW()
            WHERE signature_id = '{signature_id}' AND
                  doc_type = '{doc_type}' AND
                  doc_id = '{doc_id}';
            """,
        )

    return wrapper


@pytest.fixture
def get_correct_code(pgsql):
    def wrapper(signature_id: str, doc_type: str, doc_id: str) -> str:
        cursor = pgsql['esignature_issuer'].conn.cursor()
        cursor.execute(
            f"""
            SELECT code FROM esignature_issuer.verification_codes
            JOIN esignature_issuer.signatures
            ON signatures.validation_id=verification_codes.id
            WHERE signature_id = '{signature_id}' AND
            doc_type = '{doc_type}' AND
            doc_id = '{doc_id}'
            """,
        )
        result = list(cursor)
        assert result, f'No such signature id: {signature_id}'
        return result[0][0]

    return wrapper
