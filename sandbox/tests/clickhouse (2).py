from sandbox.services.modules.statistics_processor.schemas import clickhouse as ch_schemas


class TestModels(object):
    def test__schema_version_existence(self):
        for model_class in ch_schemas.SIGNAL_MODELS.values():
            model_class()  # should raise RuntimeError if the corresponding field is missing
