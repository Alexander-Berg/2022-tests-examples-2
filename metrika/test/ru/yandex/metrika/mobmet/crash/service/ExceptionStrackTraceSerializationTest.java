package ru.yandex.metrika.mobmet.crash.service;

import java.util.List;

import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.model.crashvalue.CrashValue;
import ru.yandex.metrika.mobmet.crash.model.crashvalue.android.AndroidCrashValue;
import ru.yandex.metrika.mobmet.crash.model.crashvalue.android.fields.AllThreads;
import ru.yandex.metrika.mobmet.crash.model.crashvalue.android.fields.Throwable;
import ru.yandex.metrika.mobmet.crash.model.crashvalue.android.fields.TraceNode;
import ru.yandex.metrika.mobmet.crash.response.stacktrace.StackTraceReport;
import ru.yandex.metrika.mobmet.crash.response.stacktrace.StackTraceUnit;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.type.OperatingSystem;

import static java.util.Collections.emptyList;
import static ru.yandex.metrika.mobmet.crash.service.StackTraceTestUtils.mockRawCrashValue;

/**
 * Мы не можем просто конвертировать java исключение в decoder объект и сравнить строки.
 * Потому что java исключение печатает ещё имя модуля, которого у нас нет.
 * Поэтому приходится конструировать безумные объекты и жить с этим.
 */
public class ExceptionStrackTraceSerializationTest {

    private final AndroidStackTraceReportBuilder stackTraceReportBuilder = new AndroidStackTraceReportBuilder();

