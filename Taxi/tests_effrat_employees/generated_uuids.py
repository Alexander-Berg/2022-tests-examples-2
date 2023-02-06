import typing as tp


class GeneratedUuids:
    def __init__(self):
        self._uuid_by_identifier = {}
        self._identifier_by_uuid = {}

    def register_uuid(self, identifier: str, uuid: str):
        if identifier not in self._uuid_by_identifier:
            self._uuid_by_identifier[identifier] = []
        self._uuid_by_identifier[identifier].append(uuid)

        if uuid not in self._identifier_by_uuid:
            self._identifier_by_uuid[uuid] = []
        self._identifier_by_uuid[uuid].append(identifier)

    def get_uuid_by_identifier(
            self, login: str, domain: str,
    ) -> tp.Optional[str]:
        identifier = f'{login}:{domain}'
        if identifier not in self._uuid_by_identifier:
            return None
        return self._uuid_by_identifier[identifier][0]

    def get_identifier_by_uuid(self, uuid: str) -> tp.Optional[str]:
        if uuid not in self._identifier_by_uuid:
            return None
        return self._identifier_by_uuid[uuid][0]

    def get_all(self):
        return list(self._identifier_by_uuid.items())
