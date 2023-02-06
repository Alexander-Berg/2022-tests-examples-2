package ru.yandex.metrika.mobmet.crash.service;

import java.time.ZonedDateTime;

import org.assertj.core.api.Assertions;
import org.junit.Before;
import org.junit.Test;
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
import static ru.yandex.metrika.mobmet.crash.service.StackTraceTestUtils.parseYaml;

public class AndroidNativeStackTraceReportBuilderTest {

    private AndroidNativeStackTraceReportBuilder stacktraceReportBuilder;
    private TxtStackTraceReportBuilder txtStackTraceReportBuilder;
    private CrashValue rawCrashValue;

    @Before
    public void init() {
        String crashDecodedEventValue = loadResource("android-native-crash.json");
        rawCrashValue = mockRawCrashValue(crashDecodedEventValue, AppEventType.EVENT_PROTOBUF_CRASH, "", OperatingSystem.ANDROID);
        stacktraceReportBuilder = new AndroidNativeStackTraceReportBuilder();
        ApplicationTimeZoneProvider appTimeZoneProvider = Mockito.mock(ApplicationTimeZoneProvider.class);
        when(appTimeZoneProvider.currentAppTime(anyInt()))
                .thenReturn(ZonedDateTime.parse("2020-03-01T10:00:00+03:00[Europe/Moscow]"));
        txtStackTraceReportBuilder = new TxtStackTraceReportBuilder(appTimeZoneProvider);
    }

    @Test
    public void checkCompact() {
        StackTraceReport actual = stacktraceReportBuilder.buildReport(rawCrashValue, StackTraceFormat.COMPACT);
        StackTraceReport expected = parseYaml(loadResource("android-native-crash-expected-format.yaml"));
        Assertions.assertThat(actual).isEqualToComparingFieldByFieldRecursively(expected);
    }

    @Test
    public void checkComplete() {
        StackTraceReport parsedCrashValue = stacktraceReportBuilder.buildReport(rawCrashValue, StackTraceFormat.COMPLETE);
        String actual = txtStackTraceReportBuilder.convertReportToTxt(
                parsedCrashValue, rawCrashValue, "http://appmetrica.com", StackTraceFormat.COMPLETE);
        String expected = loadResource("android-native-crash-expected-format.txt");
        Assertions.assertThat(actual).isEqualTo(expected);
    }

}
