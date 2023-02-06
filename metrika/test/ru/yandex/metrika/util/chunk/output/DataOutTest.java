package ru.yandex.metrika.util.chunk.output;

import java.io.ByteArrayOutputStream;

import org.jetbrains.annotations.NotNull;
import org.junit.Test;

import ru.yandex.metrika.util.PrimitiveBytes;
import ru.yandex.metrika.util.chunk.ChunkDescriptor;
import ru.yandex.metrika.util.chunk.ChunkRow;

/**
 * @author jkee
 */

public class DataOutTest {
    @Test
    public void testName() throws Exception {
        for (int i = 0; i < 255; i++) {
            for (int j = 0; j < 255; j++) {
                byte[] testBytes = new byte[4];
                //PrimitiveBytes.putInt(testBytes, 0);
                PrimitiveBytes.putShort(testBytes, 0, (short)22);
                testBytes[2] = (byte) (i);
                testBytes[3] = (byte) (j);
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                DataOut dataOut = new DataOut(baos);
                dataOut.out("ololo");
                dataOut.out(testBytes);
                dataOut.flush();
                byte[] bytes = baos.toByteArray();
                //System.out.println(bytes.length);  need assert ?

            }
        }

    }

    private static class TestInsert implements ChunkRow {
        private final byte[] bytes;

        private TestInsert(byte[] bytes) {
            this.bytes = bytes;
        }

        @Override
        public long getTime() {
            return 0;
        }

        @Override
        public ChunkDescriptor getInsertDescr() {
            return () -> new String[]{"bytes"};
        }

        @Override
        public void dumpFields(@NotNull CommandOutput output) {
            output.out(bytes);
        }
    }

}
