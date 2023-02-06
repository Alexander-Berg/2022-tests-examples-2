package ru.yandex.metrika.mobmet.crash.service;

import java.io.IOException;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.fasterxml.jackson.dataformat.yaml.YAMLGenerator;

import ru.yandex.metrika.mobmet.crash.model.crashvalue.CrashValue;
import ru.yandex.metrika.mobmet.crash.response.stacktrace.StackTraceReport;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.type.OperatingSystem;
import ru.yandex.metrika.util.io.IOUtils;
import ru.yandex.metrika.util.io.UncheckedIOException;

import static ru.yandex.metrika.segments.apps.type.OperatingSystem.IOS;

public class StackTraceTestUtils {

    /**
     * Сериализуем в yaml, чтобы можно было читать то, что мы сделали
     */
    public static ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory()
            .disable(YAMLGenerator.Feature.WRITE_DOC_START_MARKER)
            .enable(YAMLGenerator.Feature.SPLIT_LINES)
            .enable(YAMLGenerator.Feature.LITERAL_BLOCK_STYLE));

    public static StackTraceReport parseYaml(String decodedValue) {
        try {
            return yamlMapper.readValue(decodedValue, StackTraceReport.class);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public static String toYaml(StackTraceReport report) {
        try {
            return yamlMapper.writeValueAsString(report);
        } catch (IOException ex) {
            throw new UncheckedIOException(ex);
        }
    }

    public static String loadResource(String path) {
        return IOUtils.resourceAsString(StackTraceTestUtils.class, "crashvalue/" + path);
    }

    public static CrashValue mockRawCrashValue(String crashDecodedEventValue,
                                               AppEventType eventType,
                                               String eventName,
                                               OperatingSystem operatingSystem) {
        return new CrashValue(
                13,
                eventType,
                null,
                null,
                "1234567890",
                "2020-03-03 10:00:00",
                "400004",
                "0987654321",
                null,
                "ru.yandex.appmetrica",
                "3.91",
                30098L,
                operatingSystem,
                operatingSystem == IOS ? "13.2.1" : "7.0",
                "phone model",
                0,
                false,
                crashDecodedEventValue,
                eventName
        );
    }
}
