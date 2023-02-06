package ru.yandex.metrika.util.csv;

import java.io.StringReader;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Lists;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.emptyIterable;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.metrika.util.csv.CSVParserTypesTest.CSVRecordGetter.fromOptional;

/**
 * @author zgmnkv
 */
@RunWith(Parameterized.class)
public class CSVParserTypesTest {

    @FunctionalInterface
    public interface CSVRecordGetter<T> {

        T get(CSVRecord record, String columnName) throws CSVRecordInvalidException;

        static <T> CSVRecordGetter<T> fromOptional(CSVRecordGetter<Optional<? extends T>> optionalGetter) {
            return (record, columnName) -> optionalGetter.get(record, columnName).orElse(null);
        }
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

    public static final int TYPES_AMOUNT = 14;
    public static final String COLUMN_NAME = "Column";
    public static final String BAD_NUMBER_VALUE = "qwe";
    public static final String WHITESPACE_VALUE = " \t ";

    public static final List<CSVRecordGetter<?>> RECORD_GETTERS = new ImmutableList.Builder<CSVRecordGetter<?>>()
            .add(CSVRecord::getString)
            .add(CSVRecord::getBoolean)
            .add(CSVRecord::getByte)
            .add(CSVRecord::getUByte)
            .add(CSVRecord::getShort)
            .add(CSVRecord::getUShort)
            .add(CSVRecord::getInt)
            .add(CSVRecord::getUInt)
            .add(CSVRecord::getLong)
            .add(CSVRecord::getULong)
            .add(CSVRecord::getFloat)
            .add(CSVRecord::getDouble)
            .add(CSVRecord::getBigInteger)
            .add(CSVRecord::getBigDecimal)
            .build();

    public static final List<CSVRecordGetter<Optional<?>>> RECORD_OPTIONAL_GETTERS = new ImmutableList.Builder<CSVRecordGetter<Optional<?>>>()
            .add(CSVRecord::getStringOptional)
            .add(CSVRecord::getBooleanOptional)
            .add(CSVRecord::getByteOptional)
            .add(CSVRecord::getUByteOptional)
            .add(CSVRecord::getShortOptional)
            .add(CSVRecord::getUShortOptional)
            .add(CSVRecord::getIntOptional)
            .add(CSVRecord::getUIntOptional)
            .add(CSVRecord::getLongOptional)
            .add(CSVRecord::getULongOptional)
            .add(CSVRecord::getFloatOptional)
            .add(CSVRecord::getDoubleOptional)
            .add(CSVRecord::getBigIntegerOptional)
            .add(CSVRecord::getBigDecimalOptional)
            .build();

    public static final List<List<Pair<String, Object>>> GOOD_VALUES = new ImmutableList.Builder<List<Pair<String, Object>>>()
            .add(of(ImmutablePair.of("9a08a9f7-fe0f-4ab4-86e6-d45474af14a4", "9a08a9f7-fe0f-4ab4-86e6-d45474af14a4")))
            .add(of(
                    ImmutablePair.of("true", true),
                    ImmutablePair.of("false", false)
            ))
            .add(of(
                    ImmutablePair.of("-14", (byte) -14),
                    ImmutablePair.of("-128", (byte) -128),
                    ImmutablePair.of("127", (byte) 127)
            ))
            .add(of(
                    ImmutablePair.of("233", (byte) 233),
                    ImmutablePair.of("0", (byte) 0),
                    ImmutablePair.of("255", (byte) 255)
            ))
            .add(of(
                    ImmutablePair.of("-9955", (short) -9955),
                    ImmutablePair.of("-32768", (short) -32768),
                    ImmutablePair.of("32767", (short) 32767)
            ))
            .add(of(
                    ImmutablePair.of("46471", (short) 46471),
                    ImmutablePair.of("0", (short) 0),
                    ImmutablePair.of("65535", (short) 65535)
            ))
            .add(of(
                    ImmutablePair.of("-1868697905", -1868697905),
                    ImmutablePair.of("-2147483648", -2147483648),
                    ImmutablePair.of("2147483647", 2147483647)
            ))
            .add(of(
                    ImmutablePair.of("1638516947", Integer.parseUnsignedInt("1638516947")),
                    ImmutablePair.of("0", 0),
                    ImmutablePair.of("4294967295", Integer.parseUnsignedInt("4294967295"))
            ))
            .add(of(
                    ImmutablePair.of("3637928646297218323", 3637928646297218323L),
                    ImmutablePair.of("-9223372036854775808", -9223372036854775808L),
                    ImmutablePair.of("9223372036854775807", 9223372036854775807L)
            ))
            .add(of(
                    ImmutablePair.of("9482205575896593864", Long.parseUnsignedLong("9482205575896593864")),
                    ImmutablePair.of("0", 0L),
                    ImmutablePair.of("18446744073709551615", Long.parseUnsignedLong("18446744073709551615"))
            ))
            .add(of(
                    ImmutablePair.of("0.9264974", 0.9264974F),
                    ImmutablePair.of("-0.9264974", -0.9264974F)
            ))
            .add(of(
                    ImmutablePair.of("0.3655903191097476", 0.3655903191097476),
                    ImmutablePair.of("-0.3655903191097476", -0.3655903191097476)))
            .add(of(
                    ImmutablePair.of("-47381365601637697061160307725180139377", new BigInteger("-47381365601637697061160307725180139377")),
                    ImmutablePair.of("0", BigInteger.ZERO)
            ))
            .add(of(
                    ImmutablePair.of("6412666197747905834.5450876286673937145", new BigDecimal("6412666197747905834.5450876286673937145")),
                    ImmutablePair.of("0", BigDecimal.ZERO)
            ))
            .build();

