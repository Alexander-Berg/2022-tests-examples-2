import logging
import os
import sys
import time
import urllib2


def expand_host(host):
    if host == "hamster":
        return "hamster.yandex.ru"

    if "." not in host:
        return "{}.hamster.yandex.ru".format(host)

    return host


def url_open(url, retries=30):
    sleep = 1
    for i in range(retries + 1):
        try:
            return urllib2.urlopen(url).read()
        except Exception:
            time.sleep(sleep)
            sleep += 1

    raise Exception("retries limit exceeded (%s): %s" % (retries, url))


def url_open_strict(url):
    return url_open(url, retries=0)


class Beta:
    def __init__(self, host, cgi=None):
        self.Host = expand_host(host)
        self.Cgi = cgi if cgi else ""

    def __str__(self):
        return "%s?%s" % (self.Host, self.Cgi)


class TestBase:
    def __init__(self, prefix=None, config=None):
        self._Config = config if config else {}

        self._Prefix = prefix + "." if prefix else None
        self._Name = None

    def Ignore(self):
        return self.Name in self._Config.get("ignore", [])

    def Name(self):
        assert self._Name

        if self._Prefix:
            return self._Prefix + self._Name

        return self._Name

    def IsOK(self):
        raise NotImplementedError

    def Error(self):
        raise NotImplementedError


class TestsProvider:
    Name = None

    def __init__(self, config=None):
        assert self.Name

        self._Config = config.get(self.Name, {}) if config else {}

    @classmethod
    def Generate(cls, **args):
        return [cls(**args)]

    def _RunTest(self, beta):
        raise NotImplementedError

    def _IsOver(self, id):
        raise NotImplementedError

    def _Compare(self, id0, id1):
        raise NotImplementedError

    def _ParseDiff(self, diff):
        raise NotImplementedError

    def _WaitTest(self, id):
        logging.info("waiting %s: %s" % (self.Name, id))
        while True:
            over = self._IsOver(id)

            if over:
                break

            time.sleep(10)

    def RunTest(self, beta):
        logging.info("running test %s for %s" % (self.Name, beta))

        return {self.Name: self._RunTest(beta)}

    def IsOver(self, test):
        id = test.get(self.Name)
        if not id:
            return True

        return self._IsOver(id)

    def WaitTest(self, test):
        id = test.get(self.Name)
        if not id:
            return

        self._WaitTest(id)

    def StopTest(self, test):
        id = test.get(self.Name)
        if not id:
            return

        logging.info("stoping %s: %s" % (self.Name, id))
        if self._IsOver(id):
            return

        self._StopTest(id)

    def Diff(self, test0, test1):
        id0 = test0[self.Name]
        id1 = test1[self.Name]

        logging.info("diff %s: %s %s" % (self.Name, id0, id1))

        diff = self._Compare(id0, id1)

        return {self.Name: diff}

    def _DiffInfo(self, id0, id1):
        return

    def DiffInfo(self, test0, test1):
        id0 = test0[self.Name]
        id1 = test1[self.Name]

        info = self._DiffInfo(id0, id1)
        if not info:
            return []

        return ["Diff info %s: %s" % (self.Name, info)]

    def InternalErrors(self, test):
        return []

    def DiffErrors(self, diff):
        logging.info("parsing errors %s" % self.Name)
        diff = self._ParseDiff(diff[self.Name])

        errors = []
        for test in diff:
            if not test.IsOK():
                errors.append(test.Error())

        return errors

    def Run(self, beta0, beta1):
        betas = [beta0, beta1]

        tests = map(self.RunTest, betas)
        map(self.WaitTest, tests)

        diff_info = self.DiffInfo(*tests)

        errors = []
        for test in tests:
            errors.extend(self.InternalErrors(test))

        diff = self.Diff(*tests)
        errors.extend(self.DiffErrors(diff))

        if errors and diff_info:
            errors = diff_info + errors

        return errors

    def CheckTest(self, test):
        id = test.get(self.Name)
        if not id:
            return

        res = self._IsOver(id)
        sys.stdout.write("check %s %s %s\n" % (self.Name, id, res))

        internal_errors = self.InternalErrors(test)
        if internal_errors:
            sys.stdout.write("%s internal errors:\n%s\n" % (self.Name, "\n".join(internal_errors)))


class TestsContainer(TestsProvider):
    Name = "container"

    def __init__(self, testProviders, config=None, cachePath=None, cacheOnly=False, stopOnExit=False):
        TestsProvider.__init__(self, config=config)

        self.__Slaves = testProviders
        self.__CachePath = cachePath
        self.__CacheOnly = cacheOnly
        self.__StopOnExit = stopOnExit

        self.__TestsCache = {}  # Used to store running tests
        self.__TestsCachePath = os.path.join(self.__CachePath, "tests_cache.txt") if self.__CachePath else None

        if self.__CachePath and not os.path.isdir(self.__CachePath):
            assert (not os.path.exists(self.__CachePath))
            os.mkdir(self.__CachePath)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.__StopOnExit:
            map(self.StopTest, self.__TestsCache.values())
        self.__SaveTestsCache(self.__TestsCache)

    def __LoadTestsCache(self):
        if not self.__TestsCachePath or not os.path.exists(self.__TestsCachePath):
            return {}

        return eval(open(self.__TestsCachePath).read())

    def __SaveTestsCache(self, cache):
        if self.__TestsCachePath:
            with open(self.__TestsCachePath, "wb") as cacheFile:
                cacheFile.write("%s\n" % str(cache))

    def Hosts(self):
        self.__TestsCache = self.__LoadTestsCache()
        return self.__TestsCache.keys()

    def RunTest(self, beta):
        self.__TestsCache = self.__LoadTestsCache()
        betaCache = self.__TestsCache.get(str(beta), {})
        self.__TestsCache[str(beta)] = betaCache  # it will be updated later

        for slave in self.__Slaves:
            if slave.Name not in betaCache:
                if self.__CacheOnly:
                    raise Exception("No cache entry for %s %s" % (beta, slave.Name))
                betaCache.update(slave.RunTest(beta))

        self.__SaveTestsCache(self.__TestsCache)

        return betaCache

    def IsOver(self, test):
        raise NotImplementedError

    def WaitTest(self, tests):
        for slave in self.__Slaves:
            slave.WaitTest(tests)

    def StopTest(self, test):
        for slave in self.__Slaves:
            slave.StopTest(test)

    def Diff(self, test0, test1):
        res = {}
        for slave in self.__Slaves:
            diff = None
            if self.__CachePath:
                cachePath = os.path.join(self.__CachePath, "%s_result.txt" % slave.Name)
                if os.path.isfile(cachePath):
                    diff = {slave.Name: open(cachePath).read()}
            else:
                cachePath = None

            if not diff:
                diff = slave.Diff(test0, test1)
                assert (len(diff) == 1)

                if cachePath:
                    open(cachePath, "wb").write(diff[slave.Name])

            res.update(diff)

        return res

    def DiffInfo(self, *tests):
        res = []

        for slave in self.__Slaves:
            res.extend(slave.DiffInfo(*tests))

        return res

    def InternalErrors(self, test):
        res = []

        for slave in self.__Slaves:
            res.extend(slave.InternalErrors(test))

        return res

    def DiffErrors(self, diff):
        res = []

        for slave in self.__Slaves:
            res.extend(slave.DiffErrors(diff))

        return res

    def CheckTest(self, test):
        for slave in self.__Slaves:
            slave.CheckTest(test)
