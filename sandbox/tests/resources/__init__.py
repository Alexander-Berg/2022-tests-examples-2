import sandbox.sdk2 as sdk2


class ImagesTestlibOutput(sdk2.Resource):
    any_arch = True
    executable = False
    auto_backup = True
    calc_md5 = True
    share = True


class ImagesTestlibBinOutput(sdk2.Resource):
    any_arch = True
    executable = False
    auto_backup = True
    calc_md5 = True
    share = True
    parent_task = sdk2.Attributes.Integer("Parent task id")
    parent_task_type = sdk2.Attributes.String("Parent task type")
    testenv_database = sdk2.Attributes.String("TestEnv db")
