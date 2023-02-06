package ru.yandex.metrika.mobmet.crash.service;

import java.util.List;

import org.assertj.core.api.Assertions;
import org.junit.Before;
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
public class AndroidStackTraceReportBuilderTest {

    @Parameterized.Parameter
    public String inputPath;

    @Parameterized.Parameter(1)
    public String expectedPath;

    @Parameterized.Parameter(2)
    public AppEventType eventType;

    @Parameterized.Parameter(3)
    public String eventName;

    private AndroidStackTraceReportBuilder stacktraceReportBuilder;

    private StackTraceReport expected;

    @Parameterized.Parameters(name = "{2}, input: {0}, expected: {1}")
    public static List<Object[]> createParameters() {
        return List.of(
                new Object[]{
                        "android-anr.json",
                        "android-anr-expected-format.yaml",
                        AppEventType.EVENT_PROTOBUF_ANR,
                        ""},
                new Object[]{
                        "android-crash.json",
                        "android-crash-expected-format.yaml",
                        AppEventType.EVENT_PROTOBUF_CRASH,
                        ""},
                new Object[]{
                        "android-error.json",
                        "android-error-expected-format.yaml",
                        AppEventType.EVENT_PROTOBUF_ERROR,
                        ""},
                new Object[]{
                        "android-deprecated-error.json",
                        "android-deprecated-error-expected-format.yaml",
                        AppEventType.EVENT_PROTOBUF_ERROR,
                        "Error message!"},
                new Object[]{
                        "android-deprecated-2-error.json",
                        "android-deprecated-2-error-expected-format.yaml",
                        AppEventType.EVENT_PROTOBUF_ERROR,
                        "Error message!"}
        );
    }

    @Before
    public void init() {
        stacktraceReportBuilder = new AndroidStackTraceReportBuilder();
        expected = parseYaml(loadResource(expectedPath));
    }

    @Test
    public void checkAndroidStackTraceReport() {
        String crashDecodedEventValue = loadResource(inputPath);
        CrashValue rawCrashValue = mockRawCrashValue(crashDecodedEventValue, eventType, eventName, OperatingSystem.ANDROID);
        StackTraceReport actual = stacktraceReportBuilder.buildReport(rawCrashValue, StackTraceFormat.COMPACT);
        Assertions.assertThat(actual).isEqualToComparingFieldByFieldRecursively(expected);
    }
}
