package ru.yandex.metrika.mobmet.crash.service;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
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
public class IOSStackTraceReportBuilderTest {

    private IOSStackTraceReportBuilder stacktraceReportBuilder;

    @Parameterized.Parameter
    public String crashJson;
    @Parameterized.Parameter(1)
    public String expectedYaml;
    @Parameterized.Parameter(2)
    public AppEventType eventType;

    @Parameterized.Parameters
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(new Object[]{"ios-crash.json", "ios-crash-expected.yaml", AppEventType.EVENT_PROTOBUF_CRASH})
                .add(new Object[]{"ios-anr.json", "ios-anr-expected.yaml", AppEventType.EVENT_PROTOBUF_ANR})
                .add(new Object[]{"ios-custom-error.json", "ios-custom-error-expected.yaml", AppEventType.EVENT_PROTOBUF_ERROR})
                .add(new Object[]{"ios-nserror-error.json", "ios-nserror-error-expected.yaml", AppEventType.EVENT_PROTOBUF_ERROR})
                .add(new Object[]{"ios-legacy-error.json", "ios-legacy-error-expected.yaml", AppEventType.EVENT_PROTOBUF_ERROR})
                .build();
    }

    @Before
    public void init() {
        stacktraceReportBuilder = new IOSStackTraceReportBuilder();
    }

    @Test
    public void checkIOSStackTraceReport() {
        String crashDecodedEventValue = loadResource(crashJson);
        CrashValue rawCrashValue = mockRawCrashValue(crashDecodedEventValue, eventType, "", OperatingSystem.IOS);
        StackTraceReport actual = stacktraceReportBuilder.buildReport(rawCrashValue, StackTraceFormat.COMPACT);
        StackTraceReport expected = parseYaml(loadResource(expectedYaml));
        //String yaml = StackTraceTestUtils.toYaml(actual);
        Assertions.assertThat(actual).isEqualToComparingFieldByFieldRecursively(expected);
    }
}
