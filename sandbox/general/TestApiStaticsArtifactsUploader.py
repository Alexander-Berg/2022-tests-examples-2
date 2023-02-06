import glob
import traceback
import logging
import os
import shutil
import tempfile

from sandbox import sdk2
from sandbox.projects.common.arcadia import sdk as arcadiasdk
from sandbox.projects.music.resources import StaticsTestArtifacts

from sandbox.projects.music.deployment.helpers.Config import CONFIG


class TestApiStaticsArtifactsUploader:
    @classmethod
    def execute(cls, task, env):
        generated_blob_directory = cls._set_generated_blob_directory()
        cls._set_yc_environment(env)
        cls._generate_blob(task)

        facegen_directory = glob.glob(generated_blob_directory + "/facegen*")[0]
        prefix = os.path.basename(facegen_directory)
        resource = cls._create_resource(task, facegen_directory)
        return resource, prefix

    @staticmethod
    def _set_yc_environment(env):
        for name, value in env.items():
            os.environ[name] = value
            if name.endswith('PASSWORD'):
                value = '***'
            logging.info('Setting env {}={}'.format(name, value))

    @staticmethod
    def _set_generated_blob_directory():
        generated_blob_directory = tempfile.mkdtemp()
        os.environ["GENERATED_TEST_BLOB_DIRECTORY"] = generated_blob_directory
        return generated_blob_directory

    @staticmethod
    def _generate_blob_in(sources_dir, task):
        results_dir = 'results-dir'
        try:
            arcadiasdk.do_build(build_system=arcadiasdk.consts.YMAKE_BUILD_SYSTEM,
                                source_root=sources_dir,
                                targets=[CONFIG.test_blob_src_path],
                                results_dir=results_dir,
                                clear_build=False,
                                def_flags={'JDK_VERSION': CONFIG._DEFAULT_JDK_VERSION},
                                yt_store_params=None,
                                test=True,
                                disable_test_timeout=True,
                                test_filters=CONFIG.test_blob_test_filter)
        except Exception:
            logging.error(traceback.format_exc())
            raise
        finally:
            resource = sdk2.service_resources.TaskCustomLogs(task, "Test run logs", results_dir)
            resource_data = sdk2.ResourceData(resource)
            resource_data.ready()

    @classmethod
    def _generate_blob(cls, task):
        if CONFIG.is_dev:
            cls._generate_blob_in(os.path.expanduser('~/arcadia-tmp'), task)
        else:
            with arcadiasdk.mount_arc_path("arcadia:/arc/trunk/arcadia") as aarcadia:
                cls._generate_blob_in(aarcadia, task)

    @classmethod
    def _create_resource(cls, task, generated_facegen_folder):
        resource_name = os.path.basename(generated_facegen_folder)
        resource = StaticsTestArtifacts(task, "Facegen for test-api", resource_name, ttl=30)
        resource_data = sdk2.ResourceData(resource)
        resource_path = str(resource_data.path)

        filtered = cls._filter_artifacts(generated_facegen_folder)
        for artifact in filtered:
            dest = os.path.join(resource_path, os.path.relpath(artifact, generated_facegen_folder))
            if not os.path.exists(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))
            shutil.move(artifact, dest)

        cls._fix_mmap_blob_layout(resource_path)

        resource_data.ready()
        return resource

    @staticmethod
    def _fix_mmap_blob_layout(resource_path):
        logging.debug("MUSICBACKEND-4215 Fix mmap blob layout taken from the worker")
        stage_path = os.path.join(resource_path, "stage")
        face_path = os.path.join(resource_path, "face")
        face_rev_0 = os.path.join(face_path, "0")
        face_immutable_path = os.path.join(face_path, "i")
        face_mutable_path = os.path.join(face_path, "m")

        logging.debug("Remove %s", stage_path)
        shutil.rmtree(stage_path, ignore_errors=True)

        logging.debug("Move %s /i and /m to revision 0", face_path)
        os.makedirs(face_rev_0)
        shutil.move(face_immutable_path, face_rev_0)
        shutil.move(face_mutable_path, face_rev_0)

    @staticmethod
    def _filter_artifacts(facegen_folder):
        file_list = []
        for (dirpath, _, filenames) in os.walk(facegen_folder):
            file_list.extend(os.path.join(dirpath, file) for file in filenames)
        return file_list
