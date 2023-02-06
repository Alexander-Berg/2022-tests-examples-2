package ru.yandex.metrika.mobmet.crash.decoder.cloud.chunk.data;

import org.junit.Test;

public class CrashColumnsSerializersTest {

    @Test
    public void validate() {
        new CrashColumnsSerializers().validate();
    }
}
