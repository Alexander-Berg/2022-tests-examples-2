package ru.yandex.metrika.cdp.frontend.csv;

import java.time.ZoneId;
import java.util.List;
import java.util.Map;
import java.util.Set;

import javax.annotation.Nonnull;

import com.google.common.collect.Iterables;
import org.junit.Before;
import org.junit.Test;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.multipart.MultipartFile;

import ru.yandex.metrika.api.InvalidUploadingException;
import ru.yandex.metrika.cdp.api.AbstractTest;
import ru.yandex.metrika.cdp.api.InMemoryAttributesProvider;
import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.dto.schema.EntityType;
import ru.yandex.metrika.cdp.frontend.csv.converter.StringSetPropertyConverter;
import ru.yandex.metrika.cdp.frontend.csv.converter.anysetter.AnySetterConvertorContextFactory;
import ru.yandex.metrika.cdp.frontend.csv.converter.anysetter.AttributesConversionContext;
import ru.yandex.metrika.cdp.frontend.data.CSVColumnNames;
import ru.yandex.metrika.cdp.frontend.data.DelimiterType;
import ru.yandex.metrika.cdp.frontend.rows.AbstractRowWithAttributes;
import ru.yandex.metrika.cdp.frontend.rows.RowProcessor;
import ru.yandex.metrika.util.dao.Convert;
import ru.yandex.metrika.util.io.IOUtils;

import static java.lang.String.format;
import static java.util.stream.Collectors.joining;
import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.util.collections.F.mapEntity;

public class CsvServiceTest extends AbstractTest {


    private final int counterId = 42;
    private final CsvService csvService = new CsvService();
    private final CSVMetadataGenerator<AttributesConversionContext> csvMetadataGenerator =
            CSVMetadataGenerator.customAnySetterGenerator(AttributesConversionContext.class);

    private final InMemoryAttributesProvider attributesProvider = new InMemoryAttributesProvider();
    private final EntityNamespace testNamespace = EntityType.CUSTOM_EVENT.getNamespace("test");  // для теста без разницы
    private final AnySetterConvertorContextFactory<AttributesConversionContext> factory =
            AttributesConversionContext.factory(attributesProvider, counterId, testNamespace);

    private final CSVClassMeta<TestRow, AttributesConversionContext> meta =
            CSVMetadataGenerator.customAnySetterGenerator(AttributesConversionContext.class).generateMeta(TestRow.class);

    private final RowProcessor<TestRow, TestRow> processor = x -> x;

    @Before
    public void setUp() {
        attributesProvider.clear();
    }

    /**
     * Простой тест который проверят что работает базовый кейс
     */
    @Test
    public void testCsvParsingBasic() {
        var file = getFile("basic.csv");
        var csvColumnNames = columnNames(Map.of(
                "first", "One",
                "second", "Two"
        ));

        var rows = parse(file, csvColumnNames);
        assertEquals(1, rows.size());

        var row = Iterables.getOnlyElement(rows);

        assertEquals("123", row.first);
        assertEquals((Integer) 321, row.second);
    }

    /**
     * Проверяем что эскейпинг запятой работает корректно
     */
    @Test
    public void testCsvParsingCommaEscaping() {
        var file = getFile("comma_escaping.csv");
        var csvColumnNames = columnNames(Map.of(
                "strings", "Строки",
                "a1", "Значения атрибута 1"
        ));

        addAttribute("a1", AttributeType.TEXT, true);

        var rows = parse(file, csvColumnNames);
        assertEquals(2, rows.size());

        var firstRow = rows.get(0);
        var secondRow = rows.get(1);

        assertEquals(Set.of("value1", "value2"), firstRow.strings);
        assertEquals(Set.of("value3,value4"), secondRow.strings);

        assertEquals(
                Map.of(
                        Attribute.unresolved("a1"), Set.of("aaa", "bbb")
                ),
                firstRow.getAttributeValues()
        );
        assertEquals(
                Map.of(
                        Attribute.unresolved("a1"), Set.of("ccc,ddd")
                ),
                secondRow.getAttributeValues()
        );
    }

    /**
     * Проверяем что не правильном эскейпинге парсинг падает с InvalidUploadingException
     */
    @Test(expected = InvalidUploadingException.class)
    public void testCsvParsingFailureOnWrongEscaping() {
        var file = getFile("wrong_escaping.csv");
        var csvColumnNames = columnNames(Map.of("strings", "Строки"));

        parse(file, csvColumnNames);
    }

    /**
     * Проверяем что мы правильно в зависимости от того
     * атрибут multivalued или нет сплитим его на отдельные строки по запятой или нет
     */
    @Test
    public void testCsvParsingAttrsWithComma() {
        var file = getFile("attrs_with_comma.csv");
        var csvColumnNames = columnNames(Map.of(
                "a1", "Attr1",
                "a2", "Attr2",
                "a3", "Attr3"
        ));

        addAttribute("a1", AttributeType.TEXT, false);
        addAttribute("a2", AttributeType.NUMERIC, true);
        addAttribute("a3", AttributeType.DATE, true);

        var rows = parse(file, csvColumnNames);
        assertEquals(1, rows.size());

        var row = Iterables.getOnlyElement(rows);

        assertEquals(
                Map.of(
                        Attribute.unresolved("a1"), Set.of("value1,value2"),
                        Attribute.unresolved("a2"), Set.of("111", "222"),
                        Attribute.unresolved("a3"), Set.of()
                ),
                row.getAttributeValues()
        );
    }

    @Nonnull
    private List<TestRow> parse(MultipartFile file, CSVColumnNames csvColumnNames) {
        return csvService.parseRows(csvColumnNames, DelimiterType.SEMICOLON, file, meta, processor, factory);
    }

    @Nonnull
    private static MultipartFile getFile(String name) {
        var example1Csv = IOUtils.resourceAsString(CsvServiceTest.class, "files/" + name);
        return new MockMultipartFile(name, example1Csv.getBytes());
    }

    private void addAttribute(String name, AttributeType attributeType, boolean multivalued) {
        attributesProvider.add(counterId, testNamespace, new Attribute(name, name, attributeType, multivalued));
    }


    public static final class TestRow extends AbstractRowWithAttributes<TestRow> {

        private String first;
        private Integer second;
        @Convert(StringSetPropertyConverter.class)
        private Set<String> strings;

        public TestRow() {
        }

        @Override
        protected TestRow asModelInternal(ZoneId timezone) {
            return this;
        }

        public String getFirst() {
            return first;
        }

        public void setFirst(String first) {
            this.first = first;
        }

        public Integer getSecond() {
            return second;
        }

        public void setSecond(Integer second) {
            this.second = second;
        }

        public Set<String> getStrings() {
            return strings;
        }

        public void setStrings(Set<String> strings) {
            this.strings = strings;
        }
    }

    private static CSVColumnNames columnNames(Map<String, String> map) {
        return new CSVColumnNames(map.entrySet().stream().map(mapEntity((k, v) -> format("\"%s\":\"%s\"", k, v))).collect(joining(",")));
    }
}
