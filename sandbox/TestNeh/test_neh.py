#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script for testing arcadia/library/cpp/neh, by using nehc console utility
# Test can be use autonomous or within sandbox, - in autonomous mode it must be called from folder, contained nehc utility
# More info about nehc: http://wiki.yandex-team.ru/users/and42/neh/nehc
# More info on this script: http://wiki.yandex-team.ru/users/and42/neh/test_neh
#

import os
import io
import sys
import time
import subprocess
import traceback
import fcntl
import socket


class TTestError(Exception):
    def __init__(self, text):
        self.Text = text

    def __str__(self):
        return self.Text

##############################################################################################


def PipePopen(cmd, log=None, prefix='$'):
    if log is not None:
        log.write(unicode(prefix, errors='ignore'))
        if type(cmd) is unicode:
            log.write(cmd)
        else:
            log.write(unicode(cmd, errors='ignore'))
        log.write(u'\n')
        log.flush()
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, close_fds=True)


def IsPortFree(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', port))
        sock.close()
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.bind(('', port))
        sock.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', port))
        sock.close()
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock.bind(('', port))
        sock.close()
        return True
    except socket.error:
        return False

###############################################################################################


class TProcess:

    class TOutput:
        def __init__(self):
            self.Data = ''

    def __init__(self, log, prefix):
        self.Log = log
        self.Prefix = prefix
        self.Proc = None

    def RunProc(self, cmd):
        self.Proc = PipePopen(cmd, self.Log, self.Prefix)
        fd = self.Proc.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def StopProc(self):
        if self.Proc and self.Proc.returncode is None:
            try:
                self.Proc.kill()
            except OSError:
                pass

    def SendToProcess(self, data):
        try:
            self.Proc.stdin.write(data)
            self.Proc.stdin.flush()
            self.LogOutput(data)
        except IOError, exc:
            self.Log.write(unicode(self.Prefix, errors='ignore') + unicode('<<<<< (sending failed: %s)\n' % str(exc), errors='ignore'))
            self.Log.flush()

    def LogOutput(self, data):
        try:
            self.Log.write(unicode(self.Prefix, errors='ignore') + u'<<<<< ' + data)
            self.Log.flush()
        except TypeError:
            self.Log.write(unicode(self.Prefix, errors='ignore') + u'<<<<< (something binary)\n')
            self.Log.flush()

    def LogInput(self, data):
        try:
            self.Log.write(unicode(self.Prefix, errors='ignore') + u'>>>>> ' + unicode(data))
            self.Log.flush()
        except UnicodeDecodeError:
            self.Log.write(unicode(self.Prefix, errors='ignore') + u'>>>>> (something binary)\n')
            self.Log.flush()

    def ExpectFromProcessFullMatch(self, b, timelimit=3):
        def Validate(a, b, idx):
            if type(b) is str:
                b = ord(b)
            if type(a) is str:
                a = ord(a)
            if a != b:
                raise TTestError("raw bytes output different from expected at %d bytes (expect %d, receive %d)" % (idx, a, b))
            return b == a

        readBytes = 0
        while timelimit > 0:
            try:
                rb = self.Proc.stdout.read(len(b) - readBytes)
            except IOError, exc:
                if exc.errno != 11 and exc.errno != 35:
                    raise
                time.sleep(1)
                self.Proc.poll()
                timelimit -= 1
                continue
            for i in range(len(rb)):
                Validate(b[readBytes+i], rb[i], readBytes+i)
            readBytes += len(rb)
            self.LogInput(rb)
            if readBytes == len(b):
                return
            if len(rb) == 0:
                self.CheckExitStatus()
                time.sleep(1)
                self.Proc.poll()
                timelimit -= 1
        raise TTestError("expecting process output: %d raw bytes time out (received %d bytes)" % (len(b), readBytes))

    def ExpectFromProcess(self, template, timelimit=3):
        while timelimit > 0:
            try:
                inputLine = self.Proc.stdout.readline()
            except IOError, exc:
                if exc.errno != 11 and exc.errno != 35:
                    raise
                time.sleep(1)
                self.Proc.poll()
                timelimit -= 1
                continue
            self.LogInput(inputLine)
            if template in inputLine:
                return inputLine
            if len(inputLine) == 0:
                self.CheckExitStatus()
                time.sleep(1)
                self.Proc.poll()
                timelimit -= 1
        raise TTestError("expecting process output: '%s' time out" % template)

    def ExpectFromProcess2(self, templates, timelimit=3):
        while self.Proc.returncode is None and timelimit > 0:
            try:
                inputLine = self.Proc.stdout.readline()
            except IOError, exc:
                if exc.errno != 11 and exc.errno != 35:
                    raise
                time.sleep(1)
                self.Proc.poll()
                timelimit -= 1
                continue
            self.Log.flush()
            self.Log.write(unicode(self.Prefix, errors='ignore') + u'>>>>>' + unicode(inputLine, errors='ignore'))
            self.Log.flush()
            index = 0
            for tmp in templates:
                if tmp in inputLine:
                    return (index, inputLine)
                index += 1
            if len(inputLine) == 0:
                self.CheckExitStatus()
                time.sleep(1)
                self.Proc.poll()
                timelimit -= 1
        if timelimit == 0:
            raise TTestError("expecting process output (%s): time out" % str(templates))
        self.CheckExitStatus()

    def CheckExitStatus(self):
        if self.Proc.returncode is not None:
            self.LogInput(self.Proc.stdout.read())
            self.Log.write(unicode(self.Proc.stderr.read(), errors='ignore'))
            raise TTestError("process unexpectedly exit")

    # return False if process not exited
    def WaitProcessExit(self, timelimit=3, output=None):
        while self.Proc.returncode is None and timelimit > 0:
            try:
                inputData = self.Proc.stdout.read()
            except IOError, exc:
                if exc.errno != 11 and exc.errno != 35:
                    raise
                # not have data
                time.sleep(1)
                self.Proc.poll()
                timelimit -= 1
                continue
            if len(inputData) == 0:
                time.sleep(1)
                self.Proc.poll()
                timelimit -= 1
            elif output is not None:
                output.Data += inputData
            self.LogInput(inputData)
        if self.Proc.returncode is None:
            return False
        inputData = self.Proc.stdout.read()
        if len(inputData) != 0:
            if output is not None:
                output.Data += inputData
            self.LogInput(inputData)
        self.Log.write(unicode(self.Proc.stderr.read(), errors='ignore'))
        return True

    def Wait(self, timelimit=3, output=None):
        self.WaitProcessExit(timelimit, output)
        self.CheckExitStatus()


class TTestStage:
    def __init__(self, idx, function, description):
        self.Id = idx
        self.Function = function  # call(string, output_stream)
        self.Description = description


class TTestResult:
    def __init__(self):
        self.Error = None  # or TTestError
        self.Log = io.StringIO()


class TTestStages:
    def __init__(self):
        self.Stages = {}

    def Descriprion(self):
        s = "Stages:\n"
        for k, v in self.Stages.iteritems():
            s += '\t' + str(k) + '. ' + v.Description + '\n'
        return s

    def AddStage(self, function, description):
        self.Stages[len(self.Stages)] = TTestStage(len(self.Stages), function, description)

    def GetTestIndex(self, function):
        for i in range(len(self.Stages)):
            if self.Stages[i].Function == function:
                return i
        raise ValueError("unknown stage function")


class TNehcServer(TProcess):
    def __init__(self, log, prefix=None):
        if prefix is None:
            prefix = "srv$ "
        TProcess.__init__(self, log, prefix)

    def Quit(self, timelimit=10, output=None):
        self.SendToProcess('(exit command)\n')
        self.WaitQuit(timelimit=timelimit, output=output)

    def WaitQuit(self, timelimit=10, output=None, ignore_codes=[]):
        if not self.WaitProcessExit(timelimit=timelimit, output=output):
            self.Proc.kill()
            raise TTestError("nehc server locked on exit")
        if self.Proc.returncode != 0 and self.Proc.returncode not in ignore_codes:
            raise TTestError("nehc server return failure code on exit: returncode=%d" % self.Proc.returncode)


class TNehcClient(TProcess):
    def __init__(self, log, prefix=None):
        if prefix is None:
            prefix = "cln$ "
        TProcess.__init__(self, log, prefix)

    def WaitQuit(self, timelimit=10, output=None, ignore_codes=[]):
        if not self.WaitProcessExit(timelimit=timelimit, output=output):
            self.Proc.kill()
            raise TTestError("nehc client locked on exit")
        if self.Proc.returncode != 0 and self.Proc.returncode not in ignore_codes:
            raise TTestError("nehc client return failure code on exit: returncode=%d" % self.Proc.returncode)


class TNehTest(TTestStages):
    def __init__(self):
        TTestStages.__init__(self)
        self.Verbose = False

        def DefaultLogger(s):
            print >>sys.stdout, s
        # verbose[1..3] info loggers, - this hooks use sandbox for redirect output
        self.Log1 = DefaultLogger
        self.Log2 = DefaultLogger
        self.Log3 = DefaultLogger
        self.Nehc = './nehc'
        # need rotate ports for prevent busying after coredumping (port can be busy few minutes)
        self.MinPort = 40000
        self.MaxPort = 44000
        self.Protocols = ['http', 'netliba', 'post', 'post2', 'tcp', 'tcp2', 'udp']
        self.AddStage(TNehTest.TestSmallSimpleRequest, 'send small text request, receive mirror response')
        self.AddStage(TNehTest.TestBinaryDataRequest, 'send request data, contained all byte values [0..255], receive simple text response')
        self.AddStage(TNehTest.TestBinaryDataResponse, 'send simple text request data, receive response, contained all byte values [0..255]')
        # self.AddStage(TNehTest.TestCompleteSendingRequest, 'send request data, check complete sending flag')
        self.AddStage(TNehTest.TestCancelRequest, 'send request, cancel it, check detecting canceling on server side')
        # TODO: self.AddStage(TNehTest.TestMemoryLeak, 'send few thousand small requests, check memory consumpsion')
        # hardcode skipped tests (known/delayed/ignored troubles), contain tuples [ protocol, stage_function ]
        self.SkipTests = set()
        # http/GET request limit
        self.SkipTests.add(tuple(['http', TNehTest.TestBinaryDataRequest]))
        # netliba limit (cant use share memory so us testing method not work properly)
        # self.SkipTests.add(tuple(['netliba', TNehTest.TestCompleteSendingRequest]))
        # udp limit (in test used to big request for udp)
        # self.SkipTests.add(tuple(['udp', TNehTest.TestCompleteSendingRequest]))
        # self.SkipTests.add(tuple(['tcp', TNehTest.TestCompleteSendingRequest]))
        # by default use fake realization (more quick than real)
        # self.SkipTests.add(tuple(['post2', TNehTest.TestCompleteSendingRequest]))
        # by default use fake realization (more quick than real)
        # self.SkipTests.add(tuple(['tcp2', TNehTest.TestCompleteSendingRequest]))
        # some protcols can't cancel requests
        self.SkipTests.add(tuple(['tcp', TNehTest.TestCancelRequest]))
        self.SkipTests.add(tuple(['udp', TNehTest.TestCancelRequest]))
        self.Failed = 0
        # indexed by tuples [ protocol, TTestStage ], value = TTestResult
        self.Results = {}
        self.LastResult = None

    def Descriprion(self):
        s = TTestStages.Descriprion(self)
        s += "Protocols:\n\t"
        s += ', '.join(self.Protocols)
        s += "\nSkipped tests (known limits):\n"
        for p in self.Protocols:
            st = []
            for t in self.SkipTests:
                if t[0] == p or t[1] is None:
                    st.append(str(self.GetTestIndex(t[1])))
            if len(st):
                s += "\t" + p + ' - ' + ', '.join(st) + '\n'
        return s

    def SetSkipStages(self, stagesIndex):
        for k, stg in self.Stages.iteritems():
            if k in stagesIndex:
                self.SkipTests.add(tuple([None, stg.Function]))

    def ReSetStages(self, stagesIndex):
        for k, stg in self.Stages.iteritems():
            if k not in stagesIndex:
                self.SkipTests.add(tuple([None, stg.Function]))

    def Run(self):
        port = self.MinPort
        for stage in self.Stages.itervalues():
            if tuple([None, stage.Function]) in self.SkipTests:
                continue
            for proto in self.Protocols:
                if tuple([proto, None]) in self.SkipTests:
                    continue
                if tuple([proto, stage.Function]) in self.SkipTests:
                    continue

                if self.Verbose:
                    self.Log1("Run stage %d for protocol '%s' -- %s" % (stage.Id, proto, stage.Description))

                self.LastResult = TTestResult()
                self.Results[tuple([proto, stage])] = self.LastResult
                try:
                    range_start = port
                    try_ports_range = 100
                    for i in range(100+1):
                        if IsPortFree(port):
                            break
                        port += 1
                        if port >= self.MaxPort:
                            port = self.MinPort
                        if i == try_ports_range:
                            raise TTestError("can't detected free port [{}..{}]".format(range_start, port))
                    (stage.Function)(self, proto, port, self.LastResult.Log)
                except TTestError, exc:
                    self.Failed += 1
                    self.LastResult.Error = exc

                    if self.Verbose:
                        self.Log1("Error:" + str(exc))
                if self.Verbose >= 3:
                    self.Log3(self.LastResult.Log.getvalue())
                self.LastResult = None

    def ErrorsText(self):
        errText = ''
        for k, res in self.Results.iteritems():
            if res.Error:
                errText += "Protocol '%s' failed test stage %d (%s):\nError: %s\n" % (k[0], k[1].Id, k[1].Description, str(res.Error))
                errText += '='*20 + " Log " + '='*20 + '\n'
                errText += res.Log.getvalue()
                errText += '='*45 + '\n\n'
        return errText

    def TestSmallSimpleRequest(self, protocol, port, log):
        srv = None
        clnt = None
        try:
            srv = TNehcServer(log)
            srv.RunProc("%s -e '%s://*:%d/test'" % (self.Nehc, protocol, port))
            srv.Wait(1)
            clnt = TNehcClient(log)
            clnt.RunProc("%s '%s://localhost:%d/test' test_string" % (self.Nehc, protocol, port))
            clnt.ExpectFromProcessFullMatch('test_string')
            log.write(u"\ncln$ *** successfuly received mirror echo response ***\n")
            clnt.WaitQuit()
            srv.Quit(timelimit=3)
        finally:
            if clnt:
                clnt.StopProc()
            if srv:
                srv.StopProc()

    def TestBinaryDataRequest(self, protocol, port, log):
        srv = None
        clnt = None
        try:
            srv = TNehcServer(log)
            srv.RunProc("%s -s '%s://*:%d/test'" % (self.Nehc, protocol, port))
            srv.Wait(1)
            clnt = TNehcClient(log)
            clnt.RunProc("%s '%s://localhost:%d/test'" % (self.Nehc, protocol, port))
            data = bytearray(range(255))
            clnt.SendToProcess(data)
            clnt.Proc.stdin.close()
            srv.ExpectFromProcessFullMatch(data)
            log.write(u"srv$ *** successfuly received raw data request ***\n")
            srv.SendToProcess('test_string')
            srv.Proc.stdin.close()
            clnt.ExpectFromProcessFullMatch('test_string')
            log.write(u"\ncln$ *** successfuly received response ***\n")
            clnt.WaitQuit()
            srv.WaitQuit()
        finally:
            if clnt:
                clnt.StopProc()
            if srv:
                srv.StopProc()

    def TestBinaryDataResponse(self, protocol, port, log):
        srv = None
        clnt = None
        try:
            srv = TNehcServer(log)
            srv.RunProc("%s -s '%s://*:%d/test'" % (self.Nehc, protocol, port))
            srv.Wait(1)
            clnt = TNehcClient(log)
            clnt.RunProc("%s '%s://localhost:%d/test' test_string" % (self.Nehc, protocol, port))
            srv.ExpectFromProcessFullMatch('test_string')
            log.write(u"\nsrv$ *** successfuly receive request data ***\n")
            data = bytearray(range(255))
            srv.SendToProcess(data)
            srv.Proc.stdin.close()
            clnt.ExpectFromProcessFullMatch(data)
            log.write(u"cln$ *** successfuly receive raw data response ***\n")
            srv.WaitQuit()
            clnt.WaitQuit()
        finally:
            if clnt:
                clnt.StopProc()
            if srv:
                srv.StopProc()

    def TestCompleteSendingRequest(self, protocol, port, log):
        srv = None
        clnt = None
        try:
            srv = TNehcServer(log)
            srv.RunProc("%s -e -i 200 '%s://*:%d/test'" % (self.Nehc, protocol, port))
            srv.Wait(1)
            clnt = TNehcClient(log)
            clnt.RunProc("%s '%s://localhost:%d/test' -g 10000000 -v 3 -q" % (self.Nehc, protocol, port))
            output = TProcess.TOutput()
            clnt.WaitQuit(timelimit=10, output=output)
            if 'Complete sending message' in output.Data:
                if output.Data[1] != '-':  # try detect instant completion
                    raise TTestError('protocol has fake realisation completing message')
            else:
                raise TTestError('protocol not have realisation completing message')
            log.write(u"\ncln$ *** detect correct complete ***\n")
            srv.Quit(timelimit=3)
        finally:
            if clnt:
                clnt.StopProc()
            if srv:
                srv.StopProc()

    def TestCancelRequest(self, protocol, port, log):
        srv = None
        clnt = None
        try:
            srv = TNehcServer(log)
            srv.RunProc("%s -v 3 -e -i 500 '%s://*:%d/test'" % (self.Nehc, protocol, port))
            srv.Wait(1)
            clnt = TNehcClient(log)
            clnt.RunProc("%s '%s://localhost:%d/test' -c 100 -g 100 -v 3" % (self.Nehc, protocol, port))
            clnt.WaitQuit(ignore_codes=[4])  # 4 - code canceling
            output = TProcess.TOutput()
            srv.Quit(output=output)
            if 'Request canceled' in output.Data:
                return
            else:
                raise TTestError("server not detect canceling request")
        finally:
            if clnt:
                clnt.StopProc()
            if srv:
                srv.StopProc()

###############################################################################################


if __name__ == "__main__":

    nehTest = TNehTest()

    if sys.version_info < (2, 7):
        # can't make nice format for help in old pythons :(
        import optparse
        parser = optparse.OptionParser(usage="%prog [OPTIONS]\n"
                                       + '\nArcadia neh protocols testing.\n' + nehTest.Descriprion())

        parser.add_option('-s', '--skip', dest='skipStages', metavar='STAGE', type=int, help='skip given test stage')
        parser.add_option("-o", '--only', dest="onlyStages", metavar='STAGE', type=int, help='run only given test stage')
        parser.add_option('-p', '--protocols', dest='protocols', metavar='PROTOCOL', type=str, help='use only given protocol')
        parser.add_option('-v', '--verbose', dest='verbose', metavar='LEVEL', type=int, help='print process on console [0..3]')

        (options, args) = parser.parse_args()

        if options.protocols:
            nehTest.Protocols = [options.protocols, ]
        if options.skipStages:
            nehTest.SetSkipStages(options.skipStages)
        if options.onlyStages:
            nehTest.ReSetStages([options.onlyStages, ])
        nehTest.Verbose = options.verbose

    else:
        import argparse
        parser = argparse.ArgumentParser(description='Arcadia neh protocols testing.',
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=nehTest.Descriprion())
        parser.add_argument('-s', '--skip', dest='skipStages', metavar='STAGES', type=int, nargs='+', help='skip given tests stages')
        parser.add_argument('-o', '--only', dest='onlyStages', metavar='STAGES', type=int, nargs='+', help='run only given tests stages')
        parser.add_argument('-p', '--protocols', dest='protocols', metavar='PROTOCOLS', type=str, nargs='+', help='use only given protocols')
        parser.add_argument('-v', '--verbose', dest='verbose', metavar='LEVEL', type=int, help='print process on console [0..3]')

        args = parser.parse_args()

        if args.protocols:
            nehTest.Protocols = args.protocols
        if args.skipStages:
            nehTest.SetSkipStages(args.skipStages)
        if args.onlyStages:
            nehTest.ReSetStages(args.onlyStages)
        nehTest.Verbose = args.verbose

    try:
        nehTest.Run()
        if nehTest.Failed == 0:
            print "Successfully pass %d tests\n" % (len(nehTest.Results))
            exit(0)
        print >>sys.stderr, "Failed %d tests from %d:\n" % (nehTest.Failed, len(nehTest.Results)), nehTest.ErrorsText()
        exit(1)
    except Exception:
        print >>sys.stderr, "Internal test error: Catched run-time exception in test module:\n" + traceback.format_exc()
        if nehTest.LastResult:
            print >>sys.stderr, "Last log:\n" + nehTest.LastResult.Log.getvalue()
        exit(1)
