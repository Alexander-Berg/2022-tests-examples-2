# -*- coding: utf-8 -*-

from sandbox.projects.common.arcadia import sdk
from sandbox.sandboxsdk.process import run_process

from threading import Thread
import shutil

import sandbox.sdk2 as sdk2
import os
import requests
import time
import logging


class TestYaToolApphost(sdk2.Task):
    class Requirements(sdk2.Task.Requirements):
        pass

    class Parameters(sdk2.Task.Parameters):
        mode = sdk2.parameters.String("Mode", default="agent", required=True)
        vertical = sdk2.parameters.String("Vertical (need upper_case)", default="WEB", required=True)
        is_nora = sdk2.parameters.Bool("Use nora config", default=False, required=True)

        actions = sdk2.parameters.List("Admin actions", sdk2.parameters.String, required=False)

        timeout = sdk2.parameters.Integer("Time for waiting upping apphost, in seconds", default=600, required=False)

    def read_stream(self, process, stream='stdout', debug_message=''):
        """
        Method is used for reading pipes from another thread
        """
        for line in iter(getattr(process, stream).readline, ''):
            logging.info(debug_message + line)

    def handle_admin_action(self, action):
        """
        Method is used for making admin action with upped apphost
        """
        logging.info('[INFO] Make action: {}'.format(action.title()))

        return requests.get('http://localhost:10090/admin?action={}'.format(action)).text

    def on_execute(self):
        logging.info("[INFO] Starting Task")

        # neccessary for mounting local arcadia
        os.environ['YT_TOKEN'] = sdk2.Vault.data("APP_HOST", 'robot-ah-evlogfilter-yt-token')

        logging.info("[INFO] Getting local arcadia")

        with sdk.mount_arc_path('arcadia-arc:/#trunk') as local_arcadia_path:
            logging.info("[INFO] Getting 'ya' path")
            ya_path = os.path.join(local_arcadia_path, 'ya')
            if not os.path.exists(ya_path):
                ya_path = os.path.join(local_arcadia_path, 'devtools', 'ya', 'ya')

            # neccessary for ya tool apphost for install path
            os.environ['_'] = ya_path

            # -y - force yes
            # --install-path - path for directory with apphost files
            # --local-arcadia-path - path for mount arcadia root
            # --run-app-host - run apphost
            # --vertical - vertical for upping apphost
            cmd = ya_path + " tool apphost setup -y --install-path {} ".format(os.path.join(local_arcadia_path, 'test_apphost_')) + \
                            "--local-arcadia-path {local_arcadia_path} --run-app-host {mode} --vertical {vertical}".format(local_arcadia_path=local_arcadia_path,
                                                                                                                           mode=self.Parameters.mode,
                                                                                                                           vertical=self.Parameters.vertical)

            if self.Parameters.is_nora:
                cmd += " --nora"

            logging.info('[INFO] Run comand: ' + cmd)

            process = run_process(cmd, wait=False, outs_to_pipe=True)

            # read messages from ya tool apphost
            Thread(target=self.read_stream, kwargs={'process' : process, 'stream' : 'stderr',
                                                               'debug_message' : '[Tool messages] '}).start()

            attempts = 0
            while attempts < (self.Parameters.timeout / 30):
                try:
                    attempts += 1
                    answer = self.handle_admin_action('ping')

                    if "pong" in answer:
                        logging.info('[INFO] Apphost answer: ' + answer)
                        logging.info('[INFO] Apphost is upped')
                        break
                    else:
                        raise
                except:
                    logging.info('[INFO] Can not make ping')

                    # wait upping apphost
                    logging.info('[INFO] Waiting apphost')
                    time.sleep(30)

            if attempts == (self.Parameters.timeout / 30):
                logging.info('[ERROR] Can not up apphost')
                raise

            if self.Parameters.actions:
                for action in self.Parameters.actions:
                    logging.info('[INFO] Apphost answer: ' + self.handle_admin_action(action))

            process.kill()

            logging.info('[INFO] Ending task')
