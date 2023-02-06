import pytest

import sandbox.common.types.statistics as ctss
from sandbox.services.modules.statistics_processor.schemas import yt_schemas


class TestSchema(object):
    def test__meta(self):
        with pytest.raises(TypeError):
            class A(yt_schemas.YTSignal):
                meta = None

        with pytest.raises(TypeError) as exc:
            class B(yt_schemas.YTSignal):
                meta = yt_schemas.YTSignalMetadata(
                    signal_type=ctss.YTSignalType.API_CALL_YT,
                    path="//home",
                )

        assert "Missing table metadata values: proxy" in str(exc)

        class C(yt_schemas.YTSignal):
            meta = yt_schemas.YTSignalMetadata(signal_type="A", path="B", proxy=yt_schemas.Proxy.HAHN)

        assert C.meta.proxy == yt_schemas.Proxy.HAHN

    def test__schema(self):
        class TestSignal(yt_schemas.YTSignal):
            meta = yt_schemas.YTSignalMetadata(
                signal_type=ctss.YTSignalType.API_CALL_YT,
                path="//home",
                proxy=yt_schemas.Proxy.ARNOLD,
            )

            datetime = yt_schemas.StringColumn()
            user = yt_schemas.StringColumn(required=False)
            ip = yt_schemas.Int64Column()

        assert [_["name"] for _ in TestSignal.schema] == ["datetime", "user", "ip"]
        assert TestSignal.schema == [
            dict(name="datetime", required=True, type="string"),
            dict(name="user", required=False, type="string"),
            dict(name="ip", required=True, type="int64"),
        ]

        with pytest.raises(ValueError) as exc:
            TestSignal.make(ip="1234")

        assert "Missing fields: datetime" in str(exc)

        with pytest.raises(ValueError) as exc:
            TestSignal.make(ip="1234", datetime="5678", fake="field")

        assert "Unknown fields: fake" in str(exc)

        payload = dict(ip=1234, datetime="5678", user="9101112")
        signal = TestSignal.make(**payload)
        assert signal["type"] == TestSignal.meta.signal_type
        assert set(payload.keys()) & set(signal.keys()) == set(payload.keys())

    def test__cast(self):
        class PoorColumn(yt_schemas._Column):
            pass

        with pytest.raises(TypeError):
            PoorColumn()

        class TestSignal(yt_schemas.YTSignal):
            meta = yt_schemas.YTSignalMetadata(
                signal_type=ctss.YTSignalType.API_CALL_YT,
                path="//home",
                proxy=yt_schemas.Proxy.ARNOLD,
            )

            datetime = yt_schemas.Int32Column()
            user = yt_schemas.StringColumn(required=False)
            ip = yt_schemas.Int64Column()

        with pytest.raises(ValueError):
            TestSignal.make(datetime=None, user="abc", ip=0)

        data = TestSignal.make(datetime=1, user=2, ip=3)
        assert data == dict(datetime=1, user="2", ip=3, type=ctss.YTSignalType.API_CALL_YT)
