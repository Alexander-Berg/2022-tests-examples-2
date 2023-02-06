from sandbox.projects.adfox.adfox_ui.testpalm.testrunCreate.task import AdfoxTestRunCreateTask
from argparse import ArgumentParser
import logging
import sys

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    parser = ArgumentParser(description='Create testpalm testrun')
    parser.add_argument('--testpalm-token', dest='testpalm_token',
                        help="Testpalm oauth token", required=True)
    args = parser.parse_args()

    file = open('report.json')

    AdfoxTestRunCreateTask(
        testpalm_token=args.testpalm_token,
        report={},
        # report=json.loads(file.read()),
        project='pi-palmsync'
    ).execute()
    file.close()
