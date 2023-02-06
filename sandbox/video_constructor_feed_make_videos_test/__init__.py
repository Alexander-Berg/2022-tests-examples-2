# coding: utf-8

import os
import logging
import tempfile
import zipfile
import json
import datetime
from sandbox import sdk2
import sandbox.common.types.task as ctt
import sandbox.common.types.misc as ctm
from .. import video_constructor_utils as vc_utils
from .. import html2video


def make_url(url, row_num):
    """
    Добавляем к ссылке для превью параметр с номером строки
    """
    return "%s&row_num=%d" % (url, row_num)


def get_row_numbers(row_numbers):
    """
    Преобразовать диапазоны в плоский список номеров строк
    p.s. конечно, можно сделать данное преобразование быстрее за O(кол-во диапазонов), но здесь не важно
    """
    logging.info("Getting plain row numbers")

    result = []

    for row_range in row_numbers:
        parts = row_range.split('-', 1)
        if len(parts) == 1:
            result.append(int(parts[0]))
        elif len(parts) == 2:
            # правая граница диапазона включительно
            result.extend(xrange(int(parts[0]), int(parts[1]) + 1))

    return sorted(set(result))


def get_video_infos(row_numbers, prefix_name, common_audio_url, audio_urls_dict):
    digits_number = len(str(row_numbers[-1]))

    return [
        {
            "row_num": row_num,
            "name": u"%s.№%0*d" % (
                prefix_name if prefix_name else "Video",
                digits_number,
                row_num + 1
            ),
            "audio_url": audio_urls_dict[str(row_num)] if audio_urls_dict.get(str(row_num)) else common_audio_url
        } for row_num in row_numbers
    ]


def make_archive_filename(archive_filename, archive_num):
    return "%s_%s.zip" % (archive_filename, archive_num)


