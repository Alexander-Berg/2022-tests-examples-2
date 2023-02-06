package ru.yandex.metrika.mobmet.crash.service;

import java.time.ZonedDateTime;
import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.mockito.Mockito;

import ru.yandex.metrika.mobmet.crash.model.crashvalue.CrashValue;
import ru.yandex.metrika.mobmet.crash.response.stacktrace.StackTraceReport;
import ru.yandex.metrika.mobmet.dao.ApplicationTimeZoneProvider;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.type.OperatingSystem;

import static org.mockito.Matchers.anyInt;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.mobmet.crash.service.StackTraceTestUtils.loadResource;
import static ru.yandex.metrika.mobmet.crash.service.StackTraceTestUtils.mockRawCrashValue;

@RunWith(Parameterized.class)
public class IOSStackTraceTxtBuilderTest {

    private IOSStackTraceReportBuilder stacktraceReportBuilder;
    private TxtStackTraceReportBuilder txtStackTraceReportBuilder;

    @Parameterized.Parameter
    public String crashJson;
    @Parameterized.Parameter(1)
    public String expectedFile;
    @Parameterized.Parameter(2)
    public AppEventType eventType;

    @Parameterized.Parameters
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(new Object[]{"ios-crash.json", "ios-crash-expected-complete.txt", AppEventType.EVENT_PROTOBUF_CRASH})
                .add(new Object[]{"ios-anr.json", "ios-anr-expected-complete.txt", AppEventType.EVENT_PROTOBUF_ANR})
                .add(new Object[]{"ios-custom-error.json", "ios-custom-error-expected-complete.txt", AppEventType.EVENT_PROTOBUF_ERROR})
                .add(new Object[]{"ios-nserror-error.json", "ios-nserror-error-expected-complete.txt", AppEventType.EVENT_PROTOBUF_ERROR})
                .add(new Object[]{"ios-legacy-error.json", "ios-legacy-error-expected-complete.txt", AppEventType.EVENT_PROTOBUF_ERROR})
                .build();
    }

    @Before
    public void init() {
        stacktraceReportBuilder = new IOSStackTraceReportBuilder();
        ApplicationTimeZoneProvider appTimeZoneProvider = Mockito.mock(ApplicationTimeZoneProvider.class);
        when(appTimeZoneProvider.currentAppTime(anyInt()))
                .thenReturn(ZonedDateTime.parse("2020-03-01T10:00:00+03:00[Europe/Moscow]"));
        txtStackTraceReportBuilder = new TxtStackTraceReportBuilder(appTimeZoneProvider);
    }

    @Test
    public void checkIOSStackTraceReport() {
        String crashDecodedEventValue = loadResource(crashJson);
        CrashValue rawCrashValue = mockRawCrashValue(crashDecodedEventValue, eventType, "", OperatingSystem.IOS);
        StackTraceReport report = stacktraceReportBuilder.buildReport(rawCrashValue, StackTraceFormat.COMPLETE);
        String actual = txtStackTraceReportBuilder.convertReportToTxt(
                report, rawCrashValue, "https://appmetrica.yandex.ru/", StackTraceFormat.COMPLETE);

        String expected = loadResource(expectedFile);
        Assert.assertEquals(expected, actual);
    }
}
