# -*- coding: utf-8 -*-

import os
import logging
import subprocess
import itertools
import time
from collections import defaultdict
from urllib import urlretrieve

from sandbox.sandboxsdk import process
from sandbox.sandboxsdk import parameters
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.projects import resource_types
from sandbox.projects.common import utils
from sandbox.projects.common import apihelpers
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common.dynamic_models.utils import walk_files
from sandbox.projects.common.dynamic_models.utils import is_base_model
from sandbox.projects.common.dynamic_models.utils import is_middle_model
from sandbox.projects.common.dynamic_models.matrixnet import is_matrixnet
from sandbox.projects.common.dynamic_models.mxops import get_props


FACTOR_TAGS = {
    "TG_UNIMPLEMENTED": "--unimplemented",
    "TG_DEPRECATED": "--unused",
    "TG_REMOVED": "--removed",
}


def matrixnets_from_dir(models_dir, base, middle):
    files = walk_files(models_dir, False)
    matrixnets = filter(is_matrixnet, files)
    if base and middle:
        return list(matrixnets)
    elif base:
        return filter(is_base_model, matrixnets)
    elif middle:
        return filter(is_middle_model, matrixnets)
    else:
        return []


def parse_relev_fml_unused(output):
    logging.info("parse relev_fml_unused for unimplemented factors")
    formulas = defaultdict(set)
    used_in = "Used in:"
    pairs = zip(*[iter(output)]*2)
    for factor, used in pairs:
        factor = factor.split('\t', 1)
        if len(factor) < 2:
            break
        factor = int(factor[0])
        logging.info("factor: %s", factor)
        if not used.startswith(used_in):
            break
        used = used[len(used_in):]
        files = [f.strip() for f in used.split(",")]
        logging.info("files:\n%s", " ".join(files))
        for f in files:
            formulas[f].add(factor)
    return formulas


def parse_relev_fml_unused_379(output):
    logging.info("parse relev_fml_unused for 379 factor")
    used_in = "Used in:"
    formulas = []
    for used in output:
        if not used.startswith(used_in):
            break
        used = used[len(used_in):]
        files = [f.strip() for f in used.split(",")]
        logging.info("files:\n%s", " ".join(files))
        formulas.extend(files)
    return formulas


