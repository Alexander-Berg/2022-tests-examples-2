# coding: utf-8

import logging
import os
from sandbox import sdk2
from sandbox.sdk2.helpers import subprocess as sp
from sandbox.common.errors import TemporaryError
import sandbox.common.types.misc as ctm
import tempfile
import shlex
from threading import Timer
from urlparse import urlparse
import datetime
from .. import video_constructor_utils as vc_utils


class CanvasMakeVideoInBrowserTest(sdk2.Task):
    """ opens specified html in browser to make screenshots and then runs ffmpeg to make a video """

    class Context(sdk2.Task.Context):
        current_attempt = 0

    class Requirements(sdk2.Task.Requirements):
        cores = 4
        ram = 12 * 1024
        dns = ctm.DnsType.DNS64

        class Caches(sdk2.Requirements.Caches):
            pass  # means that task do not use any shared caches

    class Parameters(vc_utils.CommonVideoParameters):
        pass

    def run_browser(self, src, url, width, height, fps):
        """Нарезает скриншоты из браузера в папку ScreenshotsSet переданной рабочей директории"""
        logging.info("Making screenshots in browser")
        browser_cmd = ("yandex-browser-beta --disable-gpu --headless --window-size={},{} --screenshots-set={} '{}' --ignore-audio-stream "
                       "--autoplay-policy=no-user-gesture-required --enable-logging --no-sandbox --ignore-certificate-errors "
                       "--enable-begin-frame-control --run-all-compositor-stages-before-draw").format(width, height, fps, url)

        retries_num = 20
        timeout_seconds = 30

        for _ in range(retries_num):
            with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("cmd")) as pl:
                pr = sp.Popen(shlex.split(browser_cmd), cwd=src, stdout=pl.stdout, stderr=sp.STDOUT)

                # если ни одного скриншота не создалось за долгое время, то значит браузер повис, и надо пробовать снова
                def kill_if_not_working():
                    screenshots_dir = os.path.join(src, 'ScreenshotsSet')
                    if not os.path.isdir(screenshots_dir) or not os.listdir(screenshots_dir):
                        pr.kill()

                timer = Timer(timeout_seconds, kill_if_not_working)
                try:
                    timer.start()
                    pr.wait()
                finally:
                    timer.cancel()

                if pr.returncode == 0:
                    break

            logging.warning("Browser doesn't make screenshots for %d seconds, retrying..." % timeout_seconds)

        if pr.returncode != 0:
            msg = "{} exit code {}".format(browser_cmd, pr.returncode)
            raise TemporaryError(msg)

    def prepare_cmd_for_png2mp4(self, src, out, fps, audio_path):
        cmd = [
            self.ffmpeg_bin,
            "-framerate", str(fps),
            "-i", os.path.join(src, "ScreenshotsSet/screenshot_%d.png")
        ]

        if audio_path:
            cmd += ["-i", audio_path]

        cmd += [
            "-c:v", "libx264",
            "-crf", "23",
            "-profile:v", "baseline",
            "-level", "3.0",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-ac", "2",
            "-b:a", "128k",
            "-movflags", "faststart"
        ]

        if audio_path:
            # adds silence if audio is shorter than video
            cmd += [
                "-filter_complex", "[1:0] apad",
                "-shortest"
            ]

        cmd += [out]

        return cmd

    def png2mp4(self, src, out, fps, audio_path):
        """Собирает видео из картинок с помощью ffmpeg"""
        logging.info("Converting file")

        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("cmd")) as pl:
            png2mp4_cmd = self.prepare_cmd_for_png2mp4(src, out, fps, audio_path)

            pr = sp.Popen(png2mp4_cmd, stdout=pl.stdout, stderr=sp.STDOUT)
            pr.wait()

            if pr.returncode != 0:
                msg = 'ffmpeg {} exit code {}'.format(src, pr.returncode)
                raise TemporaryError(msg)

    def get_audio_from_url(self, url, path):
        """Загружаем аудиодорожку по ссылке и записываем по переданному пути"""
        logging.info("Download audio from url: '%s'" % str(url))
        audio = self._session.get(url).content
        with open(path, 'w') as fh:
            fh.write(audio)
        logging.info("Downloading is done")

    def convert(self, url, width, height, fps, audio_url, name):
        """съемка видео в браузере с последующей отправкой в stillage"""
        work_dir = tempfile.mkdtemp()
        self.run_browser(work_dir, url, width, height, fps)

        audio_temp_path = None
        if audio_url:
            audio_name = os.path.basename(urlparse(audio_url).path)
            audio_temp_path = tempfile.NamedTemporaryFile().name + audio_name
            self.get_audio_from_url(audio_url, audio_temp_path)

        mp4_out_temp_path = tempfile.NamedTemporaryFile().name + ".mp4"
        self.png2mp4(work_dir, mp4_out_temp_path, fps, audio_temp_path)

        preview_out_temp_path = tempfile.NamedTemporaryFile().name + ".mp4"
        vc_utils.mp42preview(self, self.ffmpeg_bin, mp4_out_temp_path, preview_out_temp_path)

        packshot_out_temp_path = tempfile.NamedTemporaryFile().name + ".png"
        vc_utils.mp42packshot(self, self.ffmpeg_bin, mp4_out_temp_path, packshot_out_temp_path,
                              template_id=self.Parameters.template_id)

        # Заливаем в stillage
        file_name = "yandex_direct_vc_%s" % datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")

        video_filename = file_name + "_video.mp4"
        video_attachment_filename = name + ".mp4" if name else video_filename

        logging.info("Uploading files")
        with open(mp4_out_temp_path) as mp4_fh:
            mp4 = vc_utils.upload_to_stillage(self._session, mp4_fh.read(), video_filename,
                                              force_use_file_name=True,
                                              attachment_filename=video_attachment_filename)
        with open(preview_out_temp_path) as preview_fh:
            preview = vc_utils.upload_to_stillage(self._session, preview_fh.read(), file_name + "_preview.mp4")
        with open(packshot_out_temp_path) as packshot_fh:
            packshot = vc_utils.upload_to_stillage(self._session, packshot_fh.read(), file_name + "_packshot.png")

        logging.info(str(mp4.json()))
        logging.info(str(preview.json()))
        logging.info(str(packshot.json()))
        return (
            mp4.json()['id'], mp4.json()['url'],
            preview.json()['id'], preview.json()['url'],
            packshot.json()['id'], packshot.json()['url']
        )

    def on_execute(self):
        self.Context.current_attempt += 1
        last_attempt = self.Context.current_attempt == self.Parameters.max_restarts + 1

        self.ffmpeg_bin = '/usr/local/bin/ffmpeg'
        self._session = vc_utils.init_session()

        mp4_stillage_id = mp4_url = preview_stillage_id = preview_url = packshot_stillage_id = packshot_url = None
        success = True
        saved_exception = None

        try:
            (mp4_stillage_id, mp4_url,
             preview_stillage_id, preview_url,
             packshot_stillage_id, packshot_url) = self.convert(
                self.Parameters.url,
                self.Parameters.width,
                self.Parameters.height,
                self.Parameters.fps,
                self.Parameters.audio_url,
                self.Parameters.name
            )
        except Exception as e:
            if not last_attempt:
                if isinstance(e, TemporaryError):
                    msg = e.message
                else:
                    msg = "Unexpected exception: %s" % e.message
                    logging.exception(msg)
                raise TemporaryError(msg)

            logging.exception("Last attempt failed, we didn't get success :(")
            success = False
            saved_exception = e

        self.Parameters.mp4_url = mp4_url
        self.Parameters.mp4_stillage_id = mp4_stillage_id
        self.Parameters.preview_url = preview_url
        self.Parameters.preview_stillage_id = preview_stillage_id
        self.Parameters.packshot_url = packshot_url
        self.Parameters.packshot_stillage_id = packshot_stillage_id
        self.Parameters.success = success
        # вызывает webhook_url
        if self.Parameters.webhook_url:
            try:
                data = {
                    'task_id': self.id,
                    'mp4_stillage_id': mp4_stillage_id,
                    'mp4_url': mp4_url,
                    'preview_stillage_id': preview_stillage_id,
                    'preview_url': preview_url,
                    'packshot_stillage_id': packshot_stillage_id,
                    'packshot_url': packshot_url,
                    'success': success
                }
                logging.debug('web hook to %s with %s', self.Parameters.webhook_url, data)
                self._session.post(self.Parameters.webhook_url, json=data, timeout=1, verify=False)
            except Exception:
                logging.exception('web hook failed send post request to %s', self.Parameters.webhook_url)

        # если завершились не успешно, то переводим таску в статус EXCEPTION, чтобы такие таски было легко найти
        if not success:
            raise saved_exception
