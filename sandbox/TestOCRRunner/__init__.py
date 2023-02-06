# -*- coding: utf-8 -*-
import re
import time
import logging
import tarfile
import subprocess
import string
import json
from os import path
from contextlib import closing
from sandbox.projects import resource_types
from sandbox.sandboxsdk.parameters import SandboxBoolParameter
from sandbox.sandboxsdk.parameters import SandboxStringParameter
from sandbox.sandboxsdk.parameters import LastReleasedResource
from sandbox.sandboxsdk.parameters import SandboxIntegerParameter
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.paths import make_folder
from sandbox.sandboxsdk.paths import list_dir
from sandbox.sandboxsdk.paths import get_logs_folder
from sandbox.sandboxsdk.paths import copy_path
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.svn import Arcadia


class OCRBinaresArchiveParameter(LastReleasedResource):
    name = 'ocr_test_resource'
    description = 'Ocr resource'
    resource_type = resource_types.OCR_RUNNER_ARCHIVE
    group = 'OCR parameters'


class ImageDataArchiveParameter(SandboxStringParameter):
    name = 'ocr_test_image_dataset'
    description = 'Image datasets'
    default_value = '<script> * <id> * <test suffix> * <config> * <langs>'
    group = 'Test parameters'
    multiline = True


class ShowImageDataArchiveParameter(LastReleasedResource):
    name = 'ocr_test_show_datasets'
    description = 'Show images datasets. No add to test'
    resource_type = resource_types.OCR_IMAGE_DATASET
    group = 'Test parameters'


class OcrTestCommentParameter(SandboxStringParameter):
    name = 'ocr_test_comment'
    description = 'Test comment'
    default_value = ''
    group = 'Test parameters'


class RunParallelParameter(SandboxBoolParameter):
    name = 'ocr_test_run_parallel'
    description = 'Run parallel on datasets'
    default_value = False
    group = 'Test parameters'


class OcrMaxThreadsParameter(SandboxIntegerParameter):
    name = 'ocr_test_max_threads'
    description = 'Max count of threads'
    default_value = 1
    group = 'Test parameters'


class OcrMaxSubThreadsParameter(SandboxIntegerParameter):
    name = 'ocr_test_max_subthreads'
    description = 'Max count of subthreads'
    default_value = 1
    group = 'Test parameters'