    @Test
    public void testSimple() {
//        java.lang.Throwable exception = new IllegalArgumentException();
//        exception.printStackTrace();

        AndroidCrashValue crashValue = exception(new Throwable(
                "java.lang.IllegalArgumentException",
                null,
                List.of(
                        new TraceNode("ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest",
                                "ExceptionStrackTraceSerializationTest.java", 25, "test", false),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                null, -2, "invoke0", true),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                "NativeMethodAccessorImpl.java", 62, "invoke", false)),
                null,
                List.of()
        ));

        String expected = "" +
                "java.lang.IllegalArgumentException\n" +
                "\tat ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest.test(ExceptionStrackTraceSerializationTest.java:25)\n" +
                "\tat jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)\n" +
                "\tat jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)";

        String actual = getActualThrowableText(crashValue);
        Assert.assertEquals(expected, actual);
    }

    @Test
    public void testWithMessage() {
//        java.lang.Throwable exception = new IllegalArgumentException("bad test");
//        exception.printStackTrace();

        AndroidCrashValue crashValue = exception(new Throwable(
                "java.lang.IllegalArgumentException",
                "bad test",
                List.of(
                        new TraceNode("ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest",
                                "ExceptionStrackTraceSerializationTest.java", 25, "test", false),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                null, -2, "invoke0", true),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                "NativeMethodAccessorImpl.java", 62, "invoke", false)),
                null,
                List.of()
        ));

        String expected = "" +
                "java.lang.IllegalArgumentException: bad test\n" +
                "\tat ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest.test(ExceptionStrackTraceSerializationTest.java:25)\n" +
                "\tat jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)\n" +
                "\tat jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)";

        String actual = getActualThrowableText(crashValue);
        Assert.assertEquals(expected, actual);
    }

    @Test
    public void testHugeWithMessage() {
//        java.lang.Throwable cause2 = new IllegalStateException("cause 2");
//        cause2.addSuppressed(new IllegalArgumentException());
//
//        java.lang.Throwable cause = new java.sql.SQLException(cause2);
//
//        java.lang.Throwable exception = new IllegalArgumentException("bad test", cause);
//        exception.addSuppressed(new IllegalArgumentException("suppressed 1"));
//        exception.addSuppressed(new IllegalArgumentException("suppressed 2"));
//        exception.printStackTrace();

        Throwable cause2Suppressed = new Throwable(
                "java.lang.IllegalArgumentException",
                null,
                List.of(
                        new TraceNode("ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest",
                                "ExceptionStrackTraceSerializationTest.java", 82, "testHugeWithMessage", false),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                null, -2, "invoke0", true),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                "NativeMethodAccessorImpl.java", 62, "invoke", false)),
                null,
                List.of());

        Throwable cause2 = new Throwable(
                "java.lang.IllegalStateException",
                "cause 2",
                List.of(
                        new TraceNode("ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest",
                                "ExceptionStrackTraceSerializationTest.java", 81, "testHugeWithMessage", false),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                null, -2, "invoke0", true),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                "NativeMethodAccessorImpl.java", 62, "invoke", false)),
                null,
                List.of(cause2Suppressed));

        Throwable cause = new Throwable(
                "java.sql.SQLException",
                null,
                List.of(
                        new TraceNode("ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest",
                                "ExceptionStrackTraceSerializationTest.java", 85, "testHugeWithMessage", false),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                null, -2, "invoke0", true),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                "NativeMethodAccessorImpl.java", 62, "invoke", false)),
                cause2,
                List.of());

        Throwable suppressed1 = new Throwable(
                "java.lang.IllegalArgumentException",
                "suppressed 1",
                List.of(
                        new TraceNode("ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest",
                                "ExceptionStrackTraceSerializationTest.java", 87, "testHugeWithMessage", false),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                null, -2, "invoke0", true),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                "NativeMethodAccessorImpl.java", 62, "invoke", false)),
                null,
                List.of());

        Throwable suppressed2 = new Throwable(
                "java.lang.IllegalArgumentException",
                "suppressed 2",
                List.of(
                        new TraceNode("ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest",
                                "ExceptionStrackTraceSerializationTest.java", 88, "testHugeWithMessage", false),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                null, -2, "invoke0", true),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                "NativeMethodAccessorImpl.java", 62, "invoke", false)),
                null,
                List.of());

        AndroidCrashValue crashValue = exception(new Throwable(
                "java.lang.IllegalArgumentException",
                "bad test",
                List.of(
                        new TraceNode("ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest",
                                "ExceptionStrackTraceSerializationTest.java", 86, "testHugeWithMessage", false),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                null, -2, "invoke0", true),
                        new TraceNode("jdk.internal.reflect.NativeMethodAccessorImpl",
                                "NativeMethodAccessorImpl.java", 62, "invoke", false)),
                cause,
                List.of(suppressed1, suppressed2)));

        String expected = "" +
                "java.lang.IllegalArgumentException: bad test\n" +
                "\tat ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest.testHugeWithMessage(ExceptionStrackTraceSerializationTest.java:86)\n" +
                "\tat jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)\n" +
                "\tat jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)\n" +
                "\tSuppressed: java.lang.IllegalArgumentException: suppressed 1\n" +
                "\t\tat ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest.testHugeWithMessage(ExceptionStrackTraceSerializationTest.java:87)\n" +
                "\t\t... 2 more\n" +
                "\tSuppressed: java.lang.IllegalArgumentException: suppressed 2\n" +
                "\t\tat ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest.testHugeWithMessage(ExceptionStrackTraceSerializationTest.java:88)\n" +
                "\t\t... 2 more\n" +
                "Caused by: java.sql.SQLException\n" +
                "\tat ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest.testHugeWithMessage(ExceptionStrackTraceSerializationTest.java:85)\n" +
                "\t... 2 more\n" +
                "Caused by: java.lang.IllegalStateException: cause 2\n" +
                "\tat ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest.testHugeWithMessage(ExceptionStrackTraceSerializationTest.java:81)\n" +
                "\t... 2 more\n" +
                "\tSuppressed: java.lang.IllegalArgumentException\n" +
                "\t\tat ru.yandex.metrika.mobmet.crash.service.ExceptionStrackTraceSerializationTest.testHugeWithMessage(ExceptionStrackTraceSerializationTest.java:82)\n" +
                "\t\t... 2 more";

        String actual = getActualThrowableText(crashValue);
        Assert.assertEquals(expected, actual);
    }

    private String getActualThrowableText(AndroidCrashValue crashValue) {
        CrashValue rawCrashValue = mockRawCrashValue(null, AppEventType.EVENT_PROTOBUF_CRASH, "", OperatingSystem.ANDROID);

        StackTraceReport actual = stackTraceReportBuilder.buildStackTraceReport(crashValue, rawCrashValue);
        Assert.assertEquals(1, actual.getHeadUnits().size());
        StackTraceUnit unit = actual.getHeadUnits().get(0);
        return unit.getBody().getRawText();
    }

    private AndroidCrashValue exception(Throwable throwable) {
        return new AndroidCrashValue(throwable, new AllThreads(null, emptyList()), emptyList(), null, null);
    }
}
