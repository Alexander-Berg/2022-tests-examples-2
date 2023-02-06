package ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation;

import java.io.InputStream;
import java.util.Map;
import java.util.Set;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.decoder.service.android.model.AndroidEventProtobufWrapper;
import ru.yandex.metrika.mobmet.crash.deobfuscation.fork.FrameRemapper;
import ru.yandex.metrika.mobmet.crash.deobfuscation.fork.MappingReader;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.CrashMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.MethodMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ProguardMethodMapping;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.EXPECTED_ANR;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.EXPECTED_ERROR;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.EXPECTED_JVM_CRASH;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.OBFUSCATED_ANR;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.OBFUSCATED_ERROR;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.OBFUSCATED_JVM_CRASH;

public class ProguardDeobfuscatorTest {

    private ProguardDeobfuscator deobfuscator;

    @Before
    public void setUp() throws Exception {
        InputStream mappingFileIStream = this.getClass().getResourceAsStream("mapping.txt");
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
        AndroidEventProtobufWrapper actual = deobfuscator.decodeJvmEvent(OBFUSCATED_JVM_CRASH);
        assertEquals(EXPECTED_JVM_CRASH, actual);
    }

    @Test
    public void decodeError() {
        AndroidEventProtobufWrapper actual = deobfuscator.decodeJvmEvent(OBFUSCATED_ERROR);
        assertEquals(EXPECTED_ERROR, actual);
    }

    @Test
    public void decodeAnr() {
        AndroidEventProtobufWrapper actual = deobfuscator.decodeJvmEvent(OBFUSCATED_ANR);
        assertEquals(EXPECTED_ANR, actual);
    }
}
