# This Python file uses the following encoding: utf-8
from sandbox.projects.common.build.KosherYaMake import KosherYaMake
from sandbox.projects.common import binary_task
from sandbox import sdk2
import os


class KolhozTestRun(KosherYaMake, binary_task.LastBinaryTaskRelease):
    class Parameters(KosherYaMake.Parameters):
        model_name = sdk2.parameters.String("Model name", default="Яндекс Станция Мини")
        kolhoz_token = sdk2.parameters.YavSecret("Kolhoz token", default="sec-01dez1a5pfxech6v1h144k1kf4")
        tus_token = sdk2.parameters.YavSecret("Tus token", default="sec-01dez1a5pfxech6v1h144k1kf4")
        device_group = sdk2.parameters.String("Device Group", default="YANDEX_TEAM")
        device_id = sdk2.parameters.String("Device ID", default="")
        kolhoz_device_id = sdk2.parameters.String("Kolhoz device ID", default="")
        occupy_device = sdk2.parameters.Bool("Occupy device in kolhoz", default=True)

    def pre_build(self, source_dir):
        from yandex_io.pylibs.kolhoz.kolhoz_api import KolhozDevice
        from yandex_io.pylibs.kolhoz.kolhoz_groomer import prepare_for_presmoke

        os.environ["TUS_TOKEN"] = self.Parameters.tus_token.data()["tus_token"]

        kolhos_token = self.Parameters.kolhoz_token.data()["kolhoz_token"]
        if self.Parameters.occupy_device:
            device = KolhozDevice.get_device(
                kolhos_token, self.Parameters.model_name, self.Parameters.device_group, self.Parameters.device_id
            )
        else:
            device = KolhozDevice(self.Parameters.device_id, self.Parameters.kolhoz_device_id, kolhos_token)
        device.connect()
        prepare_for_presmoke(device, os.path.join(source_dir, 'yandex_io/functional_tests/'))
