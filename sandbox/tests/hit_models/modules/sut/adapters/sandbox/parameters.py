from sandbox import sdk2
from sandbox.projects.runtime_models.components.yabs.resources import YabsHitModelsDaemon, RsyaHitModelsHeavyShard01NannyLayer
from sandbox.projects.websearch.begemot.resources import BEGEMOT_REALTIME_PACKAGE


class HitModelsSUTParameters(sdk2.Task.Parameters):
    with sdk2.parameters.Group("LmService sut parameters:") as sut_group:
        service_binary = sdk2.parameters.Resource('Resource with hit models service binary', resource_type=YabsHitModelsDaemon, required=True)
        service_layer = sdk2.parameters.Resource('Resource with hit models service resource', resource_type=RsyaHitModelsHeavyShard01NannyLayer, required=True)
        service_model_archive = sdk2.parameters.Resource('Resource with hit models archive of models', resource_type=BEGEMOT_REALTIME_PACKAGE, required=True)


class HitModelsSUTParametersSecondRun(sdk2.Task.Parameters):
    with sdk2.parameters.Group("LmService sut parameters for second run:") as sut_group_second_run:
        service_binary_2 = sdk2.parameters.Resource('Resource with hit models service binary', resource_type=YabsHitModelsDaemon, required=True)
        service_layer_2 = sdk2.parameters.Resource('Resource with hit models service resource', resource_type=RsyaHitModelsHeavyShard01NannyLayer, required=True)
        service_model_archive_2 = sdk2.parameters.Resource('Resource with hit models archive of models', resource_type=BEGEMOT_REALTIME_PACKAGE, required=True)
