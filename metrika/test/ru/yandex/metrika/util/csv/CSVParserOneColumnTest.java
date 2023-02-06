package ru.yandex.metrika.util.csv;

import java.io.ByteArrayInputStream;
import java.io.StringReader;
import java.nio.charset.StandardCharsets;
import java.util.Collection;
import java.util.List;

import com.google.common.collect.Lists;
import org.hamcrest.Matchers;
import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.notNullValue;

/**
 * @author zgmnkv
 */
public class CSVParserOneColumnTest {

    public static class CSVRow {

        private String value;

        public CSVRow(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    public static final String COLUMN = "Column";
    public static final String CHANGED_CASE_COLUMN = "cOlUmN";
    public static final String BAD_CHARS_COLUMN = " ![C o l u m n]! ";

    public static final List<CSVColumnDescriptor> COLUMN_DESCRIPTORS = List.of(new CSVColumnDescriptor(COLUMN));

    public static final CSVRowMapper<CSVRow> ROW_MAPPER = record -> new CSVRow(record.getString(COLUMN));

    private CSVParser<CSVRow> parser = new CSVParser<>(ROW_MAPPER, COLUMN_DESCRIPTORS);

    @Test
    public void testBasic() {
        List<CSVRow> rows = parse(COLUMN + "\nvalue");

        assertThat(rows, Matchers.<Collection<CSVRow>>allOf(
                hasSize(1),
                everyItem(hasProperty("value", equalTo("value")))
        ));
    }

    @Test
    public void testQuotedHeader() {
        List<CSVRow> rows = parse('"' + COLUMN + '"' + "\nvalue");

        assertThat(rows, Matchers.<Collection<CSVRow>>allOf(
                hasSize(1),
                everyItem(hasProperty("value", equalTo("value")))
        ));
    }

    @Test
    public void testQuotedValue() {
        List<CSVRow> rows = parse(COLUMN + "\n\"value\"");

        assertThat(rows, contains(hasProperty("value", equalTo("value"))));
    }

    @Test
    public void testQuoteInValue() {
        List<CSVRow> rows = parse(COLUMN + "\nval\"ue");

        assertThat(rows, contains(hasProperty("value", equalTo("val\"ue"))));
    }

    @Test
    public void testEscapedQuote() {
        List<CSVRow> rows = parse(COLUMN + "\n\"val\"\"ue\"");

        assertThat(rows, contains(hasProperty("value", equalTo("val\"ue"))));
    }

    @Test
    public void testChangedHeaderCase() {
        List<CSVRow> rows = parse(CHANGED_CASE_COLUMN + "\nvalue");

        assertThat(rows, contains(hasProperty("value", equalTo("value"))));
    }

    @Test
    public void testBadCharsInHeader() {
        List<CSVRow> rows = parse(BAD_CHARS_COLUMN + "\nvalue");

        assertThat(rows, contains(hasProperty("value", equalTo("value"))));
    }

    @Test
    public void testTrim() {
        List<CSVRow> rows = parse(COLUMN + "\n  value  ");

        assertThat(rows, contains(hasProperty("value", equalTo("value"))));
    }

    @Test
    public void testExtraColumnBefore() {
        List<CSVRow> rows = parse("ExtraColumn," + COLUMN + "\nvalue,value");

        assertThat(rows, contains(hasProperty("value", equalTo("value"))));
    }

    @Test
    public void testExtraColumnAfter() {
        List<CSVRow> rows = parse(COLUMN + ",ExtraColumn" + "\nvalue,value");

        assertThat(rows, contains(hasProperty("value", equalTo("value"))));
    }

    @Test
    public void testEmptyLines() {
        List<CSVRow> rows = parse(COLUMN + "\n\nvalue\n\nvalue\n\n");

        assertThat(rows, Matchers.<Collection<CSVRow>>allOf(
                hasSize(2),
                everyItem(hasProperty("value", equalTo("value")))
        ));
    }

    @Test
    public void testMissingColumn() {
        CSVParseException exception = null;
        try {
            parse("NotExistingColumn\nvalue");
        } catch (CSVParseException e) {
            exception = e;
        }

        assertThat(exception, notNullValue());
        assertThat(exception.getLineNumber(), equalTo(1L));
    }

    @Test
    public void testBadFormatInHeader() {
        CSVParseException exception = null;
        try {
            parse("\"" + COLUMN + "\nvalue");
        } catch (CSVParseException e) {
            exception = e;
        }

        assertThat(exception, notNullValue());
        assertThat(exception.getLineNumber(), equalTo(1L));
    }

    @Test
    public void testBadFormatInValue() {
        CSVParseException exception = null;
        try {
            parse(COLUMN + "\n\"valu\"e");
        } catch (CSVParseException e) {
            exception = e;
        }

        assertThat(exception, notNullValue());
        assertThat(exception.getLineNumber(), equalTo(2L));
    }

    @Test
    public void testEmptyCSV() {
        CSVParseException exception = null;
        try {
            parse("");
        } catch (CSVParseException e) {
            exception = e;
        }

        assertThat(exception, notNullValue());
        assertThat(exception.getLineNumber(), equalTo(1L));
    }

    @Test
    public void testDuplicatedColumn() {
        CSVParseException exception = null;
        try {
            parse("Column,Column");
        } catch (CSVParseException e) {
            exception = e;
        }

        assertThat(exception, notNullValue());
        assertThat(exception.getLineNumber(), equalTo(1L));
    }

    @Test
    public void testInputStream() {
        CSVParseResult<CSVRow> parseResult = parser.parse(new ByteArrayInputStream((COLUMN + "\nvalue").getBytes(StandardCharsets.UTF_8)));
        List<CSVRow> rows = Lists.newArrayList(parseResult.iterator());

        assertThat(rows, contains((hasProperty("value", equalTo("value")))));
    }

    private List<CSVRow> parse(String csv) {
        List<CSVRow> rows;
        try (CSVParseResult<CSVRow> parseResult = parser.parse(new StringReader(csv))) {
            rows = Lists.newArrayList(parseResult);
        }
        return rows;
    }
}