class TestOCRRunner(SandboxTask):
    type = 'TEST_OCR_RUNNER'

    input_parameters = [
        OCRBinaresArchiveParameter,
        ShowImageDataArchiveParameter,
        ImageDataArchiveParameter,
        OcrMaxThreadsParameter,
        OcrMaxSubThreadsParameter,
        RunParallelParameter,
        OcrTestCommentParameter
    ]

    execution_space = 10000

    OCR_TEST_DATASETS = 'datasets'
    OCR_TEST_BIN_DATA = 'binData'
    OCR_TEST_RESULT = 'result'

    OCR_TEST_RESULT_DATASETS = path.join(OCR_TEST_RESULT, 'datasets')
    OCR_TEST_CONFIG_DATA_PATH = path.join(OCR_TEST_BIN_DATA, 'data')

    OCR_ARCADIA_BIN = path.join(OCR_TEST_BIN_DATA, 'bin')
    OCR_TEST_ALIAS = path.join(OCR_ARCADIA_BIN, 'cv/imageproc/ocr/tools/statistic/auto_tests/alias.txt')
    OCR_SVN_INFO = path.join(OCR_TEST_BIN_DATA, 'svn.info')

    def on_execute(self):

        logging.info('Get arcadia ya info')
        arcadia_src_dir = Arcadia.get_arcadia_src_dir(Arcadia.trunk_url())
        if not arcadia_src_dir:
            raise SandboxTaskFailureError(
                'Cannot get repo for url {0}'.format(Arcadia.trunk_url())
            )
        ya_bin_path = path.join(arcadia_src_dir, 'ya')
        logging.info('Get arcadia ya info: Done {0}'.format(ya_bin_path))

        logging.info('Get data set info')
        (datasetsId, datasetsTests) = self.createDataSetId()
        datasetRun = {}
        for elemId in range(0, len(datasetsTests)):
            datasetRun[elemId] = True
        logging.info('Get data set info : Done')

        logging.info('Unpack bin data')
        tar_binares = self.sync_resource(self.ctx[OCRBinaresArchiveParameter.name])
        make_folder(self.abs_path(self.OCR_TEST_BIN_DATA), True)
        with closing(tarfile.open(tar_binares, 'r:*', dereference=True)) as tar_file:
            tar_file.extractall(self.abs_path(self.OCR_TEST_BIN_DATA))
        logging.info('Unpack bin data : Done')

        logging.info('Get data')
        path_to_data = self.abs_path(self.OCR_TEST_DATASETS)
        make_folder(path_to_data, True)
        for id in datasetsId:
            current_dataset = path.join(path_to_data, str(id))
            make_folder(current_dataset, True)
            tar_binares = self.sync_resource(id)
            with closing(tarfile.open(tar_binares, 'r:gz', dereference=True)) as tar_file:
                tar_file.extractall(current_dataset)
        logging.info('Get data : Done')

        logging.info('Fix configs')
        for elemId in range(0, len(datasetsTests)):
            (id, name, suffix, scriptName, configPath, langs) = datasetsTests[elemId]
            configPath = self.abs_path(path.join(self.OCR_TEST_CONFIG_DATA_PATH, configPath))
            if not(path.isfile(configPath)):
                datasetRun[elemId] = False
                continue
            conf = ""
            with open(configPath, "r") as f:
                conf = f.read()
            threads = self.ctx[OcrMaxThreadsParameter.name]
            if (threads > 0):
                conf = re.sub(r"MaxThreads (\d+)\n", "MaxThreads " + str(threads) + "\n", conf)
            subthreads = self.ctx[OcrMaxSubThreadsParameter.name]
            if (subthreads > 0):
                conf = re.sub(r"MaxSubThreads (\d+)\n", "MaxSubThreads " + str(subthreads) + "\n", conf)
            with open(configPath, "w") as f:
                f.write(conf)
        logging.info('Fix configs : Done')

        logging.info('Load alias and svn info')
        alias = {}
        with open(self.abs_path(self.OCR_TEST_ALIAS)) as fAlias:
            for line in fAlias:
                words = line[:-1].split('\t')
                if (len(words) != 2):
                    logging.error('Bad alias {}'.format(line))
                    continue
                alias[words[0]] = words[1]

        svnRev = 0
        with open(self.abs_path(self.OCR_SVN_INFO)) as fSvnInfo:
            info = json.loads(fSvnInfo.read())
            svnRev = max(int(info['DataInfo']['entry_revision']), int(info['CodeInfo']['entry_revision']))

        logging.info('Load alias and svn info : Done')

        logging.info('Run statistic')
        make_folder(self.abs_path(self.OCR_TEST_RESULT), True)
        make_folder(self.abs_path(self.OCR_TEST_RESULT_DATASETS), True)
        waitOcrRunner = not(self.ctx[RunParallelParameter.name])
        procs = []
        outFolders = []
        elemId = 0
        freeThreads = self.client_info['ncpu']
        if freeThreads < threads:
            logging.error('Current cpu count less then {0}'.format(threads))
            raise SandboxTaskFailureError('Test has errors')
        logging.info('Current cpu count {0}.'.format(freeThreads))

        workedThreads = set()
        for elemId in range(0, len(datasetsTests)):
            (id, name, suffix, scriptName, configPath, langs) = datasetsTests[elemId]
            if(not(datasetRun[elemId])):
                logging.info('No run statistic :' + scriptName + ' ' + str(id) + ' ' + suffix + ' ' + configPath)
                continue

            in_dir = self.abs_path(path.join(self.OCR_TEST_DATASETS, str(id)))
            out_dir = self.abs_path(path.join(self.OCR_TEST_RESULT_DATASETS, str(id) + suffix))
            out_logRes = self.abs_path(path.join(self.OCR_TEST_RESULT_DATASETS, str(id) + suffix + "log."))
            configPath = self.abs_path(path.join(self.OCR_TEST_CONFIG_DATA_PATH, configPath))
            if out_dir in outFolders:
                logging.info('Image result folder {} exist!'.format(out_dir))
                datasetRun[elemId] = False
                continue
            outFolders.append(out_dir)
            make_folder(out_dir, True)
            execCommand = scriptName
            if scriptName in alias:
                execCommand = alias[scriptName]
            execCommand = execCommand.replace('{arcadia}', self.abs_path(self.OCR_ARCADIA_BIN))
            execCommand = execCommand.replace('{ya}', ya_bin_path)
            command = " ".join((
                execCommand, self.abs_path(self.OCR_ARCADIA_BIN), in_dir, out_dir, configPath, out_logRes, str(threads), langs
            ))
            logging.info('Executed: {}'.format(command))
            procs.append((
                elemId,
                run_process(
                    command,
                    shell=True, wait=waitOcrRunner, log_prefix=out_logRes + "runLog.txt",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, outputs_to_one_file=False, check=False
                )
            ))
            freeThreads -= threads
            if not(waitOcrRunner):
                while freeThreads < threads:
                    for (elemId, proc) in procs:
                        if not(elemId in workedThreads) and proc.poll() is not None:
                            workedThreads.add(elemId)
                            freeThreads += threads
                    time.sleep(30)

        statisticResult = []
        for (elemId, proc) in procs:
            proc.wait()
            procInOut = proc.communicate()
            statisticJson = {}
            if proc.returncode:
                logging.error('Process "{0}" died with exit code {1}\nCerr:\n{2}\nCout:\n{3}\n'.format(proc.saved_cmd, proc.returncode, procInOut[1], procInOut[0]))
                logging.error('Process "{0}" logs: '.format(proc.saved_cmd))
                (id, name, suffix, scriptName, configPath, langs) = datasetsTests[elemId]
                log_prefix = str(id) + suffix + "log."
                logs = list_dir(self.OCR_TEST_RESULT_DATASETS, filter=log_prefix, files_only=True)
                for log in logs:
                    logging.error('\t{0}'.format(log))
                    copy_path(path.join(self.OCR_TEST_RESULT_DATASETS, log), path.join(get_logs_folder(), log))
                datasetRun[elemId] = False
                continue
            else:
                linesCout = procInOut[0].split('\n')
                statistic = linesCout[len(linesCout) - 2]
                try:
                    statisticJson = json.loads(statistic)
                except ValueError:
                    logging.error('Can\'t  parse statistic result:\n Command {0}\nCout: {1}'.format(proc.saved_cmd, procInOut[0]))
                    datasetRun[elemId] = False
                    continue

            (id, name, suffix, scriptName, configPath, langs) = datasetsTests[elemId]
            statisticElement = {
                "testInfo": {
                    "suffix": suffix,
                    "id": id,
                    "name": name,
                    "script": scriptName,
                    "config": configPath,
                    "langs": langs
                },
                "time": str(time.time()),
                "comment": str(self.ctx[OcrTestCommentParameter.name]),
                "ocrres": str(self.ctx[OCRBinaresArchiveParameter.name]),
                "ocrtask": str(self.id),
                "status": statisticJson["status"],
                "svnver": svnRev,
                "metrics": statisticJson["metrics"],
                "rmetrics": statisticJson["rmetrics"]
            }
            statisticResult.append(statisticElement)
        logging.info('Run statistic : Done')

        logging.info('Save result')
        info_resource = channel.sandbox.get_resource(self.ctx['info_ocr_pub_id'])
        with open(info_resource.path, 'w') as fInfo:
            fInfo.write('Statistic result for test ' + str(self.id) + '\n')
            for stat in statisticResult:
                fInfo.write(json.dumps(stat) + '\n')
        self.mark_resource_ready(info_resource)

        resource_path = channel.sandbox.get_resource(self.ctx['out_ocr_pub_id']).path
        with closing(tarfile.open(resource_path, 'w:gz', dereference=True)) as tar_file:
            tar_file.add(self.abs_path(self.OCR_TEST_RESULT), arcname="./")
        logging.info('Save result : Done')

        for run in datasetRun.values():
            if not(run):
                raise SandboxTaskFailureError('Test has errors')

    def createDataSetId(self):
        datasetsId = set()
        datasetsTests = []
        items = string.split(self.ctx[ImageDataArchiveParameter.name], '\n')
        for dataLine in items:
            if len(dataLine) < 2:
                continue
            if dataLine[-1] == '\r':
                dataLine = dataLine[:-1]
            (scriptName, data, suffix, config, langs) = string.split(dataLine, " * ")
            info = channel.sandbox.get_resource(data)
            if info is not None:
                datasetsId.add(info.id)
                datasetsTests.append((info.id, info.description, suffix, scriptName, config, langs))
            else:
                resources = channel.sandbox.list_resources(resource_type=resource_types.OCR_IMAGE_DATASET, attribute_name="name", attribute_value=data)
                if (resources is None):
                    raise SandboxTaskFailureError('Image dataset name {} not found'.format(data))
                for info in resources:
                    datasetsId.add(info.id)
                    datasetsTests.append((info.id, info.description, suffix, scriptName, config, langs))
        return (datasetsId, datasetsTests)

    def on_enqueue(self):
        SandboxTask.on_enqueue(self)
        filename = 'ocr_test_result.tar.gz'
        resource_path = self.abs_path(filename)
        resource_name = '%s (%s)' % (self.descr, filename)
        self.ctx['out_ocr_pub_id'] = self._create_resource(
            resource_name,
            resource_path,
            resource_types.OCR_TEST_RESULT).id
        filename = 'ocr_test_result.info'
        resource_path = self.abs_path(filename)
        resource_name = '%s info' % (self.descr)
        self.ctx['info_ocr_pub_id'] = self._create_resource(
            resource_name,
            resource_path,
            resource_types.OCR_TEST_RESULT_INFO).id


__Task__ = TestOCRRunner
