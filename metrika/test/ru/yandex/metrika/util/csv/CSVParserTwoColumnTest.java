package ru.yandex.metrika.util.csv;

import java.io.StringReader;
import java.util.Collection;
import java.util.List;

import com.google.common.collect.Lists;
import org.hamcrest.Matchers;
import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.nullValue;

/**
 * @author zgmnkv
 */
public class CSVParserTwoColumnTest {

    public static class CSVRow {

        private String value;
        private String optionalValue;

        public CSVRow(String value, String optionalValue) {
            this.value = value;
            this.optionalValue = optionalValue;
        }

        public String getValue() {
            return value;
        }

        public String getOptionalValue() {
            return optionalValue;
        }
    }

    public static final String COLUMN = "Column";
    public static final String OPTIONAL_COLUMN = "OptionalColumn";

    public static final List<CSVColumnDescriptor> COLUMN_DESCRIPTORS =
            List.of(new CSVColumnDescriptor(COLUMN), new CSVColumnDescriptor(OPTIONAL_COLUMN, true));

    public static final CSVRowMapper<CSVRow> ROW_MAPPER = record ->
            new CSVRow(record.getString(COLUMN), record.getStringOptional(OPTIONAL_COLUMN).orElse(null));

    private CSVParser<CSVRow> parser = new CSVParser<>(ROW_MAPPER, COLUMN_DESCRIPTORS);

    @Test
    public void testBasic() {
        List<CSVRow> rows = parse(COLUMN + ',' + OPTIONAL_COLUMN + "\nvalue,optionalValue");

        assertThat(rows, Matchers.<Collection<CSVRow>>allOf(
                hasSize(1),
                everyItem(allOf(
                        hasProperty("value", equalTo("value")),
                        hasProperty("optionalValue", equalTo("optionalValue"))
                ))
        ));
    }

    @Test
    public void testWithoutOptionalColumn() {
        List<CSVRow> rows = parse(COLUMN + "\nvalue");

        assertThat(rows, Matchers.<Collection<CSVRow>>allOf(
                hasSize(1),
                everyItem(allOf(
                        hasProperty("value", equalTo("value")),
                        hasProperty("optionalValue", nullValue())
                ))
        ));
    }

    @Test
    public void testExtraColumnInBetween() {
        List<CSVRow> rows = parse(COLUMN + ",ExtraColumn," + OPTIONAL_COLUMN + "\nvalue,extraValue,optionalValue");

        assertThat(rows, Matchers.<Collection<CSVRow>>allOf(
                hasSize(1),
                everyItem(allOf(
                        hasProperty("value", equalTo("value")),
                        hasProperty("optionalValue", equalTo("optionalValue"))
                ))
        ));
    }

    @Test
    public void testShuffledColumns() {
        List<CSVRow> rows = parse(OPTIONAL_COLUMN + ',' + COLUMN + "\noptionalValue,value");

        assertThat(rows, Matchers.<Collection<CSVRow>>allOf(
                hasSize(1),
                everyItem(allOf(
                        hasProperty("value", equalTo("value")),
                        hasProperty("optionalValue", equalTo("optionalValue"))
                ))
        ));
    }

    private List<CSVRow> parse(String csv) {
        List<CSVRow> rows;
        try (CSVParseResult<CSVRow> parseResult = parser.parse(new StringReader(csv))) {
            rows = Lists.newArrayList(parseResult);
        }
        return rows;
    }
}
