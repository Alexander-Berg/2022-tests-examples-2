import tests_bank_notifications.defaults as defaults


class Event:
    def __init__(
            self,
            event_id=None,
            bank_uid=None,
            req_id=None,
            created_at=None,
            event_type=None,
            defaults_group=None,
            priority=None,
            title=None,
            description=None,
            action=None,
            merge_key=None,
            merge_status=None,
            experiment=None,
            title_tanker_args=None,
            description_tanker_args=None,
            payload=None,
    ):
        self.event_id = str(event_id)
        self.bank_uid = bank_uid
        self.req_id = str(req_id)
        self.created_at = created_at
        self.event_type = event_type
        self.defaults_group = defaults_group
        self.priority = priority
        self.title = title
        self.description = description
        self.action = action
        self.merge_key = merge_key
        self.merge_status = merge_status
        self.experiment = experiment
        self.title_tanker_args = title_tanker_args
        self.description_tanker_args = description_tanker_args
        self.payload = payload

    def __eq__(self, other):
        if not isinstance(other, Event):
            return False
        return (
            self.to_json() == other.to_json()
            and (
                self.priority is None
                or other.priority is None
                or self.priority == other.priority
            )
            and self.merge_status == other.merge_status
            and self.experiment == other.experiment
        )

    def to_json(self):
        res = {
            defaults.EVENT_TYPE_KEY: self.event_type,
            defaults.DEFAULTS_GROUP_KEY: self.defaults_group,
        }
        if self.title is not None:
            title_object = {defaults.KEY_KEY: self.title}
            if self.title_tanker_args is not None:
                title_object[defaults.ARGS_KEY] = self.title_tanker_args
            res[defaults.TITLE_KEY] = title_object
        if self.description is not None:
            description_object = {defaults.KEY_KEY: self.description}
            if self.description_tanker_args is not None:
                description_object[
                    defaults.ARGS_KEY
                ] = self.description_tanker_args
            res[defaults.DESCRIPTION_KEY] = description_object
        if self.action is not None:
            res[defaults.ACTION_KEY] = self.action
        if self.merge_key is not None:
            res[defaults.MERGE_KEY_KEY] = self.merge_key
        if self.experiment is not None:
            res[defaults.EXPERIMENT_KEY] = self.experiment
        if self.payload is not None:
            res[defaults.PAYLOAD_KEY] = self.payload
        return res

    @staticmethod
    def from_json(j):
        return Event(
            event_type=j.get(defaults.EVENT_TYPE_KEY),
            defaults_group=j.get(defaults.DEFAULTS_GROUP_KEY),
            priority=j.get(defaults.PRIORITY_KEY),
            title=j.get(defaults.TITLE_KEY).get(defaults.KEY_KEY)
            if j.get(defaults.TITLE_KEY) is not None
            else None,
            title_tanker_args=j.get(defaults.TITLE_KEY).get(defaults.ARGS_KEY)
            if j.get(defaults.TITLE_KEY) is not None
            and j.get(defaults.TITLE_KEY).get(defaults.ARGS_KEY) is not None
            else None,
            description=j.get(defaults.DESCRIPTION_KEY).get(defaults.KEY_KEY)
            if j.get(defaults.DESCRIPTION_KEY) is not None
            else None,
            description_tanker_args=j.get(defaults.DESCRIPTION_KEY).get(
                defaults.ARGS_KEY,
            )
            if j.get(defaults.DESCRIPTION_KEY) is not None
            and j.get(defaults.DESCRIPTION_KEY).get(defaults.ARGS_KEY)
            is not None
            else None,
            action=j.get(defaults.ACTION_KEY),
            merge_key=j.get(defaults.MERGE_KEY_KEY),
            experiment=j.get(defaults.EXPERIMENT_KEY),
            payload=j.get(defaults.PAYLOAD_KEY),
        )

    @staticmethod
    def default(
            event_id=defaults.gen_uuid(),
            bank_uid=defaults.BUID,
            req_id=defaults.gen_uuid(),
            event_type=defaults.EVENT_TYPE,
            defaults_group=defaults.DEFAULTS_GROUP,
            priority=defaults.PRIORITY,
            title=defaults.TITLE,
            description=defaults.DESCRIPTION,
            action=defaults.ACTION,
            merge_key=None,
            merge_status=None,
            experiment=None,
            title_tanker_args=None,
            description_tanker_args=None,
            payload=None,
    ):
        return Event(
            event_id=event_id,
            bank_uid=bank_uid,
            req_id=req_id,
            event_type=event_type,
            defaults_group=defaults_group,
            priority=priority,
            title=title,
            description=description,
            action=action,
            merge_key=merge_key,
            merge_status=merge_status,
            experiment=experiment,
            title_tanker_args=title_tanker_args,
            description_tanker_args=description_tanker_args,
            payload=payload,
        )


