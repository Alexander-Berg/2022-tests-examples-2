package ru.yandex.metrika.mobmet.crash.decoder.symbols.raw.impl;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.Map;
import java.util.Set;

import org.apache.commons.io.IOUtils;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.CrashMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.R8MethodMapping;

import static org.junit.Assert.assertEquals;

public class JavaMappingRawFileProcessorTest {

    /**
     * Проверяем, что мы правильно читаем r8 mappping.txt
     */
    @Test
    public void readAndCheckR8Mapping() throws IOException {
        ByteArrayInputStream r8MappingFile = new ByteArrayInputStream(IOUtils.toByteArray(
                this.getClass().getResourceAsStream("r8-mapping.txt")));
        CrashMapping<R8MethodMapping> crashMapping = JavaMappingRawFileProcessor.readAndCheckR8Mapping(r8MappingFile);

        Map<String, Set<R8MethodMapping>> methodMap =
                crashMapping.getClassMethodMap().get("com.bluelinelabs.conductor.Router");
        assertEquals(methodMap.size(), 65);
    }
}
