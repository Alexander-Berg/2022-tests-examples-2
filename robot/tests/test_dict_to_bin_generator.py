import filecmp
from shutil import copyfile
import os

import yatest.common


def test_dict_to_bin_generator():
    gen = yatest.common.binary_path('robot/jupiter/legacy/dict_to_bin_generator/dict_to_bin_generator')

    work_dir = yatest.common.work_path("")
    tmp_dir = "{}/{}".format(work_dir, 'tmp')
    os.makedirs(tmp_dir)

    for file_name in ('link_adult.dict', 'link_porno.dict', 'new_direct.dict'):

        data_file = "{}/{}".format('robot/jupiter/legacy/legacy_data/', file_name)
        data = yatest.common.source_path(data_file)

        input = "{}/{}".format(tmp_dir, 'input_' + file_name)
        copyfile(data, input)

        yatest.common.execute([gen, input])

        output = input + ".bin"
        result = yatest.common.source_path(output)

        expected_file = "{}/{}".format('robot/jupiter/legacy/legacy_data/', file_name + ".bin")
        expected_result = yatest.common.source_path(expected_file)

        assert filecmp.cmp(expected_result, result)