class SendEventsRequest:
    def __init__(
            self,
            req_id=None,
            consumer=None,
            idempotency_token=None,
            bank_uid=None,
            events=None,
            status_code=None,
            code=None,
            message=None,
            event_ids=None,
            created_at=None,
            all_param=None,
    ):
        self.req_id = str(req_id)
        self.consumer = consumer
        self.idempotency_token = str(idempotency_token)
        self.bank_uid = bank_uid
        if events is None or isinstance(events[0], Event):
            self.events = events
        else:
            self.events = [Event.from_json(it) for it in events]
        self.status_code = status_code
        self.code = code
        self.message = message
        self.event_ids = (
            None if events is None else [ev.event_id for ev in self.events]
        )
        self.created_at = created_at
        self.all_param = all_param

        if self.bank_uid == defaults.ALL_KEY:
            self.bank_uid = None
            self.all_param = True

    def __eq__(self, other):
        if not isinstance(other, SendEventsRequest):
            return False
        # do not compare req_id, event_ids and created_at
        return (
            self.consumer == other.consumer
            and self.idempotency_token == other.idempotency_token
            and self.bank_uid == other.bank_uid
            and self.events == other.events
            and self.status_code == other.status_code
            and self.code == other.code
            and self.message == other.message
            and self.all_param == other.all_param
        )

    def headers(self):
        return {'X-Idempotency-Token': self.idempotency_token}

    def to_json(self):
        json_rep = {
            defaults.CONSUMER_KEY: self.consumer,
            defaults.BUID_KEY: self.bank_uid,
            defaults.EVENTS_KEY: [event.to_json() for event in self.events],
        }

        if self.all_param is not None:
            json_rep['all'] = self.all_param

        return json_rep

    @staticmethod
    def default(
            req_id=defaults.gen_uuid(),
            consumer=defaults.CONSUMER,
            idempotency_token=defaults.gen_uuid(),
            bank_uid=defaults.BUID,
            all_param=None,
            events=[
                Event.default(),
            ],  # pylint: disable=dangerous-default-value
            status_code=200,
            code=None,
            message=None,
    ):
        return SendEventsRequest(
            req_id=req_id,
            consumer=consumer,
            idempotency_token=idempotency_token,
            bank_uid=bank_uid,
            all_param=all_param,
            events=events,
            status_code=status_code,
            code=code,
            message=message,
            event_ids=None
            if events is None
            else [ev.event_id for ev in events],
        )


class Mark:
    def __init__(
            self, mark_id, bank_uid, req_id, created_at, mark_type, event_id,
    ):
        self.mark_id = str(mark_id)
        self.bank_uid = bank_uid
        self.req_id = str(req_id)
        self.created_at = created_at
        self.mark_type = mark_type
        self.event_id = str(event_id)

    def __eq__(self, other):
        if not isinstance(other, Mark):
            return False
        return (
            self.mark_id == other.mark_id
            and self.bank_uid == other.bank_uid
            and self.req_id == other.req_id
            and self.created_at == other.created_at
            and self.mark_type == other.mark_type
            and self.event_id == other.event_id
        )


