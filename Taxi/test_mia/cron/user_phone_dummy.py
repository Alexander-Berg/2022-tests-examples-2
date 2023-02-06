import typing


class UserPhoneWrapperDummy:
    def __init__(self, phone_to_ids: typing.Dict[str, typing.List[str]]):
        self.phone_to_ids = phone_to_ids
        self.id_to_phone: typing.Dict[str, str] = {}
        for phone, ids in phone_to_ids.items():
            for id_ in ids:
                self.id_to_phone[id_] = phone

    async def get_phone(self, phone_id: str):
        return self.id_to_phone[phone_id]

    async def retrieve_phones_ids(self, phones: typing.List[str]):
        return {
            phone: self.phone_to_ids.get(phone)
            for phone in phones
            if self.phone_to_ids.get(phone)
        }

    async def get_phones(self, phone_ids: typing.List[str]):
        return {id_: self.id_to_phone[id_] for id_ in phone_ids}