def find_bad_factors(relev_fml_unused, models_dir, factor_tags, *files):
    logging.debug('find bad factors for: %s', " ".join(files))
    command = [
        relev_fml_unused,
        '--arc', models_dir,
        '-f', '379',
        '--no-default',
        '--factors_gen', 'factors_gen.in'
    ] + [FACTOR_TAGS[i] for i in factor_tags]
    ps = subprocess.Popen(command + list(files), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = [line.strip() for line in ps.stderr]
    parts = [i for i, line in enumerate(output) if line.startswith("web ")]
    parts = zip(parts, parts[1:] + [None])
    bad = defaultdict(set)
    for start, end in parts:
        if output[start].startswith("web 379"):
            formulas = parse_relev_fml_unused_379(output[start+1:end])
            for path in formulas:
                bad[path].add(379)
        else:
            for f_tag in factor_tags:
                if output[start].startswith("web {}".format(f_tag)):
                    unimplemented = parse_relev_fml_unused(output[start + 1:end])
                    for path, factors in unimplemented.iteritems():
                        bad[path].update(factors)
    return bad


def unpack_models_archive(archiver_path, archive_path, directory):
    logging.info('unpack models from %s', archive_path)
    process.run_process([archiver_path, "-u", "-d", directory, archive_path], timeout=600)


def id_from_link(link):
    return link[link.rfind('/')+1:] if link else None


class Formula:
    def __init__(self, path, mx_ops, factors):
        logging.info("init formula %s", path)
        self.filename = os.path.basename(path)
        info = get_props(mx_ops, path)
        self.formula_id = info.get("formula-id")
        self.formula_link = info.get("formula-link")
        self.id = id_from_link(self.formula_link)
        self.author = info.get("author") or info.get("user")
        links = (info.get("{0}.formula-link".format(mn)) for mn in ["mn1", "mn2"])
        ids = (id_from_link(link) for link in links)
        self.deps = set(i for i in ids if i)
        self.factors = factors
        self.factors_string = " ".join(str(f) for f in sorted(factors))

    def show(self, show_filename=True):
        template = "{self.formula_id} {self.formula_link} {self.author}"
        if show_filename:
            template += " {self.filename}"
        template += ": {self.factors_string}"
        return template.format(**locals())

    def show_tree(self, result, formulas):
        tree = []
        self.get_tree(tree, formulas)
        result.extend("*" * depth + " " + f.show(depth <= 0) for depth, f in tree)

    def get_tree(self, result, formulas, depth=0):
        result.append((depth, self))
        deps = (formulas[f] for f in self.deps if f in formulas)
        for formula in deps:
            formula.get_tree(result, formulas, depth + 1)


def formulas_info(bad, mx_ops):
    logging.info('getting info with %s for %s formulas', mx_ops, len(bad))
    return [Formula(path, mx_ops, factors) for path, factors in bad.iteritems()]


def download_formula(models_dir, formula_id):
    url = """http://fml.yandex-team.ru/download/computed/formula?id={0}&file=matrixnet.info""".format(formula_id)
    path = os.path.join(models_dir, "tmp_matrixnet_from_fml_{0}.info".format(formula_id))
    logging.info("downloading %s", url)
    for attempt in range(4):
        try:
            urlretrieve(url, path)
            return path
        except IOError:
            time.sleep(2**attempt)
    urlretrieve(url, path)
    return path


def matrixnets_from_fml(models_dir, ids):
    logging.info('downloading matrixnets from fml')
    return [download_formula(models_dir, i) for i in ids]


def find_bad_factors_info_tree(models_dir, relev_fml_unused, mx_ops, check_base, check_middle, factor_tags):
    logging.info('build bad factors tree')
    matrixnets = matrixnets_from_dir(models_dir, check_base, check_middle)
    bad = find_bad_factors(relev_fml_unused, models_dir, factor_tags, *matrixnets)
    top_formulas = formulas_info(bad, mx_ops)
    new_formulas = top_formulas
    all_formulas = {}
    while new_formulas:
        logging.info('new formulas: %s', " ".join(f.formula_id for f in new_formulas))
        all_formulas.update({f.id: f for f in new_formulas if f.id})
        ids = itertools.chain.from_iterable(f.deps for f in new_formulas)
        ids = set(i for i in ids if i not in all_formulas)
        matrixnets = matrixnets_from_fml(models_dir, ids)
        bad = find_bad_factors(relev_fml_unused, models_dir, factor_tags, *matrixnets)
        new_formulas = [f for f in formulas_info(bad, mx_ops) if f.id not in all_formulas]
    return all_formulas, top_formulas


def svn_last_revision_url(url):
    parsed = Arcadia.parse_url(url)
    revision = parsed.revision
    if not revision or revision == "HEAD":
        parent = Arcadia.parent_dir(url)
        revision = utils.svn_last_change(parent)
    return Arcadia.replace(url, revision=revision)


class ModelsArchiveParameter(parameters.ResourceSelector):
    name = 'models_archive_resource_id'
    description = 'Models archive'
    resource_type = ['DYNAMIC_MODELS_ARCHIVE', 'DYNAMIC_MODELS_ARCHIVE_BASE']
    required = True


class RelevFmlUnusedParameter(parameters.ResourceSelector):
    name = 'relev_fml_unused_resource_id'
    description = 'relev_fml_unused executable'
    resource_type = 'RELEV_FML_UNUSED_EXECUTABLE'


class FactorsGenParameter(parameters.SandboxArcadiaUrlParameter):
    name = 'factors_gen'
    description = 'factors_gen.in arcadia url'
    default_value = 'arcadia:/arc/trunk/arcadia/kernel/web_factors_info/factors_gen.in'
    required = False


class CheckBaseModelsParameter(parameters.SandboxBoolParameter):
    name = 'check_base_models'
    description = 'Check base models'
    default_value = True


class CheckMiddleModelsParameter(parameters.SandboxBoolParameter):
    name = 'check_middle_models'
    description = 'Check middle models'
    default_value = True


class FailOnAnyBadFactor(parameters.SandboxBoolParameter):
    name = 'fail_on_any_bad_factor'
    description = 'Fail on any bad factor'
    default_value = False


class StrictModelsParameter(parameters.SandboxStringParameter):
    name = 'strict_models'
    description = 'Fail if these models use bad factors (comma separated list)'
    required = False


class FactorTags(parameters.SandboxBoolGroupParameter):
    name = "factor_tags_to_check"
    description = "Factor tags to check"
    choices = zip(FACTOR_TAGS.keys(), FACTOR_TAGS.keys())
    default_value = " ".join(FACTOR_TAGS.keys())


class TestDynamicModelsFeatures(SandboxTask):
    """
        Проверяет, что в архиве нет моделей, использующих:
          * TG_UNIMPLEMENTED факторы
          * 379-й фактор
    """

    type = 'TEST_DYNAMIC_MODELS_FEATURES'

    input_parameters = [
        ModelsArchiveParameter,
        RelevFmlUnusedParameter,
        FactorsGenParameter,
        CheckBaseModelsParameter,
        CheckMiddleModelsParameter,
        FailOnAnyBadFactor,
        StrictModelsParameter,
        FactorTags,
    ]
    execution_space = 20 * 1024  # 20 Gb

    def on_execute(self):
        if not self.ctx.get(RelevFmlUnusedParameter.name):
            self._prepare_tools()
        self._prepare_factors()
        self._run_check()

    def _prepare_tools(self):
        build_relev_fml_unused_task_id = self.ctx.get("build_relev_fml_unused_task_id")
        if build_relev_fml_unused_task_id:
            utils.check_if_tasks_are_ok([build_relev_fml_unused_task_id])
            build_relev_fml_unused_task = channel.sandbox.get_task(build_relev_fml_unused_task_id)
            relev_fml_unused_resource_id = build_relev_fml_unused_task.ctx["relev_fml_unused_resource_id"]
            channel.sandbox.set_resource_attribute(
                relev_fml_unused_resource_id,
                "source_url",
                build_relev_fml_unused_task.ctx["checkout_arcadia_from_url"]
            )
            self.ctx[RelevFmlUnusedParameter.name] = relev_fml_unused_resource_id
        else:
            check_base = utils.get_or_default(self.ctx, CheckBaseModelsParameter)
            url = self._get_stable_url(
                'BASESEARCH_EXECUTABLE' if check_base else 'RANKING_MIDDLESEARCH_EXECUTABLE'
            )
            relev_fml_unused_resources = apihelpers.get_resources_with_attribute(
                "RELEV_FML_UNUSED_EXECUTABLE", "source_url", url,
                limit=1,
                arch=self.arch
            )
            if relev_fml_unused_resources:
                self.ctx[RelevFmlUnusedParameter.name] = relev_fml_unused_resources[0].id
            else:
                build_relev_fml_unused_task_id = self._run_build_relev_fml_unused(url)
                self.ctx["build_relev_fml_unused_task_id"] = build_relev_fml_unused_task_id
                self.wait_task_completed(build_relev_fml_unused_task_id)

    def _prepare_factors(self):
        url = self.ctx.get(FactorsGenParameter.name)
        if not url:
            relev_fml_unused = channel.sandbox.get_resource(self.ctx[RelevFmlUnusedParameter.name])
            source_url = relev_fml_unused.attributes.get("source_url")
            url = Arcadia.append(source_url, "kernel/web_factors_info/factors_gen.in") if source_url else FactorsGenParameter.default_value
        self.ctx[FactorsGenParameter.name] = svn_last_revision_url(url)

    def _run_check(self):
        check_base = utils.get_or_default(self.ctx, CheckBaseModelsParameter)
        check_middle = utils.get_or_default(self.ctx, CheckMiddleModelsParameter)
        eh.ensure(check_base or check_middle, "please select check_base_models or check_middle_models")

        mx_ops = utils.sandbox_resource(resource_types.MX_OPS_EXECUTABLE, "build_dynamic_models", "75-4")
        archiver_path = utils.sandbox_resource(resource_types.ARCHIVER_TOOL_EXECUTABLE, "build_dynamic_models", "75-4")

        models_archive = self.sync_resource(self.ctx[ModelsArchiveParameter.name])
        models_dir = self.path("models")
        unpack_models_archive(archiver_path, models_archive, models_dir)

        Arcadia.export(self.ctx[FactorsGenParameter.name], os.path.join(models_dir, "factors_gen.in"))
        relev_fml_unused = self.sync_resource(self.ctx[RelevFmlUnusedParameter.name])
        all_formulas, top_formulas = find_bad_factors_info_tree(
            models_dir, relev_fml_unused, mx_ops, check_base, check_middle,
            utils.get_or_default(self.ctx, FactorTags).strip().split(" ")
        )

        top_formulas = sorted(top_formulas, key=lambda x: x.filename)
        tree = []
        for f in top_formulas:
            f.get_tree(tree, all_formulas)
        self.ctx["formulas_tree"] = [(d, f.__dict__) for d, f in tree]

        strict_models = set(s.strip() for s in self.ctx.get(StrictModelsParameter.name, "").split(","))
        strict_top_formulas = [f for f in top_formulas if f.filename in strict_models]
        if strict_top_formulas:
            lines = []
            for f in strict_top_formulas:
                f.show_tree(lines, all_formulas)
            eh.check_failed("models with bad factors:\n" + "\n".join(lines))
        else:
            lines = []
            for f in top_formulas:
                f.show_tree(lines, all_formulas)
            logging.info("All bad models:\n%s", "\n".join(lines))
            if utils.get_or_default(self.ctx, FailOnAnyBadFactor) and lines:
                eh.check_failed("There are bad models:\n{}".format("\n".join(lines)))

    def _get_stable_url(self, resource_type):
        search_resource = apihelpers.get_last_released_resource(resource_type, arch=self.arch)
        eh.verify(search_resource, "cannot find stable search")

        search_build_task = channel.sandbox.get_task(search_resource.task_id)
        eh.verify(search_build_task, "cannot find stable search build task")

        url = search_build_task.ctx.get("checkout_arcadia_from_url")
        eh.verify(url, "stable search build task has no arcadia url")
        url = svn_last_revision_url(url)

        return url

    def _run_build_relev_fml_unused(self, url):
        return self.create_subtask(
            task_type='BUILD_SEARCH',
            input_parameters={
                "checkout_arcadia_from_url": url,
                "build_relev_fml_unused": True,
            },
            description=self.descr,
        ).id


__Task__ = TestDynamicModelsFeatures
