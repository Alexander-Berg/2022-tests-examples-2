import jupiter_cppproxy
from robot.jupiter.library.python import ytcpp


class TableBuffer(object):
    def __init__(self, path, protoclass, sorted_by=None):
        self.table = ytcpp.Table(path, protoclass)
        self.key_columns = sorted_by or self.table.sorted().key_columns()
        self.data = {}

    def add_proto(self, proto):
        key = self._extract_key_columns(proto)
        if key in self.data and self.data[key] is list:
            self.data[key].append(proto)
        else:
            self.data[key] = proto

    def add(self, **kwargs):
        self.add_proto(self.table.protobuf(**kwargs))

    def _input_stream(self):
        for v in self.data.values():
            if v is list:
                for x in v:
                    yield x
            else:
                yield v

    def _extract_key_columns(self, proto):
        return tuple([getattr(proto, k, None) for k in self.key_columns])

    def write(self, yt):
        yt.create_table(self.table, recursive=True)
        yt.write_table(self.table, self._input_stream())

    def sort(self, yt):
        yt.run_sort(self.table.sorted(by=self.key_columns))

    def read(self, yt):
        self.data.clear()
        for proto in yt.read_table(self.table):
            self.add_proto(proto)

    def __repr__(self):
        return repr(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return key in self.data

    def itervalues(self):
        return self.data.itervalues()


class BucketedTableBuffer(object):
    def __init__(self, path, protoclass, sorted_by=None, base_buckets_count=None, index_buckets_count=None):
        """@base_buckets_count or @index_buckets_count select type of bucketing (by url or by shard)

        @path should contains [bucket] which is replaced by bucket number
        """

        assert "[bucket]" in path, "Path should contain [bucket] to be replaced by bucket number: " + path
        assert (not base_buckets_count) ^ (not index_buckets_count), "Either base_buckets_count or index_buckets_count should be provided, but not both"

        self.tables = []
        self.base_buckets_count = base_buckets_count
        self.index_buckets_count = index_buckets_count
        for i in xrange(base_buckets_count or index_buckets_count):
            self.tables.append(TableBuffer(path.replace("[bucket]", str(i)), protoclass, sorted_by=sorted_by))

    def add(self, **kwargs):
        if self.base_buckets_count:
            bucket = jupiter_cppproxy.get_bucket_for_url(kwargs["Host"], kwargs["Path"], self.base_buckets_count)
        else:
            bucket = jupiter_cppproxy.get_bucket_for_shard(kwargs["Shard"], self.index_buckets_count)

        self.tables[bucket].add(**kwargs)

    def write(self, yt):
        for table in self.tables:
            table.write(yt)

    def sort(self, yt):
        for table in self.tables:
            table.sort(yt)

    def read(self, yt):
        for table in self.tables:
            table.read(yt)

    def itervalues(self):
        for table in self.tables:
            for v in table.itervalues():
                yield v

    def __repr__(self):
        ret = ""
        for i, table in enumerate(self.tables):
            ret += "{} : {}\n".format(i, repr(table))
        return ret

    def __getitem__(self, key):
        if self.base_buckets_count:
            bucket = jupiter_cppproxy.get_bucket_for_url(key[0], key[1], self.base_buckets_count)
        else:
            bucket = jupiter_cppproxy.get_bucket_for_shard(key[0], self.index_buckets_count)
        return self.tables[bucket][key]


class TableSetBuffer(object):
    def __init__(self):
        self.tables = []

    def _add_table(self, name, path, protoclass, sorted_by=None, base_buckets_count=None, index_buckets_count=None):
        if base_buckets_count or index_buckets_count:
            table = BucketedTableBuffer(path, protoclass, sorted_by=sorted_by, base_buckets_count=base_buckets_count, index_buckets_count=index_buckets_count)
        else:
            table = TableBuffer(path, protoclass, sorted_by=sorted_by)

        self.tables.append((name, table))
        setattr(self, name, table)

    def __repr__(self):
        ret = ""
        for name, table in self.tables:
            ret += "{}: {}\n\n".format(name, repr(table))
        return ret

    def finish(self, yt):
        for _, table in self.tables:
            table.write(yt)
            table.sort(yt)

    def read(self, yt):
        for _, table in self.tables:
            table.read(yt)
