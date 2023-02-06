import json
import difflib

from sandbox import sdk2
from sandbox.sandboxsdk import environments
from sandbox.sdk2.helpers import subprocess as sp, ProcessLog
from sandbox.projects.resource_types import OTHER_RESOURCE
import sandbox.projects.news.resources as resources


def is_ignored(path, ignored_list):
    for ignored in ignored_list:
        if path.startswith(ignored):
            return True
    return False


def get_cleared_json(obj, ignored, path='', depth=0):
    if isinstance(obj, list):
        result = []
        new_path = path + ".[]"
        for sub_obj in sorted(obj, key=lambda val: val['type']) if depth == 0 else sorted(obj):
            if depth == 0:
                new_path = sub_obj['type']
            if not is_ignored(new_path, ignored):
                result.append(get_cleared_json(sub_obj, ignored, new_path, depth + 1))
        return result
    elif isinstance(obj, dict):
        result = {}
        for key in obj:
            new_path = path + '.' + key
            if not is_ignored(new_path, ignored):
                result[key] = get_cleared_json(obj[key], ignored, new_path, depth + 1)
        return result
    else:
        return obj


def prepare_json(obj):
    if isinstance(obj, list):
        for sub_obj in obj:
            apphost_type = sub_obj['type']
            if apphost_type == 'http_response' and 'content' in sub_obj:
                try:
                    real_content = json.loads(sub_obj['content'])
                    sub_obj['content'] = real_content
                except:
                    pass
    return obj


def get_json_description(obj):
    if isinstance(obj, list):
        array_desc = []
        for child in obj:
            array_desc.append(get_json_description(child))
        return array_desc
    elif isinstance(obj, dict):
        dict_desc = {}
        for key in obj:
            dict_desc[key] = get_json_description(obj[key])
        return dict_desc

    return str(type(obj))


def clean_json_description(obj1, obj2, strict_dict=False):
    if type(obj1) != type(obj2):
        return
    if isinstance(obj1, list):
        length = min(len(obj1), len(obj2))
        obj1 = obj1[:length]
        obj2 = obj2[:length]
        for i in range(length):
            clean_json_description(obj1[i], obj2[i], strict_dict)
    elif isinstance(obj1, dict) and not strict_dict:
        keys_to_delete = []
        for key in obj2:
            if key not in obj1:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del obj2[key]
        for key in obj2:
            if key in obj1 and key in obj2:
                clean_json_description(obj1[key], obj2[key], strict_dict)