class MarkEventsRequest:
    def __init__(
            self,
            req_id=None,
            initiator_type=None,
            initiator_id=None,
            idempotency_token=None,
            bank_uid=None,
            event_type=None,
            event_ids=None,
            mark_type=None,
            status_code=None,
            code=None,
            message=None,
            created_at=None,
            merge_key=None,
    ):
        self.req_id = str(req_id)
        self.initiator_type = initiator_type
        self.initiator_id = initiator_id
        self.idempotency_token = str(idempotency_token)
        self.bank_uid = bank_uid
        self.event_type = event_type
        if isinstance(event_ids, str):
            event_ids = event_ids[1:-1].split(',')
        if event_ids is None:
            self.event_ids = None
        else:
            self.event_ids = list()
            for id in event_ids:
                self.event_ids.append(str(id))
        self.mark_type = mark_type
        self.status_code = status_code
        self.code = code
        self.merge_key = merge_key
        self.message = message
        self.created_at = created_at

    def __eq__(self, other):
        if not isinstance(other, MarkEventsRequest):
            return False
        # do not compare req_id and created_at
        return (
            self.initiator_type == other.initiator_type
            and self.initiator_id == other.initiator_id
            and self.idempotency_token == other.idempotency_token
            and self.bank_uid == other.bank_uid
            and self.event_type == other.event_type
            and self.event_ids == other.event_ids
            and self.mark_type == other.mark_type
            and self.status_code == other.status_code
            and self.code == other.code
            and self.message == other.message
            and self.merge_key == other.merge_key
        )


class S2SMarkEventsRequest(MarkEventsRequest):
    def headers(self):
        return {'X-Idempotency-Token': self.idempotency_token}

    def to_json(self):
        res = {
            defaults.MARK_TYPE_KEY: self.mark_type,
            defaults.CONSUMER_KEY: self.initiator_id,
            defaults.BUID_KEY: self.bank_uid,
        }
        if self.event_type:
            res[defaults.EVENT_TYPE_KEY] = self.event_type
        if self.event_ids:
            res[defaults.EVENT_IDS_KEY] = self.event_ids
        if self.merge_key:
            res[defaults.MERGE_KEY_KEY] = self.merge_key
        return res

    @staticmethod
    def default(
            req_id=defaults.gen_uuid(),
            idempotency_token=defaults.gen_uuid(),
            initiator_type=defaults.CONSUMER_TYPE,
            initiator_id=defaults.CONSUMER,
            bank_uid=defaults.BUID,
            event_type=None,
            event_ids=[
                defaults.gen_uuid(),
            ],  # pylint: disable=dangerous-default-value
            mark_type=defaults.MARK_TYPE,
            status_code=200,
            code=None,
            message=None,
            merge_key=None,
    ):
        return S2SMarkEventsRequest(
            req_id=req_id,
            initiator_type=initiator_type,
            initiator_id=initiator_id,
            idempotency_token=idempotency_token,
            bank_uid=bank_uid,
            event_type=event_type,
            event_ids=event_ids,
            mark_type=mark_type,
            status_code=status_code,
            code=code,
            message=message,
            merge_key=merge_key,
        )


class SDKMarkEventsRequest(MarkEventsRequest):
    def headers(self):
        headers = defaults.auth_headers()
        headers['X-Idempotency-Token'] = self.idempotency_token
        return headers

    def to_json(self):
        res = {defaults.MARK_TYPE_KEY: self.mark_type}
        if self.event_type:
            res[defaults.EVENT_TYPE_KEY] = self.event_type
        if self.event_ids:
            res[defaults.EVENT_IDS_KEY] = self.event_ids
        return res

    @staticmethod
    def default(
            req_id=defaults.gen_uuid(),
            idempotency_token=defaults.gen_uuid(),
            initiator_type=defaults.BUID_TYPE,
            bank_uid=defaults.BUID,
            event_type=None,
            event_ids=[
                defaults.gen_uuid(),
            ],  # pylint: disable=dangerous-default-value
            mark_type=defaults.MARK_TYPE,
            status_code=200,
            code=None,
            message=None,
            merge_key=None,
    ):
        return SDKMarkEventsRequest(
            req_id=req_id,
            initiator_type=initiator_type,
            initiator_id=bank_uid,
            idempotency_token=idempotency_token,
            bank_uid=bank_uid,
            event_type=event_type,
            event_ids=event_ids,
            mark_type=mark_type,
            status_code=status_code,
            code=code,
            message=message,
            merge_key=merge_key,
        )