    public static final List<List<String>> BAD_VALUES = new ImmutableList.Builder<List<String>>()
            .add(of())
            .add(of())
            .add(of(BAD_NUMBER_VALUE, "-129", "128"))
            .add(of(BAD_NUMBER_VALUE, "-1", "256"))
            .add(of(BAD_NUMBER_VALUE, "-32769", "32768"))
            .add(of(BAD_NUMBER_VALUE, "-1", "65536"))
            .add(of(BAD_NUMBER_VALUE, "-2147483649", "2147483648"))
            .add(of(BAD_NUMBER_VALUE, "-1", "4294967296"))
            .add(of(BAD_NUMBER_VALUE, "-9223372036854775809", "9223372036854775808"))
            .add(of(BAD_NUMBER_VALUE, "-1", "18446744073709551616"))
            .add(of(BAD_NUMBER_VALUE))
            .add(of(BAD_NUMBER_VALUE))
            .add(of(BAD_NUMBER_VALUE, "0.1"))
            .add(of(BAD_NUMBER_VALUE))
            .build();

    @Parameterized.Parameters(name = "{0}, csvValue {2}, expectedValue {3}, expectEmpty {4}")
    public static Collection<Object[]> initParams() {
        return new ImmutableList.Builder<Object[]>()
                .addAll(IntStream.range(0, TYPES_AMOUNT).boxed()
                        .flatMap(i -> GOOD_VALUES.get(i).stream().flatMap(value -> Stream.of(
                                new Object[] { "goodValue" + i, RECORD_GETTERS.get(i), value.getLeft(), value.getRight(), false },
                                new Object[] { "goodValueOptional" + i, fromOptional(RECORD_OPTIONAL_GETTERS.get(i)), value.getLeft(), value.getRight(), false }
                        ))).collect(Collectors.toList())
                )
                .addAll(IntStream.range(0, TYPES_AMOUNT).boxed()
                        .flatMap(i -> BAD_VALUES.get(i).stream().flatMap(value -> Stream.of(
                                new Object[] { "badValue" + i, RECORD_GETTERS.get(i), value, null, true },
                                new Object[] { "badValueOptional" + i, fromOptional(RECORD_OPTIONAL_GETTERS.get(i)), value, null, false }
                        ))).collect(Collectors.toList())
                )
                .addAll(IntStream.range(0, TYPES_AMOUNT).boxed().flatMap(i -> Stream.of(
                        new Object[] { "emptyValue" + i, RECORD_GETTERS.get(i), StringUtils.EMPTY, null, true },
                        new Object[] { "whitespaceValue" + i, RECORD_GETTERS.get(i), WHITESPACE_VALUE, null, true },
                        new Object[] { "emptyValueOptional" + i, fromOptional(RECORD_OPTIONAL_GETTERS.get(i)), StringUtils.EMPTY, null, false },
                        new Object[] { "whitespaceValueOptional" + i, fromOptional(RECORD_OPTIONAL_GETTERS.get(i)), WHITESPACE_VALUE, null, false }
                )).collect(Collectors.toList()))
                .build();
    }

    @Parameterized.Parameter
    public String name;

    @Parameterized.Parameter(1)
    public CSVRecordGetter recordGetter;

    @Parameterized.Parameter(2)
    public String csvValue;

    @Parameterized.Parameter(3)
    public Object expectedValue;

    @Parameterized.Parameter(4)
    public boolean expectEmpty;

    @Test
    public void test() {
        CSVRowMapper<CSVRow> mapper = record -> new CSVRow<>(recordGetter.get(record, COLUMN_NAME));
        CSVParser<CSVRow> parser = new CSVParser<>(mapper, List.of(new CSVColumnDescriptor(COLUMN_NAME)));

        List<CSVRow> rows;
        try (CSVParseResult<CSVRow> parseResult = parser.parse(new StringReader(COLUMN_NAME + '\n' + csvValue + ','))) {
            rows = Lists.newArrayList(parseResult);
        }

        if (expectEmpty) {
            assertThat(rows, emptyIterable());
        } else {
            assertThat(rows, allOf(
                    iterableWithSize(1),
                    contains(hasProperty("value", equalTo(expectedValue)))
            ));
        }
    }
}
