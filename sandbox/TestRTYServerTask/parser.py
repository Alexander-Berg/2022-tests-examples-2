import logging
import os

from sandbox.sandboxsdk.errors import SandboxTaskFailureError


class Parser:
    def readFile_lines(self, filename, must_exist=False, must_not_empty=False):
        if not os.path.exists(filename):
            if must_exist or must_not_empty:
                raise SandboxTaskFailureError('results file %s does not exist' % filename)
            else:
                logging.info('warning: results file %s does not exist' % filename)
                return
        f = open(filename, 'r')
        lines = []
        try:
            lines = f.readlines()
            if len(lines) == 0 and must_not_empty:
                raise SandboxTaskFailureError('results file %s is empty' % filename)
        except Exception as e:
            logging.info('Exception <%s> caught while parsing %s' % (e, filename))
            return
        finally:
            f.close()
        return lines

    def getMusts(self, line):
        must_exs = False
        if line.find(':MUST_EXIST') != -1:
            line = line.replace(':MUST_EXIST', ':')
            must_exs = True
        must_nempty = False
        if line.find(':MUST_NOT_EMPTY') != -1:
            line = line.replace(':MUST_NOT_EMPTY', ':')
            must_exs = True
            must_nempty = True
        return line, must_exs, must_nempty

    def getFName(self, line, scr_vars):
        for var in sorted(scr_vars, key=lambda x: len(x), reverse=True):
            for var_w in ['${' + var + '}', var]:
                if var_w in line:
                    line = line.replace(var_w, '')
                    return line, var
            for beg in ('file:', 'new:', 'f:'):
                if var.startswith(beg):
                    var_n = var[len(beg):]
                    for var_w in ('${' + var_n + '}', var_n):
                        if var_w in line:
                            line = line.replace(var_w, '')
                            return line, var

        return line, None

    def getCtxField(self, line):
        if ':to:' in line:
            try:
                field = line[line.find(':to:') + len(':to:'):].split(':')[0]
                line = line.replace(':to:' + field, '')
                return line, field
            except:
                line = line.replace(':to:', '')
        return line, None

    def getWayToParse(self, line, ways):
        for way in ways:
            if way in line:
                pos = line.find(way) + len(way)
                params = line[pos:].strip(' :;,')
                return way, params
        return None, None

    def parseFileEW(self, filename, error_words, must_exist=False, must_not_empty=False):
        lines = self.readFile_lines(filename, must_exist, must_not_empty)
        if not isinstance(error_words, list):
            error_words = [error_words]
        for line in lines:
            for ew in error_words:
                if ew in line:
                    raise SandboxTaskFailureError(
                        'error signal word found in %s, first occurrence %s' % (filename, line))

        logging.info('file %s parsed with signal words %s, nothing found' % (filename, error_words))

    def getFromLines(self, lines, to_get, strict=False, last=False):
        to_get = str(to_get)
        result = []
        for line in lines:
            if to_get in line:
                value = ''
                if strict:
                    parts = line.strip().split()
                    if parts[0] != to_get or len(parts) != 2:
                        continue
                    value = parts[-1]
                else:
                    try:
                        value = line[line.find(to_get) + len(to_get):]
                        if last:
                            value = value.strip().split()[-1]
                    except:
                        value = ''
                result.append(value.strip())
        return result

    def parseFileGet(self, filename, to_get, must_exist=False, must_not_empty=False):
        lines = self.readFile_lines(filename, must_exist, must_not_empty)
        result = self.getFromLines(lines, to_get)
        logging.info('file %s parsed with getting %s. %s occurrences found' % (filename, to_get, len(result)))
        return result

    def parseDolbiloResults(self, filename, must_exist=False, must_not_empty=False):
        lines_to_ctx = {
            'error requests': 'dolbilo_errors',
            'requests/sec': 'result_rps',
            'avg req. time': 'avg_req_time'
        }
        lines_strict = {'requests'}
        fields_to_ctx = {
            'Ok': 'requests_ok',
            'requests': 'requests_total',
            'Bad gateway': 'result_errors',
            'Gateway time out': 'result_timeout',
            'Not found': 'result_empty',
            'Bad request': 'result_400'
        }
        lines = self.readFile_lines(filename, must_exist, must_not_empty)
        reqs_error = int(self.getFromLines(lines, 'error requests')[0])
        reqs_total = int(self.getFromLines(lines, 'requests', True)[0])
        other_errors = 0
        err_404 = 0
        started = False
        result = {}
        for line, cline in lines_to_ctx.items():
            result[cline] = self.getFromLines(lines, line, line in lines_strict) or ['0']
        for line in lines:
            if line.strip() == '':
                if started:
                    break
                else:
                    started = True
            elif started:
                parts = line.strip().split()
                value = int(parts[-1])
                name = ' '.join(parts[:-1])
                if name == 'Not found':
                    err_404 = value
                elif name != 'Ok':
                    other_errors += value
                    reqs_error += value
                if name in fields_to_ctx:
                    result[fields_to_ctx[name]] = value

        try:
            result['result_empty_perc'] = 100 * float(err_404) / reqs_total
        except:
            result['result_empty_perc'] = -1

        try:
            result['dolbilo_errors_perc'] = 100 * float(reqs_error) / reqs_total
            result['result_errors'] = [str(reqs_error)]
        except:
            result['dolbilo_errors_perc'] = -1
        return result

    def writeContext(self, ctx_field, result, ctx):
        try:
            ', '.join(result)
            if isinstance(result, str):
                result = [result, ]
        except:
            result = [str(result), ]
        if ctx.get(ctx_field, ''):
            ctx[ctx_field] = str(ctx.get(ctx_field, '')) + ', ' + ', '.join(result)
        else:
            ctx[ctx_field] = ', '.join(result)

    dummy = ''
