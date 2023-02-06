import datetime
from typing import List
from typing import Optional
import uuid

import supportai_calls.models as db_models


def create_context_from_dialog(
        chat_id: str,
        ai_questions: List[str],
        user_answers: List[str],
        responses_features: Optional[List[List[dict]]] = None,
        policy_titles: Optional[List[str]] = None,
        num_records: Optional[int] = None,
        duration_s: Optional[int] = None,
        tags: Optional[List[str]] = None,
        tags_index: Optional[int] = None,
        version: Optional[str] = None,
        error_code: Optional[str] = None,
        error_code_index: Optional[int] = None,
        is_forwarded: bool = False,
):
    user_messages = [''] + user_answers
    ai_messages = ai_questions + ['']
    assert len(user_messages) == len(ai_messages)
    return create_context(
        chat_id,
        user_messages=user_messages,
        ai_messages=ai_messages,
        responses_features=responses_features,
        policy_titles=policy_titles,
        num_records=num_records,
        duration_s=duration_s,
        tags=tags,
        tags_index=tags_index,
        version=version,
        error_code=error_code,
        error_code_index=error_code_index,
        is_forwarded=is_forwarded,
        is_ended=not is_forwarded,
    )


def create_context(
        chat_id: str,
        created_at: Optional[datetime.datetime] = None,
        user_messages: Optional[List[str]] = None,
        ai_messages: Optional[List[str]] = None,
        responses_features: Optional[List[List[dict]]] = None,
        policy_titles: Optional[List[str]] = None,
        num_records: Optional[int] = None,
        duration_s: Optional[int] = None,
        tags: Optional[List[str]] = None,
        tags_index: Optional[int] = None,
        version: Optional[str] = None,
        error_code: Optional[str] = None,
        error_code_index: Optional[int] = None,
        is_ended: bool = True,
        is_forwarded: bool = False,
        callcenter_number: Optional[str] = None,
):
    if created_at is None:
        created_at = datetime.datetime.now().astimezone()

    first_record_ts = created_at
    last_record_ts = (
        first_record_ts + datetime.timedelta(seconds=duration_s)
        if duration_s
        else first_record_ts
    )

    context: dict = {'chat_id': chat_id, 'created_at': str(created_at)}
    records = []
    num_records = (
        len(user_messages)
        if user_messages is not None
        else len(ai_messages)
        if ai_messages is not None
        else len(policy_titles)
        if policy_titles is not None
        else len(responses_features)
        if responses_features is not None
        else num_records
        if num_records is not None
        else 1
    )
    if user_messages is None:
        user_messages = [f'user_reply_{i}' for i in range(num_records)]
        user_messages[0] = ''
    if ai_messages is None:
        ai_messages = [f'ai_question_{i + 1}' for i in range(num_records)]
        if is_ended:
            ai_messages[-1] = ''

    if policy_titles is not None:
        assert len(policy_titles) == num_records

    if responses_features is not None:
        assert len(responses_features) == num_records

    if error_code and error_code_index is None:
        error_code_index = 0

    for idx, (user_message, ai_message) in enumerate(
            zip(user_messages, ai_messages),
    ):
        request_features = [{'key': 'event_type', 'value': 'dial'}]
        if callcenter_number:
            request_features.append(
                {'key': 'callcenter_number', 'value': callcenter_number},
            )

        records.append(
            create_context_record(
                user_message=user_message,
                ai_message=ai_message,
                request_features=request_features if idx == 0 else None,
                response_features=responses_features[idx]
                if responses_features
                else None,
                tags=tags if tags_index is None or tags_index == idx else None,
                policy_title=policy_titles[idx] if policy_titles else None,
                version=version,
                error_code=error_code
                if error_code is not None
                and error_code_index is not None
                and error_code_index == idx
                else None,
                created_at=first_record_ts if idx == 0 else last_record_ts,
                is_forwarded=is_forwarded if idx == num_records - 1 else False,
            ),
        )
        if error_code_index is not None and error_code_index == idx:
            break

    context['records'] = records

    return context


def create_context_record(
        user_message: Optional[str] = '',
        ai_message: Optional[str] = 'some phrase',
        request_features: Optional[List[dict]] = None,
        response_features: Optional[List[dict]] = None,
        tags: Optional[List[str]] = None,
        policy_title: Optional[str] = None,
        version: Optional[str] = None,
        record_id: Optional[str] = None,
        created_at: Optional[datetime.datetime] = None,
        error_code: Optional[str] = None,
        is_forwarded: bool = False,
):
    request: dict = {'dialog': {'messages': []}, 'features': []}
    response: dict = {}
    record: dict = {'request': request, 'response': response}

    if user_message is not None:
        request['dialog']['messages'].append({'text': user_message})
    if ai_message is not None:
        response['reply'] = {'text': ai_message}
    if request_features:
        request['features'].extend(request_features)
    if response_features:
        response['features'] = {
            'features': [feature for feature in response_features],
            'probabilities': [],
        }
    if policy_title is not None:
        response['explanation'] = {'policy_titles': [policy_title]}
    if version is not None:
        response['version'] = version
    if tags:
        response['tag'] = {'add': [tag for tag in tags]}
    if record_id is not None:
        record['id'] = record_id
    if created_at is not None:
        record['created_at'] = str(created_at)
    if error_code is not None:
        request['features'].append({'key': 'error_code', 'value': error_code})
    if is_forwarded:
        response['forward'] = {'line': 'something'}

    return record


def get_preset_call(
        project_slug,
        *,
        direction=db_models.CallDirection.OUTGOING,
        call_service=db_models.CallService.IVR_FRAMEWORK,
        task_id='does not matter',
        phone='does not matter',
        personal_phone_id='does not matter',
        chat_id=None,
        features='[]',
        status=db_models.CallStatus.QUEUED,
        has_record=False,
        created=datetime.datetime.now().astimezone(),
        begin_at=None,
        end_at=None,
        initiated=None,
        attempt_number=0,
        attempts_left=None,
) -> db_models.Call:
    return db_models.Call(
        id=-1,
        project_slug=project_slug,
        direction=direction,
        call_service=call_service,
        task_id=task_id,
        phone=phone,
        personal_phone_id=personal_phone_id,
        chat_id=chat_id if chat_id else str(uuid.uuid4()),
        attempt_number=attempt_number,
        features=features,
        status=status,
        has_record=has_record,
        created=created,
        begin_at=begin_at,
        end_at=end_at,
        initiated=initiated,
        attempts_left=attempts_left,
    )
