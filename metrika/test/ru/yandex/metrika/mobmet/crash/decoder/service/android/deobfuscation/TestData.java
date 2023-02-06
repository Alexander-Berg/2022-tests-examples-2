package ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.List;
import java.util.UUID;

import com.google.common.io.Resources;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.tuple.Pair;

import ru.yandex.metrika.mobmet.crash.decoder.android.proto.CrashAndroid;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.model.AndroidAnrProtobufWrapper;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.model.AndroidCrashProtobufWrapper;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.model.AndroidErrorProtobufWrapper;

import static java.nio.charset.StandardCharsets.UTF_8;
import static java.util.Arrays.asList;
import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;

public class TestData {

    public static int APP_ID = 185600;

    public static final String BUILD_UUID = UUID.randomUUID().toString();

    public static final CrashAndroid.StackTraceElement OBFUSCATED_STACK_TRACE_ELEMENT_1 =
            CrashAndroid.StackTraceElement.newBuilder()
                    .setClassName("ru.yandex.taxi.controller.dd")
                    .setFileName("SourceFile")
                    .setLineNumber(1027)
                    .setMethodName("a")
                    .setIsNative(false)
                    .build();
    public static final CrashAndroid.StackTraceElement EXPECTED_STACK_TRACE_ELEMENT_1_1 =
            CrashAndroid.StackTraceElement.newBuilder()
                    .setClassName("ru.yandex.taxi.controller.OrderTitleFormatter_MembersInjector")
                    .setFileName("OrderTitleFormatter_MembersInjector.java")
                    .setLineNumber(27)
                    .setMethodName("injectMembers")
                    .setIsNative(false)
                    .build();
    public static final CrashAndroid.StackTraceElement EXPECTED_STACK_TRACE_ELEMENT_1_2 =
            CrashAndroid.StackTraceElement.newBuilder()
                    .setClassName("ru.yandex.taxi.controller.OrderTitleFormatter_MembersInjector")
                    .setFileName("OrderTitleFormatter_MembersInjector.java")
                    .setLineNumber(8)
                    .setMethodName("injectMembers")
                    .setIsNative(false)
                    .build();

    public static final CrashAndroid.StackTraceElement OBFUSCATED_STACK_TRACE_ELEMENT_2 =
            CrashAndroid.StackTraceElement.newBuilder()
                    .setClassName("ru.yandex.taxi.controller.db")
                    .setFileName("SourceFile")
                    .setLineNumber(18)
                    .setMethodName("<init>")
                    .setIsNative(false)
                    .build();
    public static final CrashAndroid.StackTraceElement EXPECTED_STACK_TRACE_ELEMENT_2 =
            CrashAndroid.StackTraceElement.newBuilder()
                    .setClassName("ru.yandex.taxi.controller.OrderTitleFormatter")
                    .setFileName("OrderTitleFormatter.java")
                    .setLineNumber(18)
                    .setMethodName("<init>")
                    .setIsNative(false)
                    .build();

    public static final CrashAndroid.Throwable OBFUSCATED_THROWABLE_1 = CrashAndroid.Throwable.newBuilder()
            .setExceptionClass("jp")
            .setMessage("Couldn't find component")
            .addAllBacktrace(asList(OBFUSCATED_STACK_TRACE_ELEMENT_1, OBFUSCATED_STACK_TRACE_ELEMENT_2))
            .build();
    public static final CrashAndroid.Throwable EXPECTED_THROWABLE_1 = CrashAndroid.Throwable.newBuilder()
            .setExceptionClass("com.bumptech.glide.Registry$MissingComponentException")
            .setMessage("Couldn't find component")
            .addAllBacktrace(asList(
                    EXPECTED_STACK_TRACE_ELEMENT_1_1,
                    EXPECTED_STACK_TRACE_ELEMENT_1_2,
                    EXPECTED_STACK_TRACE_ELEMENT_2))
            .build();

    public static final CrashAndroid.Throwable OBFUSCATED_THROWABLE_WITH_CAUSE = CrashAndroid.Throwable.newBuilder()
            .setExceptionClass("jq")
            .setMessage("Illegal header value")
            .setCause(OBFUSCATED_THROWABLE_1)
            .addAllBacktrace(singletonList(OBFUSCATED_STACK_TRACE_ELEMENT_2))
            .build();
    public static final CrashAndroid.Throwable EXPECTED_THROWABLE_WITH_CAUSE = CrashAndroid.Throwable.newBuilder()
            .setExceptionClass("com.bumptech.glide.Registry$NoImageHeaderParserException")
            .setMessage("Illegal header value")
            .addAllBacktrace(singletonList(EXPECTED_STACK_TRACE_ELEMENT_2))
            .setCause(EXPECTED_THROWABLE_1)
            .build();