class CanvasMakeFeedVideosTest(sdk2.Task):
    """ Task for creating a bundle of videos for each offer in feed """
    MAX_ARCHIVE_SIZE_BYTES = 300 * 1024 * 1024

    class Context(sdk2.Task.Context):
        video_task_ids = []

    class Requirements(sdk2.Task.Requirements):
        cores = 1
        ram = 2 * 1024
        dns = ctm.DnsType.DNS64

        class Caches(sdk2.Requirements.Caches):
            pass  # means that task do not use any shared caches

    class Parameters(vc_utils.CommonVideoParameters):
        max_restarts = 0  # ретраи сделаны в дочерних тасках на съемку

        row_numbers = sdk2.parameters.List("Row numbers (ranges, numbering from 0)", required=True)
        archive_name = sdk2.parameters.String("Archive name", required=False)
        audio_urls = sdk2.parameters.JSON("Audio urls (row_num -> audio_url)", required=False)

        with sdk2.parameters.Output:
            mp4_urls = sdk2.parameters.List("mp4 urls", required=False)
            archive_url = sdk2.parameters.String("archive url", required=False)
            archive_urls = sdk2.parameters.List("archive urls", required=False)

    def make_videos(self, video_infos):
        """
        Запускам таски на создание пачки видео, дожидаемся завершения и возвращаем их результат
        """
        logging.info("Start creating tasks")

        with self.memoize_stage.create_children_tasks:
            for video_info in video_infos:
                logging.info("Creating task %d" % video_info['row_num'])

                html2video_task = html2video.CanvasMakeVideoInBrowser(
                    self,
                    url=make_url(self.Parameters.url, video_info['row_num']),
                    audio_url=video_info['audio_url'],
                    width=self.Parameters.width,
                    height=self.Parameters.height,
                    fps=self.Parameters.fps,
                    name=video_info['name'],
                    template_id=self.Parameters.template_id
                ).enqueue()

                self.Context.video_task_ids.append(html2video_task.id)

            logging.info("Waiting tasks to finish")
            raise sdk2.WaitTask(
                self.Context.video_task_ids,
                ctt.Status.Group.FINISH | ctt.Status.Group.BREAK,
                wait_all=True,
                timeout=86400
            )

        logging.info("All tasks are finished")

        result = []
        for task_id in self.Context.video_task_ids:
            task = sdk2.Task[task_id]
            result.append({
                'mp4_url': str(task.Parameters.mp4_url) if task.Parameters.mp4_url else None,
                'mp4_stillage_id': str(task.Parameters.mp4_stillage_id) if task.Parameters.mp4_stillage_id else None,
                'preview_url': str(task.Parameters.preview_url) if task.Parameters.preview_url else None,
                'preview_stillage_id': (str(task.Parameters.preview_stillage_id)
                                        if task.Parameters.preview_stillage_id
                                        else None),
                'packshot_url': str(task.Parameters.packshot_url) if task.Parameters.packshot_url else None,
                'packshot_stillage_id': (str(task.Parameters.packshot_stillage_id)
                                         if task.Parameters.packshot_stillage_id
                                         else None)
            })
        logging.info(result)

        return result

    def get_video_from_url(self, url, path):
        """
        Загружаем видео по ссылке и записываем по переданному пути
        """
        logging.info("Download video from url: '%s'" % str(url))
        audio = self._session.get(url).content
        with open(path, 'w') as fh:
            fh.write(audio)
        logging.info("Downloading is done")

    def make_archive(self, urls, video_infos):
        """
        Создаем несколько zip-архивов из всех видео, загружаем их в стиллаж и возвращаем ссылки
        """
        logging.info("Start making zip-archive")

        temp_dir = tempfile.mkdtemp()
        for url, video_info in zip(urls, video_infos):
            if url:
                self.get_video_from_url(url, os.path.join(temp_dir, video_info['name'] + ".mp4"))

        archive_filename = "yandex_direct_vc_%s_feed_videos" % datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")

        current_archive_size = 0
        current_archive_num = 1

        zf = zipfile.ZipFile(
            make_archive_filename(archive_filename, current_archive_num),
            "w",
            zipfile.ZIP_DEFLATED,
            allowZip64=True
        )

        try:
            for name in sorted(os.listdir(temp_dir)):
                file_path = os.path.normpath(os.path.join(temp_dir, name))
                file_size = os.stat(file_path).st_size

                if file_size + current_archive_size > self.MAX_ARCHIVE_SIZE_BYTES:
                    zf.close()

                    current_archive_size = 0
                    current_archive_num += 1

                    zf = zipfile.ZipFile(
                        make_archive_filename(archive_filename, current_archive_num),
                        "w",
                        zipfile.ZIP_DEFLATED,
                        allowZip64=True
                    )

                current_archive_size += file_size
                zf.write(file_path, name)
        finally:
            zf.close()

        logging.info("Zip-archives are done: %s, total archives number: %d" % (archive_filename, current_archive_num))

        archive_urls = []

        for archive_num in range(1, current_archive_num + 1):
            archive_attachment_filename = make_archive_filename(
                self.Parameters.archive_name
                if self.Parameters.archive_name
                else archive_filename,
                archive_num
            )

            logging.info("Uploading zip-archive number %d to stillage" % archive_num)

            current_archive_filename = make_archive_filename(archive_filename, archive_num)
            with open(current_archive_filename) as archive_fh:
                archive = vc_utils.upload_to_stillage(self._session, archive_fh.read(), current_archive_filename,
                                                      force_use_file_name=True,
                                                      attachment_filename=archive_attachment_filename)

            logging.info("Zip-archive number %d was successfully uploaded to stillage" % archive_num)
            logging.info(str(archive.json()))

            archive_urls.append(archive.json()['url'])

        logging.info("All zip-archives were uploaded to stillage")

        return archive_urls

    def on_execute(self):
        self._session = vc_utils.init_session()

        mp4_urls = archive_url = archive_urls = mp4_stillage_id = mp4_url = preview_stillage_id = preview_url =\
            packshot_stillage_id = packshot_url = None
        success = True
        saved_exception = None

        row_numbers = get_row_numbers(self.Parameters.row_numbers)
        if len(row_numbers) == 0:
            raise ValueError("Empty list of row numbers")

        audio_urls_dict = json.loads(self.Parameters.audio_urls) if self.Parameters.audio_urls else {}

        video_infos = get_video_infos(
            row_numbers,
            self.Parameters.name,
            self.Parameters.audio_url,
            audio_urls_dict
        )

        try:
            videos = self.make_videos(video_infos)

            mp4_urls = [video['mp4_url'] for video in videos]
            if any(mp4_url for mp4_url in mp4_urls):
                archive_urls = self.make_archive(mp4_urls, video_infos)
                archive_url = archive_urls[0]

            ready_video = next((video for video in videos if video['mp4_url']), videos[0])
            # берем значения для превью из первого видео в пачке
            mp4_stillage_id = ready_video['mp4_stillage_id']
            mp4_url = ready_video['mp4_url']
            preview_stillage_id = ready_video['preview_stillage_id']
            preview_url = ready_video['preview_url']
            packshot_stillage_id = ready_video['packshot_stillage_id']
            packshot_url = ready_video['packshot_url']
        except Exception as e:
            success = False
            saved_exception = e

        self.Parameters.mp4_urls = mp4_urls
        self.Parameters.archive_url = archive_url
        self.Parameters.archive_urls = archive_urls
        self.Parameters.mp4_stillage_id = mp4_stillage_id
        self.Parameters.mp4_url = mp4_url
        self.Parameters.preview_stillage_id = preview_stillage_id
        self.Parameters.preview_url = preview_url
        self.Parameters.packshot_stillage_id = packshot_stillage_id
        self.Parameters.packshot_url = packshot_url
        self.Parameters.success = success

        if self.Parameters.webhook_url:
            try:
                data = {
                    'mp4_stillage_id': mp4_stillage_id,
                    'mp4_url': mp4_url,
                    'preview_stillage_id': preview_stillage_id,
                    'preview_url': preview_url,
                    'packshot_stillage_id': packshot_stillage_id,
                    'packshot_url': packshot_url,
                    'feed_archive_url': archive_url,
                    'feed_archive_urls': archive_urls,
                    'feed_mp4_urls': mp4_urls,
                    'success': success
                }
                logging.debug('Web hook to %s with %s', self.Parameters.webhook_url, data)
                self._session.post(self.Parameters.webhook_url, json=data, timeout=1, verify=False)
            except Exception:
                logging.exception('Web hook failed send post request to %s', self.Parameters.webhook_url)

        if not success:
            raise saved_exception