class CompareNewsApphostSerivceResponses(sdk2.Task):
    environment = (
        environments.SvnEnvironment(),
    )

    class Requirements(sdk2.Task.Requirements):
        cores = 1
        disk_space = 1 * 1024
        ram = 2 * 1024

        class Caches(sdk2.Requirements.Caches):
            pass

    class Context(sdk2.Context):
        service_config = "void"

    class Parameters(sdk2.Task.Parameters):
        service_name = sdk2.parameters.String(
            'Name of the service to read config from yweb/news/runtime_yappy',
            required=True
        )

        with sdk2.parameters.String("Compare method:") as compare_method:
            compare_method.values.DEEP_COMPARE = compare_method.Value("Deep compare", default=True)
            compare_method.values.SCHEMA_ONLY = compare_method.Value("Check schema only (new fields in response 2 are ignored)")

        requests = sdk2.parameters.Resource('Requests', resource_type=resources.NEWS_APPHOST_SERVICE_REQUESTS, required=True)
        responses1 = sdk2.parameters.Resource('Responses 1', resource_type=resources.NEWS_APPHOST_SERVICE_RESPONSES, required=True)
        responses2 = sdk2.parameters.Resource('Responses 2', resource_type=resources.NEWS_APPHOST_SERVICE_RESPONSES, required=True)
        with sdk2.parameters.Output:
            has_diff = sdk2.parameters.Bool("Does input responses has difference", default=True)

    def compare_json(self, json1, json2):
        if json1 != json2:
            self.set_info("there is some diff")
            json1_text = json.dumps(json1, sort_keys=True, indent=4)
            json2_text = json.dumps(json2, sort_keys=True, indent=4)
            diff = list(difflib.unified_diff(json1_text.split('\n'), json2_text.split('\n')))
            return False, '\n'.join(diff)

        return True, ""

    def compare_deep(self, response1, response2, ignored_fields):
        json1 = prepare_json(get_cleared_json(json.loads(response1)['answers'], ignored_fields))
        json2 = prepare_json(get_cleared_json(json.loads(response2)['answers'], ignored_fields))
        return self.compare_json(json1, json2)

    def compare_schema(self, response1, response2, ignored_fields):
        json1 = json.loads(response1)
        json2 = json.loads(response2)
        responses = []
        path = ""

        json1_desc = get_json_description(json1)
        json2_desc = get_json_description(json2)
        clean_json_description(json1_desc, json2_desc)
        return self.compare_json(json1_desc, json2_desc)

    def compare_responses(self, comparator, raw_responses1, raw_responses2, raw_requests, ignored_fields):
        responses1 = []
        responses2 = []
        requests = []

        for line in raw_responses1:
            if line != '\n' and len(line.split('\t')) > 2:
                responses1.append(line.split('\t')[2])
        for line in raw_responses2:
            if line != '\n' and len(line.split('\t')) > 2:
                responses2.append(line.split('\t')[2])

        for line in raw_requests:
            if line != '\n':
                requests.append(line.strip())

        if len(responses1) != len(responses2):
            return False, [{'diff': "Different number of responses. Responses 1 length {}, responses 2 length {}".format(len(responses1), len(responses2))}]
        self.set_info("there is {} responses to compare".format(len(responses1)))

        global_ok = True
        global_diff = []
        for i in range(len(responses1)):
            ok, diff = comparator(responses1[i], responses2[i], ignored_fields)
            global_ok = global_ok and ok
            if not ok:
                global_diff.append({'diff': diff, 'resp1': str(responses1[i]), 'resp2': str(responses2[i]), 'reqs': str(requests[i])})

        return global_ok, global_diff

    def load_responses_resource(self, resource):
        resource_data = sdk2.ResourceData(resource)
        return resource_data.path.read_text().splitlines()

    def on_execute(self):
        ok = False
        diff_set = []
        responses1 = self.load_responses_resource(self.Parameters.responses1)
        responses2 = self.load_responses_resource(self.Parameters.responses2)
        requests = self.load_responses_resource(self.Parameters.requests)

        self.Context.service_config = self.load_service_config()
        self.Context.save()

        self.set_info("compare method: {}".format(self.Parameters.compare_method))
        ignored_fields = []
        if 'ignored_jsonpath' in self.Context.service_config:
            ignored_fields = self.Context.service_config['ignored_jsonpath']

        if self.Parameters.compare_method == "DEEP_COMPARE":
            ok, diff_set = self.compare_responses(self.compare_deep, responses1, responses2, requests, ignored_fields)
        if self.Parameters.compare_method == "SCHEMA_ONLY":
            ok, diff_set = self.compare_responses(self.compare_schema, responses1, responses2, requests, ignored_fields)

        self.set_info("global_ok: {}, len(global_diff): {}".format(ok, len(diff_set)))
        self.Parameters.has_diff = not ok
        self.Context.has_diff = not ok
        self.Context.save()

        if not ok:
            diff_resource = OTHER_RESOURCE(self, "Diff results", "compare_diff", ttl=14)
            diff_resource_data = sdk2.ResourceData(diff_resource)
            diff_resource_data.path.mkdir(0o755, parents=True, exist_ok=True)
            i = 0
            for diff in diff_set:
                diff_resource_data.path.joinpath("diff_{}".format(i)).mkdir(0o755, parents=True, exist_ok=True)
                diff_resource_data.path.joinpath("diff_{}/diff.txt".format(i)).write_bytes(diff['diff'])
                if 'resp1' in diff:
                    diff_resource_data.path.joinpath("diff_{}/response1.txt".format(i)).write_bytes(diff['resp1'])
                    diff_resource_data.path.joinpath("diff_{}/response2.txt".format(i)).write_bytes(diff['resp2'])
                    diff_resource_data.path.joinpath("diff_{}/request.txt".format(i)).write_bytes(diff['reqs'])
                i = i + 1
            diff_resource_data.ready()

    def on_failure(self, prev_status):
        self.set_info("on_failure called")

    def on_break(self, prev_status, status):
        self.set_info("on_break called")

    def load_service_config(self):
        with ProcessLog(self, 'bash_magic.log') as pl:
            environments.SvnEnvironment().prepare()

            sp.check_call(
                ["bash", "-c", "svn cat svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/ya | python - clone"],
                stdout=pl.stdout, stderr=pl.stderr
            )

            sp.check_call(
                ["arcadia/ya", "make", "--checkout", "arcadia/yweb/news/runtime_scripts/yappy"],
                stdout=pl.stdout, stderr=pl.stderr
            )

            service_config = {}
            with open("arcadia/yweb/news/runtime_scripts/yappy/" + self.Parameters.service_name + ".json") as conf:
                service_config = json.load(conf)

            self.set_info("Full service config: " + str(json.dumps(service_config, indent=4)))
            return service_config
