package ru.yandex.metrika.mobmet.crash.service;

import java.util.List;

import org.assertj.core.api.Assertions;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.mobmet.crash.model.crashvalue.CrashValue;
import ru.yandex.metrika.mobmet.crash.response.stacktrace.StackTraceReport;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.type.OperatingSystem;

import static ru.yandex.metrika.mobmet.crash.service.StackTraceTestUtils.loadResource;
import static ru.yandex.metrika.mobmet.crash.service.StackTraceTestUtils.mockRawCrashValue;
import static ru.yandex.metrika.mobmet.crash.service.StackTraceTestUtils.parseYaml;

@RunWith(Parameterized.class)
public class FlutterStackTraceReportBuilderTest {

    @Parameterized.Parameter
    public String inputPath;

    @Parameterized.Parameter(1)
    public String expectedPath;

    @Parameterized.Parameter(2)
    public AppEventType eventType;

    @Parameterized.Parameter(3)
    public String eventName;

    private final FlutterStackTraceReportBuilder stacktraceReportBuilder = new FlutterStackTraceReportBuilder();

    @Parameterized.Parameters(name = "{2}, input: {0}, expected: {1}")
    public static List<Object[]> createParameters() {
        return List.of(
                new Object[]{
                        "flutter-android-crash.json",
                        "flutter-android-crash-expected-format.yaml",
                        AppEventType.EVENT_PROTOBUF_CRASH,
                        ""},
                new Object[]{
                        "flutter-android-error.json",
                        "flutter-android-error-expected-format.yaml",
                        AppEventType.EVENT_PROTOBUF_ERROR,
                        ""},
                new Object[]{
                        "flutter-ios-error.json",
                        "flutter-ios-error-expected-format.yaml",
                        AppEventType.EVENT_PROTOBUF_ERROR,
                        ""}
        );
    }

    @Test
    public void checkFlutterStackTraceReport() {
        StackTraceReport expected = parseYaml(loadResource(expectedPath));
        String crashDecodedEventValue = loadResource(inputPath);
        CrashValue rawCrashValue = mockRawCrashValue(crashDecodedEventValue, eventType, eventName, OperatingSystem.ANDROID);
        StackTraceReport actual = stacktraceReportBuilder.buildReport(rawCrashValue, StackTraceFormat.COMPACT);
        Assertions.assertThat(actual).isEqualToComparingFieldByFieldRecursively(expected);
    }
}
