package ru.yandex.metrika.util.csv;

import java.io.StringReader;
import java.math.BigDecimal;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import com.google.common.collect.Lists;
import org.apache.commons.lang3.tuple.ImmutableTriple;
import org.apache.commons.lang3.tuple.Triple;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.iterableWithSize;

@RunWith(Parameterized.class)
public class CSVParseBigDecimalTest {
    @FunctionalInterface
    public interface CSVRecordGetter<T> {

        T get(CSVRecord record, String columnName, char delimiter) throws CSVRecordInvalidException;
    }

    public static class CSVRow<T> {

        private T value;

        public CSVRow(T value) {
            this.value = value;
        }

        public T getValue() {
            return value;
        }

        public void setValue(T value) {
            this.value = value;
        }
    }

    public static final String COLUMN_NAME = "Column";

    public static final CSVRecordGetter<?> RECORD_GETTER = CSVRecord::getBigDecimal;

    public static final List<Triple<String, Character, BigDecimal>> GOOD_VALUES = of(
            ImmutableTriple.of("6412666197747905834.5450876286673937145", '.', new BigDecimal("6412666197747905834.5450876286673937145")),
            ImmutableTriple.of("0", '.', BigDecimal.ZERO),
            ImmutableTriple.of("1,234.567", '.', new BigDecimal("1234.567")),
            ImmutableTriple.of("1234,567", ',', new BigDecimal("1234.567")),
            ImmutableTriple.of("1.234,567", ',', new BigDecimal("1234.567"))
    );

    @Parameterized.Parameters(name = "{0}, csvValue {2}, decimalDelimiter {3}, expectedValue {4}")
    public static Collection<Object[]> initParams() {
        return GOOD_VALUES.stream().map(value ->
                new Object[]{"test BigDecimal parse with delimiter", RECORD_GETTER, value.getLeft(), value.getMiddle(), value.getRight()}
        ).collect(Collectors.toList());
    }

    @Parameterized.Parameter
    public String name;

    @Parameterized.Parameter(1)
    public CSVRecordGetter recordGetter;

    @Parameterized.Parameter(2)
    public String csvValue;

    @Parameterized.Parameter(3)
    public char decimalDelimiter;

    @Parameterized.Parameter(4)
    public Object expectedValue;

    @Test
    public void test() {
        CSVRowMapper<CSVRow> mapper = record -> new CSVRow<>(recordGetter.get(record, COLUMN_NAME, decimalDelimiter));
        CSVParser<CSVRow> parser = new CSVParser<>(mapper, List.of(new CSVColumnDescriptor(COLUMN_NAME)), true, true,
                CSVParser.DEFAULT_FORMAT.withDelimiter(';'),
                CSVParser.NORMALIZE_HEADER_NAME_PREPROCESSOR
        );

        List<CSVRow> rows;
        try (CSVParseResult<CSVRow> parseResult = parser.parse(new StringReader(COLUMN_NAME + '\n' + csvValue + ';'))) {
            rows = Lists.newArrayList(parseResult);
        }


        assertThat(rows, allOf(
                iterableWithSize(1),
                contains(hasProperty("value", equalTo(expectedValue)))
        ));

    }
}
