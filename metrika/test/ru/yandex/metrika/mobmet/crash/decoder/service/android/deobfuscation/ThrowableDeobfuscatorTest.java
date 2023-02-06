package ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation;

import java.io.InputStream;
import java.util.Map;
import java.util.Set;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.decoder.android.proto.CrashAndroid;
import ru.yandex.metrika.mobmet.crash.deobfuscation.fork.FrameRemapper;
import ru.yandex.metrika.mobmet.crash.deobfuscation.fork.MappingReader;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.CrashMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.MethodMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ProguardMethodMapping;

import static java.util.Collections.singletonList;
import static org.junit.Assert.assertEquals;

public class ThrowableDeobfuscatorTest {

    private static final CrashAndroid.Throwable OBFUSCATED_THROWABLE = CrashAndroid.Throwable.newBuilder()
            .setExceptionClass("java.lang.RuntimeException")
            .setMessage("message")
            .addAllBacktrace(singletonList(CrashAndroid.StackTraceElement.newBuilder()
                    .setClassName("ru.yandex.research.b")
                    .setFileName("Unknown Source")
                    .setMethodName("close")
                    .setLineNumber(-1)
                    .setIsNative(false)
                    .build()))
            .addAllSuppressed(singletonList(CrashAndroid.Throwable.newBuilder()
                    .setExceptionClass("java.lang.RuntimeException")
                    .setMessage("MyFstClosable close")
                    .addAllBacktrace(singletonList(CrashAndroid.StackTraceElement.newBuilder()
                            .setClassName("ru.yandex.research.a")
                            .setFileName("Unknown Source")
                            .setMethodName("close")
                            .setLineNumber(-1)
                            .setIsNative(false)
                            .build()))
                    .build()))
            .build();
    private static final CrashAndroid.Throwable EXPECTED_THROWABLE = CrashAndroid.Throwable.newBuilder()
            .setExceptionClass("java.lang.RuntimeException")
            .setMessage("message")
            .addAllBacktrace(singletonList(CrashAndroid.StackTraceElement.newBuilder()
                    .setClassName("ru.yandex.research.TryWithResourceTest$MySndClosable")
                    .setFileName("TryWithResourceTest.java")
                    .setMethodName("close")
                    .setLineNumber(-1)
                    .setIsNative(false)
                    .build()))
            .addAllSuppressed(singletonList(CrashAndroid.Throwable.newBuilder()
                    .setExceptionClass("java.lang.RuntimeException")
                    .setMessage("MyFstClosable close")
                    .addAllBacktrace(singletonList(CrashAndroid.StackTraceElement.newBuilder()
                            .setClassName("ru.yandex.research.TryWithResourceTest$MyFstClosable")
                            .setFileName("TryWithResourceTest.java")
                            .setMethodName("close")
                            .setLineNumber(-1)
                            .setIsNative(false)
                            .build()))
                    .build()))
            .build();

    private ProguardDeobfuscator deobfuscator;


    @Before
    public void setUp() throws Exception {
        InputStream mappingFileIStream = this.getClass().getResourceAsStream("mapping_with_suppressed.txt");
        MappingReader mappingFileReader = new MappingReader(mappingFileIStream);
        FrameRemapper proguardRemapper = new FrameRemapper();
        mappingFileReader.pump(proguardRemapper);

        Map<String, Map<String, Set<ProguardMethodMapping>>> mappings =
                MethodMapping.convertMappings(proguardRemapper.getClassMethodMap(), ProguardMethodMapping::new);

        CrashMapping<ProguardMethodMapping> crashMapping = new CrashMapping<>(
                proguardRemapper.getClassMap(), mappings);

        deobfuscator = new ProguardDeobfuscator(crashMapping);
    }

    @Test
    public void decodeJvmCrash() {
        CrashAndroid.Throwable actual = deobfuscator.decodeThrowable(OBFUSCATED_THROWABLE);
        assertEquals(EXPECTED_THROWABLE, actual);
    }
}
