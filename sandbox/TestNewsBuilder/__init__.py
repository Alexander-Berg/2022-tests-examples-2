# -*- coding: utf-8 -*-

import subprocess
import tarfile
import os
import sys
from shutil import copytree
import time
from contextlib import closing
from six.moves.urllib.request import urlopen

from sandbox.sandboxsdk import errors as se
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.util import system_info
from sandbox.sandboxsdk import paths

import sandbox.common.types.client as ctc

from sandbox.projects import resource_types
from sandbox.projects.geobase.GeodataTreeLingStable.resource import GEODATA_TREE_LING_STABLE
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common.news.newsd import SlaveNewsd
from sandbox.projects.common.news.master_newsd import MasterNewsd
from sandbox.projects.news.resources import NEWS_DEFAULT_INDEX_CONFIG


class PackageResourceParameter(sp.LastReleasedResource):
    name = 'package_resource_id'
    description = 'News package'
    resource_type = ['NEWS_INDEXER_YT_PACKAGE', 'NEWS_INDEXER_PACKAGE']
    required = True


class NewsDataResourceParameter(sp.LastReleasedResource):
    name = 'news_data_resource_id'
    description = 'News data'
    resource_type = resource_types.NEWS_BACKOFFICE_DATA
    required = True


class StorageResourceParameter(sp.LastReleasedResource):
    name = 'storage_resource_id'
    description = 'Info storage'
    resource_type = resource_types.NEWS_STORAGE
    required = True


class MediaResourceParameter(sp.LastReleasedResource):
    name = 'media_resource_id'
    description = 'Media data'
    resource_type = resource_types.NEWS_MEDIA_STORE
    required = True


class Geobase(sp.ResourceSelector):
    name = 'geobase'
    description = 'geodata4.bin'
    resource_type = GEODATA_TREE_LING_STABLE
    required = False


class IndexConfig(sp.ResourceSelector):
    name = 'index_config'
    description = 'index config path'
    resource_type = NEWS_DEFAULT_INDEX_CONFIG
    required = True


class ArchiveMode(sp.SandboxBoolParameter):
    name = 'archive_mode'
    description = 'Run in archive mode'
    default_value = False
    required = False


