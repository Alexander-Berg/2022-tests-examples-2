package ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation;

import java.io.InputStream;

import com.android.tools.r8.naming.ClassNameMapper;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.decoder.service.android.model.AndroidEventProtobufWrapper;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.EXPECTED_ANR;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.EXPECTED_ERROR;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.EXPECTED_JVM_CRASH;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.OBFUSCATED_ANR;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.OBFUSCATED_ERROR;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.OBFUSCATED_JVM_CRASH;

public class R8DeobfuscatorTest {

    private R8Deobfuscator deobfuscator;

    @Before
    public void setUp() throws Exception {
        InputStream mappingFileIStream = this.getClass().getResourceAsStream("mapping.txt");
        ClassNameMapper classNameMapper = ClassNameMapper.mapperFromInputStream(mappingFileIStream);

        deobfuscator = new R8Deobfuscator(classNameMapper);
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
