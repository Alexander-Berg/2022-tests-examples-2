from dmp_suite import yt


class NoDocFieldTable(yt.YTTable):
    pass


class WrongTyprDocFieldTable(yt.YTTable):
    doc = yt.Int()


class RawTable(yt.YTTable):
    id = yt.Int(sort_key=True, sort_position=0)
    doc = yt.Any()


class PartitionedRawTable(RawTable):
    __partition_scale__ = yt.MonthPartitionScale('dt')

    dt = yt.Datetime()


class PdTable(yt.YTTable):
    phone = yt.String()
    phone_pd_id = yt.String()
    identification = yt.String()
    identification_pd_id = yt.String()
