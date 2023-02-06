package ru.yandex.metrika.mobmet.crash.deobfuscation.mapping;

import java.io.IOException;

import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.SymbolsType;
import ru.yandex.metrika.mobmet.crash.SymbolsUploadMeta;
import ru.yandex.metrika.mobmet.crash.SymbolsUploadType;
import ru.yandex.metrika.mobmet.crash.symbols.SymbolsYdbTableType;
import ru.yandex.metrika.util.io.IOUtils;

import static org.assertj.core.api.Assertions.assertThat;

public class JavaMappingMetaParserTest {

    private final JavaMappingMetaParser parser = new JavaMappingMetaParser();

    @Test
    public void test() throws IOException {
        SymbolsUploadMeta rawSymbolsMeta = SymbolsUploadMeta.create(
                10L, 1111, SymbolsType.ANDROID_PROGUARD, 10, 0, SymbolsUploadType.UID, 10000L);
        String body = IOUtils.resourceAsString(JavaMappingMetaParserTest.class, "info.json");
        JavaMappingMeta actual = parser.parse(rawSymbolsMeta, body.getBytes());

        JavaMappingMeta expected = JavaMappingMeta.create(
                1111,
                "6e1f884b-c849-4287-8c93-38fde5a4d4cf",
                "2.0.0",
                10048,
                JavaMappingType.PROGUARD,
                SymbolsUploadType.UID,
                SymbolsYdbTableType.COMPRESSED);

        assertThat(actual).isEqualToComparingFieldByFieldRecursively(expected);
    }
}
