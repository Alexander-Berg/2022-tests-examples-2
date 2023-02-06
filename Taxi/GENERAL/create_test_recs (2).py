import argparse

from zoo.expected_source.rec_sys.nirvana import common

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-path', type=str,
        required=False, default='config.json'
    )
    args = parser.parse_args()
    exp_manager = common.get_exp_manager(args.config_path)
    common.hahn_main(
        lambda job:
        exp_manager.create_test_recs(job, intensity='data'),
        cxx=True
    )
