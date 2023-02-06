import os
import mmap

from sandbox.common import fs


def test__tail(tmpdir):
    tmpdir = str(tmpdir)
    fname = os.path.join(tmpdir, "2tail.txt")
    line_tmpl = "my test line {}\n"
    size = len(line_tmpl)
    lines = []
    with open(fname, 'w') as fh:
        left = mmap.ALLOCATIONGRANULARITY * 2.33
        while left > 0:
            line = line_tmpl.format(len(lines))
            fh.write(line)
            left -= size
            lines.append(line[:-1])
    lines.append('')

    with open(fname, 'r') as fh:
        assert list(fs.tail(fh, 2)) == lines[-2:]
        assert list(fs.tail(fh, len(lines) * 2)) == lines
        partial = mmap.ALLOCATIONGRANULARITY // size + 1
        assert list(fs.tail(fh, partial)) == lines[-partial:]


def test_allocate_file(tmpdir):
    tmpdir = str(tmpdir)
    fname1 = os.path.join(tmpdir, 'foo.dump')
    fname2 = os.path.join(tmpdir, 'bar.dump')
    size = 10 * 1024 ** 2
    assert fs.allocate_file(fname1, size)
    assert fs.allocate_file(fname2, size, force_seek=True)
    assert os.stat(fname1).st_size == size
    assert os.stat(fname2).st_size == size
