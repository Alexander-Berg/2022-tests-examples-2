package ru.yandex.autotests.metrika.utils;

import java.io.InputStream;
import java.io.OutputStream;

import org.apache.commons.io.IOUtils;
import org.apache.http.entity.AbstractHttpEntity;

public class EmptyHttpEntity extends AbstractHttpEntity {

    private static final InputStream emptyInputStream = IOUtils.toInputStream("");

    @Override
    public boolean isRepeatable() {
        return false;
    }

    @Override
    public long getContentLength() {
        return 0;
    }

    @Override
    public InputStream getContent() throws UnsupportedOperationException {
        return emptyInputStream;
    }

    @Override
    public void writeTo(OutputStream outstream) {}

    @Override
    public boolean isStreaming() {
        return false;
    }
}