    public static CrashAndroid.Thread OBFUSCATED_THREAD_1 = CrashAndroid.Thread.newBuilder()
            .setName("thread-pool-1")
            .setPriority(Thread.MAX_PRIORITY)
            .setTid(87635432)
            .setGroup("thread-group-1")
            .setState(Thread.State.WAITING.ordinal())
            .addAllStacktrace(asList(OBFUSCATED_STACK_TRACE_ELEMENT_1, OBFUSCATED_STACK_TRACE_ELEMENT_2))
            .build();
    public static CrashAndroid.Thread EXPECTED_THREAD_1 = CrashAndroid.Thread.newBuilder()
            .setName("thread-pool-1")
            .setPriority(Thread.MAX_PRIORITY)
            .setTid(87635432)
            .setGroup("thread-group-1")
            .setState(Thread.State.WAITING.ordinal())
            .addAllStacktrace(asList(
                    EXPECTED_STACK_TRACE_ELEMENT_1_1,
                    EXPECTED_STACK_TRACE_ELEMENT_1_2, EXPECTED_STACK_TRACE_ELEMENT_2))
            .build();

    public static CrashAndroid.Thread OBFUSCATED_THREAD_2 = CrashAndroid.Thread.newBuilder()
            .setName("thread-pool-2")
            .setPriority(Thread.MIN_PRIORITY)
            .setTid(234635432)
            .setGroup("thread-group-2")
            .setState(Thread.State.RUNNABLE.ordinal())
            .addAllStacktrace(singletonList(OBFUSCATED_STACK_TRACE_ELEMENT_1))
            .build();
    public static CrashAndroid.Thread EXPECTED_THREAD_2 = CrashAndroid.Thread.newBuilder()
            .setName("thread-pool-2")
            .setPriority(Thread.MIN_PRIORITY)
            .setTid(234635432)
            .setGroup("thread-group-2")
            .setState(Thread.State.RUNNABLE.ordinal())
            .addAllStacktrace(asList(EXPECTED_STACK_TRACE_ELEMENT_1_1, EXPECTED_STACK_TRACE_ELEMENT_1_2))
            .build();


    public static final CrashAndroid.AllThreads OBFUSCATED_ALL_THREADS = CrashAndroid.AllThreads.newBuilder()
            .setAffectedThread(OBFUSCATED_THREAD_1)
            .addAllThreads(asList(OBFUSCATED_THREAD_1, OBFUSCATED_THREAD_2))
            .build();
    public static final CrashAndroid.AllThreads EXPECTED_ALL_THREADS = CrashAndroid.AllThreads.newBuilder()
            .setAffectedThread(EXPECTED_THREAD_1)
            .addAllThreads(asList(EXPECTED_THREAD_1, EXPECTED_THREAD_2))
            .build();

    public static final String VIRTUAL_MACHINE = "JVM";
    public static final String VIRTUAL_MACHINE_VERSION = null;
    public static final List<Pair<String, String>> PLUGIN_ENVIRONMENT = emptyList();

    public static final String ERROR_MESSAGE = RandomStringUtils.randomAlphanumeric(20);

    public final static AndroidCrashProtobufWrapper OBFUSCATED_JVM_CRASH = new AndroidCrashProtobufWrapper(
            BUILD_UUID,
            OBFUSCATED_THROWABLE_WITH_CAUSE,
            OBFUSCATED_ALL_THREADS,
            VIRTUAL_MACHINE,
            VIRTUAL_MACHINE_VERSION,
            PLUGIN_ENVIRONMENT);

    public final static AndroidCrashProtobufWrapper EXPECTED_JVM_CRASH = new AndroidCrashProtobufWrapper(
            BUILD_UUID,
            EXPECTED_THROWABLE_WITH_CAUSE,
            EXPECTED_ALL_THREADS,
            VIRTUAL_MACHINE,
            VIRTUAL_MACHINE_VERSION,
            PLUGIN_ENVIRONMENT);

    public final static AndroidErrorProtobufWrapper OBFUSCATED_ERROR = new AndroidErrorProtobufWrapper(
            BUILD_UUID,
            null,
            ERROR_MESSAGE,
            OBFUSCATED_THROWABLE_WITH_CAUSE,
            List.of(
                    OBFUSCATED_STACK_TRACE_ELEMENT_1,
                    OBFUSCATED_STACK_TRACE_ELEMENT_2
            ),
            VIRTUAL_MACHINE,
            VIRTUAL_MACHINE_VERSION,
            PLUGIN_ENVIRONMENT);

    public final static AndroidErrorProtobufWrapper EXPECTED_ERROR = new AndroidErrorProtobufWrapper(
            BUILD_UUID,
            null,
            ERROR_MESSAGE,
            EXPECTED_THROWABLE_WITH_CAUSE,
            List.of(
                    EXPECTED_STACK_TRACE_ELEMENT_1_1,
                    EXPECTED_STACK_TRACE_ELEMENT_1_2,
                    EXPECTED_STACK_TRACE_ELEMENT_2
            ),
            VIRTUAL_MACHINE,
            VIRTUAL_MACHINE_VERSION,
            PLUGIN_ENVIRONMENT);

    public final static AndroidAnrProtobufWrapper OBFUSCATED_ANR = new AndroidAnrProtobufWrapper(
            BUILD_UUID,
            OBFUSCATED_ALL_THREADS
    );

    public final static AndroidAnrProtobufWrapper EXPECTED_ANR = new AndroidAnrProtobufWrapper(
            BUILD_UUID,
            EXPECTED_ALL_THREADS
    );

    public static String getExpectedStackTraceAsText() {
        try {
            //noinspection UnstableApiUsage
            return Resources.toString(
                    JavaDecodeServiceTest.class.getResource("expected_affected_thread_content.txt"), UTF_8);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
