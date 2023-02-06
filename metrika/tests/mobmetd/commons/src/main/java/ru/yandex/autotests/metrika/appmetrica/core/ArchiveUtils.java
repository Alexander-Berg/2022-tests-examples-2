package ru.yandex.autotests.metrika.appmetrica.core;

import org.apache.commons.io.IOUtils;
import ru.yandex.autotests.metrika.appmetrica.exceptions.AppMetricaException;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.zip.GZIPInputStream;

public class ArchiveUtils {
    public static byte[] unGZip(byte[] source) {
        try (GZIPInputStream gzipIStream = new GZIPInputStream(new ByteArrayInputStream(source))) {
            return IOUtils.toByteArray(gzipIStream);
        } catch (IOException e) {
            throw new AppMetricaException(e);
        }
    }
}
