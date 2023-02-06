import typing


class TimezoneWrapperDummy:
    def __init__(self, zones: typing.Dict[str, str]):
        self.zones = zones

    async def get_timezones(
            self, zones: typing.List[str],
    ) -> typing.Dict[str, str]:
        result = {}
        for zone in zones:
            if zone in self.zones:
                result[zone] = self.zones[zone]
        return result