class TestNewsBuilder(SandboxTask):
    """
        Запускает новостной builder на замороженных данных и проверяет его работоспособность
    """

    type = 'TEST_NEWS_BUILDER'

    required_ram = 64 * 1024  # 64G
    execution_space = 120 * 1024  # 120G
    client_tags = ctc.Tag.LINUX_PRECISE

    input_parameters = (
        PackageResourceParameter,
        NewsDataResourceParameter,
        StorageResourceParameter,
        MediaResourceParameter,
        Geobase,
        ArchiveMode,
        IndexConfig,
    )

    def load_resource(self, name):
        resource_id = self.ctx[name]
        self.sync_resource(resource_id)
        return channel.sandbox.get_resource(resource_id)

    def install_ynews_scripts_package(self, tar):
        python_scripts_path = "scripts/lib/python"
        extract_target = os.path.join(python_scripts_path, "ynews")

        members = tar.getmembers()
        tar.extractall(members=filter(lambda x: x.name.startswith(extract_target), members))

        sys.path.append(self.path(python_scripts_path))

    def on_execute(self):
        package = self.load_resource(PackageResourceParameter.name)
        news_data = self.load_resource(NewsDataResourceParameter.name)
        storage = self.load_resource(StorageResourceParameter.name)
        media = self.load_resource(MediaResourceParameter.name)

        storage_path = self.path("info_storage")
        copytree(storage.path + "/info", storage_path)
        media_path = self.path("media")
        copytree(media.path, media_path)

        for entry in media_path, storage_path:
            os.chmod(entry, 0o777)
            for root, dirs, files in os.walk(entry):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o777)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o777)

        arcmode = self.ctx.get(ArchiveMode.name)

        with tarfile.open(package.path) as tar:
            try:
                self.install_ynews_scripts_package(tar)

                from ynews.builder import Builder

                storage_path = os.path.abspath(storage_path)
                storage_config = r'"type":"dir","keep-versions":1,"path":"' + storage_path + r'"'

                builder = Builder(package=package.path, news_data=news_data.path, work_dir="builder")

                if arcmode:
                    self.run_with_log(
                        builder.run,
                        "builder.out.txt",
                        storage=storage_config,
                        results_dir="results",
                        media=media_path,
                        threads=system_info()['ncpu'],
                        arcmode=True,
                        verbose=True,
                    )
                    builder.make_group_attrs("grattrs")
                    builder.make_newsd_binary_state("{" + storage_config + "}", "newsd")
                else:
                    def get_timestamp(path):
                        with open(path, 'r') as fd:
                            timestamp = fd.read()
                            return timestamp.rstrip("\n")

                    storage_timestamp = get_timestamp(storage.path + "/timestamp")
                    media_timestamp = get_timestamp(media.path + "/timestamp")
                    eh.ensure(
                        storage_timestamp == media_timestamp,
                        "Storage and Media resources are from different iterations"
                    )

                    rt_toloka = builder.make_fake_rt_toloka()

                    builder_results = self.path("results")

                    self.run_with_log(
                        builder.run,
                        "builder.out.txt",
                        storage=storage_config,
                        results_dir=builder_results,
                        media=media_path,
                        timestamp=storage_timestamp,
                        rt_toloka=rt_toloka,
                        threads=system_info()['ncpu'],
                        arcmode=False,
                        verbose=True,
                    )

                    tar.extract("bin/slave_newsd")
                    tar.extract("bin/master_newsd")
                    tar.extract("config/slave_newsd.conf")

                    geobase = self.load_resource(Geobase.name).path
                    index_config_path = self.load_resource(IndexConfig.name).path

                    master_port = 17170
                    slave_port = 17270

                    slave_newsd = SlaveNewsd(
                        binary="bin/slave_newsd",
                        cfg="config/slave_newsd.conf",
                        port=slave_port,
                        geobase=geobase,
                        index_config_path=index_config_path,
                    )

                    storage_config_file = self.path("storage.config")
                    with open(storage_config_file, "w") as fout:
                        fout.write("{" + storage_config + "}")

                    master_newsd = MasterNewsd(
                        binary="bin/master_newsd",
                        port=master_port,
                        slave="localhost:" + str(slave_newsd.get_state_port()),
                        state=builder_results,
                        storage=storage_config_file,
                        onlines="disk:" + media_path + "/onlines",
                        debug=True
                    )

                    master_newsd.start()
                    time.sleep(30)
                    slave_newsd.start()
                    master_newsd.wait(timeout=600)
                    slave_newsd.wait()

                    url = "http://localhost:{p}/tops?state_version_tag={t}&profile=1".format(
                        p=slave_newsd.get_http_port(),
                        t=storage_timestamp,
                    )
                    with closing(urlopen(url)) as r:
                        tops = r.read()
                        self.run_with_log(builder.check_morda_news, "checkMordaNews2.pl.out.txt", tops)

                self.set_info("All is OK")

            except Exception as e:
                raise se.SandboxTaskFailureError(e)

    def run_with_log(self, func, log_name, *args, **kwargs):
        def tail(log, n=10):
            lines = log.split("\n")
            return "\n".join(lines[-n:])

        log_file = paths.get_unique_file_name(paths.get_logs_folder(), log_name)
        with open(log_file, 'w') as log:
            try:
                output = func(*args, **kwargs)
                log.write(output)
            except subprocess.CalledProcessError as e:
                log.write(e.output)
                self.set_info("Tail from {}:\n{}".format(log_name, tail(e.output)))
                raise e


__Task__ = TestNewsBuilder
