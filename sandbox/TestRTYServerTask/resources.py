
import logging
import os

from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.paths import get_unique_file_name
from sandbox.sandboxsdk.paths import list_dir
from sandbox.sandboxsdk.paths import make_folder
from sandbox.sandboxsdk.paths import remove_path
from sandbox.sandboxsdk.paths import copy_path, chmod
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.svn import Arcadia

from sandbox.projects.common import apihelpers


class ResourceManager:
    tarExt = ('.tar.gz', '.tgz', '.tar.gzip')

    def unpackTar(self, tarname, target=None):
        if not target:
            target = tarname
            for ext in self.tarExt:
                target = target.replace(ext, '')
        make_folder(target)
        run_process(["tar", "xvf", tarname, "-C", target], log_prefix='untar')
        unpacked = list_dir(target, abs_path=True)
        if len(unpacked) == 1:
            return unpacked[0]
        else:
            return target

    def get_attribute(self, resource, attrName, defaultValue):
        try:
            attrValue = resource.attributes.get(attrName, defaultValue)
        except:
            attrValue = defaultValue
        return attrValue

    def checkSvnUpd(self, res_ex, downPath):
        if res_ex:
            rev_ex = self.get_attribute(res_ex, 'revision', 0)
        else:
            rev_ex = 0
        rev_new = Arcadia.info(downPath)['commit_revision']
        return int(rev_new) > int(rev_ex), rev_new

    def get_or_download_resource(self, task, resType, attrName, attrValue, downTo=None):
        if not downTo:
            downTo = get_unique_file_name(task.abs_path(), str(resType) + '_res')
        downPath = attrValue if attrName == 'from_path' else None

        logging.info('looking for resource %s %s' % (attrName, attrValue))
        res_ex = apihelpers.get_last_resource_with_attribute(resType, attrName, attrValue)
        logging.info('found: %s' % res_ex)

        key_rev = 0
        if attrName == 'key':
            downPath, key_rev, upd_key = self.process_key(task, attrValue, res_ex)
            if upd_key:
                res_ex = None

        if not downPath and not res_ex:
            raise SandboxTaskFailureError('cannot find resource with attr %s = %s' % (attrName, attrValue))

        if res_ex and not downPath:
            channel.task.sync_resource(res_ex.id)
            res_ex = channel.sandbox.get_resource(res_ex.id)
            logging.info("local resource %s %s" % (str(res_ex.id), res_ex.path))
            return res_ex

        if 'svn+ssh' in downPath:
            svnNew, new_rev = self.checkSvnUpd(res_ex, downPath)
        else:
            svnNew, new_rev = False, 0

        if res_ex and svnNew:
            res_ex = None
        if res_ex:
            channel.task.sync_resource(res_ex.id)
            res_ex = channel.sandbox.get_resource(res_ex.id)
            logging.info('found resource %s' % res_ex)
        if not res_ex:
            downTo = get_unique_file_name(os.path.dirname(downTo), os.path.basename(downTo) + '_res')
            if downPath.endswith(self.tarExt):
                downTo += '.tar.gz'
            if os.path.exists(downTo):
                remove_path(downTo)
            try:
                task.remote_copy(downPath, downTo, create_resource=False, resource_type=resType,
                                 resource_descr=str(resType))
                if downPath.startswith('rbtorrent'):
                    downTo = list_dir(downTo, abs_path=True)[0]
                res_ex = task._create_resource(str(resType), downTo, resType, complete=1)
            except Exception as e:
                logging.error("fail to copy remote resource %s, exception %s" % (downPath, e))
                raise SandboxTaskFailureError(e)
            channel.sandbox.set_resource_attribute(res_ex.id, 'from_path', downPath)
            if 'svn+ssh' in downPath:
                channel.sandbox.set_resource_attribute(res_ex.id, 'revision', new_rev)
            channel.sandbox.set_resource_attribute(res_ex.id, attrName, attrValue)

        res_ex.path = channel.sandbox.get_resource(res_ex.id).path

        if key_rev > 0 and self.get_attribute(res_ex, 'revision', 0) < key_rev:
            channel.sandbox.set_resource_attribute(res_ex.id, 'revision', key_rev)

        logging.info("local resource %s %s" % (str(res_ex.id), res_ex.path))
        task.ctx['resources_used'] = task.ctx.get('resources_used', [])
        task.ctx['resources_used'].append({'id': "<a href='http://sandbox.yandex-team.ru/resource/{0}/view'>{0}</a>".format(res_ex.id), 'descr': '%s' % res_ex})
        return res_ex

    def readSvnFile(self, svn_path, task):
        tmp_path = get_unique_file_name(task.abs_path(), 'key_tmp')
        Arcadia.export(svn_path, tmp_path)
        from_path = ''
        with open(tmp_path, 'r') as f:
            lines = f.read().split('\n')
            for line in lines:
                if len(line.strip()) > 0:
                    from_path = line.strip()
                    break
        return from_path

    def process_key(self, task, key, res_ex):
        logging.info('checking key %s, last existing resource %s' % (key, res_ex))
        from_path = ''
        if res_ex:
            from_path = self.get_attribute(res_ex, 'from_path', None)
        key_path = os.path.join(task.default_keys_path, key + '.txt')
        try:
            needs_upd_key, key_rev = self.checkSvnUpd(res_ex, key_path)
        except Exception as e:
            logging.warning('cannot check for keys update, svn path %s, exception %s' % (key_path, e))
            needs_upd_key = False
            key_rev = 0
        if needs_upd_key:
            try:
                from_path = self.readSvnFile(key_path, task)
                logging.info('key %s needs update, path %s' % (key, from_path))
            except Exception as e:
                logging.warning('error while reading %s, exception %s' % (key_path, e))

        return from_path, key_rev, needs_upd_key

    def get_resource_with_two_attrs(self, rtype, at1, v1, at2, v2):
        res = apihelpers.get_last_resource_with_attrs(rtype, {at1: v1, at2: v2}, True)
        if not res:
            raise SandboxTaskFailureError('resource not found')
        channel.task.sync_resource(res.id)
        return channel.sandbox.get_resource(res.id)

    def get_resource_to_task_dir(self, task, resType, attrName, attrValue, downTo=None):
        if not downTo:
            downTo = get_unique_file_name(task.abs_path(), str(resType) + '_res')
        res = self.get_or_download_resource(task or self, resType, attrName, attrValue, downTo)
        if res.path == downTo:
            logging.info("warning: resource for copy is already here %s" % downTo)
            return downTo
        logging.info("copying to path %s" % downTo)
        if os.path.exists(downTo):
            remove_path(downTo)
        if not res.path.endswith(self.tarExt):
            copy_path(res.path, downTo)
        else:
            downTo = self.unpackTar(res.path, downTo)

        try:
            chmod(downTo, 0o777)
        except:
            pass
        os.chmod(downTo, 0o777)
        return downTo
