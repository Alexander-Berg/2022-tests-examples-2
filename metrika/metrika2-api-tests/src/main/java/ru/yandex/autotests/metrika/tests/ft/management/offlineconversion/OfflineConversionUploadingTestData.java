package ru.yandex.autotests.metrika.tests.ft.management.offlineconversion;

import java.math.BigInteger;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableMap;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;

import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionUploadingData;
import ru.yandex.autotests.metrika.tests.ft.management.conversion.CommonConversionUploadingTestData;
import ru.yandex.autotests.metrika.utils.CsvSerializer;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType;

import static com.google.common.collect.Collections2.filter;
import static com.google.common.collect.ImmutableList.of;
import static com.google.common.collect.Lists.newArrayList;
import static com.google.common.collect.Lists.transform;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_CLIENT_ID;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_CURRENCY;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_DATE_TIME;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_PRICE;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_TARGET;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_USER_ID;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_YCLID;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_CALL_MISSED;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_CALL_TRACKER_URL;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_FIRST_TIME_CALLER;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_HOLD_DURATION;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_PHONE_NUMBER;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_STATIC_CALL;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_TAG;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_TALK_DURATION;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData.COLUMN_URL;

public class OfflineConversionUploadingTestData {

    private static final String WHITESPACE_VALUE = " \t \r\n ";

    private static final Set<String> OPTIONAL_COLUMNS = new HashSet<>(of(COLUMN_PRICE, COLUMN_CURRENCY, COLUMN_PHONE_NUMBER, COLUMN_TALK_DURATION,
            COLUMN_HOLD_DURATION, COLUMN_CALL_MISSED, COLUMN_TAG, COLUMN_FIRST_TIME_CALLER, COLUMN_URL, COLUMN_CALL_TRACKER_URL, COLUMN_STATIC_CALL));

    private static final Set<String> NON_OPTIONAL_COLUMNS = new HashSet<>(of(COLUMN_USER_ID, COLUMN_CLIENT_ID, COLUMN_YCLID, COLUMN_TARGET, COLUMN_DATE_TIME));

    private static final Map<String, String> COLUMNS_WITH_NON_WORD_CHARS = ImmutableMap.<String, String>builder()
            .put(COLUMN_USER_ID, " UserId ")
            .put(COLUMN_CLIENT_ID, " ClientId ")
            .put(COLUMN_YCLID, " Yclid ")
            .put(COLUMN_DATE_TIME, "Date Time")
            .put(COLUMN_PRICE, "'Price'")
            .put(COLUMN_CURRENCY, "\"Currency\"")
            .put(COLUMN_TARGET, "[Target]")
            .put(COLUMN_PHONE_NUMBER, "!PhoneNumber")
            .put(COLUMN_TALK_DURATION, "TalkDuration?")
            .put(COLUMN_HOLD_DURATION, "`HoldDuration`")
            .put(COLUMN_CALL_MISSED, "Call Missed")
            .put(COLUMN_TAG, "{Tag}")
            .put(COLUMN_FIRST_TIME_CALLER, "(FirstTimeCaller)")
            .put(COLUMN_URL, "@URL")
            .put(COLUMN_CALL_TRACKER_URL, "*Call*Tracker*URL*")
            .put(COLUMN_STATIC_CALL, "Static Call")
            .build();

    private static final Map<String, String> VALUES = ImmutableMap.<String, String>builder()
            .put(COLUMN_USER_ID, "user@test.com")
            .put(COLUMN_CLIENT_ID, "133591247640966458")
            .put(COLUMN_YCLID, "123123123")
            .put(COLUMN_DATE_TIME, "1481718166")
            .put(COLUMN_PRICE, "123.45")
            .put(COLUMN_CURRENCY, "RUB")
            .put(COLUMN_TARGET, "GOAL1")
            .put(COLUMN_PHONE_NUMBER, "+71234567890")
            .put(COLUMN_TALK_DURATION, "136")
            .put(COLUMN_HOLD_DURATION, "23")
            .put(COLUMN_CALL_MISSED, "0")
            .put(COLUMN_TAG, "Tag")
            .put(COLUMN_FIRST_TIME_CALLER, "0")
            .put(COLUMN_URL, "https://test.com/")
            .put(COLUMN_CALL_TRACKER_URL, "https://test.com/")
            .put(COLUMN_STATIC_CALL, "0")
            .build();

    private static final Map<String, List<String>> SPECIAL_VALUES = ImmutableMap.<String, List<String>>builder()
            .put(COLUMN_DATE_TIME, of("1481718166.12345"))
            .put(COLUMN_TALK_DURATION, of("0", "4294967295"))
            .put(COLUMN_HOLD_DURATION, of("0", "4294967295"))
            .put(COLUMN_CALL_MISSED, of("1"))
            .put(COLUMN_FIRST_TIME_CALLER, of("1"))
            .put(COLUMN_STATIC_CALL, of("1"))
            .build();

    private static final Map<String, List<String>> INCORRECT_VALUES = ImmutableMap.<String, List<String>>builder()
            .put(COLUMN_CLIENT_ID, of("notNumber", "-133591247640966458"))
            .put(COLUMN_YCLID, of("notNumber", "asd"))
            .put(COLUMN_DATE_TIME, of("notNumber", "-1481718166", "2147483647"))
            .put(COLUMN_PRICE, of("notNumber"))
            .put(COLUMN_CURRENCY, of("notNumber"))
            .put(COLUMN_TALK_DURATION, of("notNumber", "-1", "4294967296"))
            .put(COLUMN_HOLD_DURATION, of("notNumber", "-1", "4294967296"))
            .put(COLUMN_CALL_MISSED, of("notNumber", "-1", "2"))
            .put(COLUMN_FIRST_TIME_CALLER, of("notNumber", "-1", "2"))
            .put(COLUMN_STATIC_CALL, of("notNumber", "-1", "2"))
            .build();

    private static CsvSerializer csvSerializer = new CsvSerializer();

    public static Object[] createBaseContent(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return CommonConversionUploadingTestData.createBaseContent(type.getColumns(clientIdType), VALUES);
    }

    public static Object[] createContentWithChangedHeaderCase(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return CommonConversionUploadingTestData.createContentWithChangedHeaderCase(type.getColumns(clientIdType), VALUES);
    }

    public static Object[] createContentWithNonWordCharsInHeader(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return CommonConversionUploadingTestData.createContentWithNonWordCharsInHeader(type.getColumns(clientIdType),
                COLUMNS_WITH_NON_WORD_CHARS, VALUES);
    }

    public static Object[] createContentWithShuffledColumns(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return CommonConversionUploadingTestData.createContentWithShuffledColumns(type.getColumns(clientIdType), VALUES);
    }

    public static Object[] createContentWithEmptyLines(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return CommonConversionUploadingTestData.createContentWithEmptyLines(type.getColumns(clientIdType), VALUES);
    }

    public static Object[] createContentWithUntrimmedValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return CommonConversionUploadingTestData.createContentWithUntrimmedValues(type.getColumns(clientIdType), VALUES);
    }

    public static Object[] createContentWithEmptyOptionalValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        List<String> columns = type.getColumns(clientIdType);
        return toArray("пустые значения в необязательных колонках", csvSerializer.serialize(of(
                columns,
                transform(columns, col -> OPTIONAL_COLUMNS.contains(col) ? "" : VALUES.get(col))
        )));
    }

    public static Object[] createContentWithWhitespaceOptionalValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        List<String> columns = type.getColumns(clientIdType);
        return toArray("пробельные значения в необязательных колонках", csvSerializer.serialize(of(
                columns,
                transform(columns, col -> OPTIONAL_COLUMNS.contains(col) ? WHITESPACE_VALUE : VALUES.get(col))
        )));
    }

    public static Object[] createContentWithoutOptionalColumns(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        List<String> columns = newArrayList(filter(type.getColumns(clientIdType), NON_OPTIONAL_COLUMNS::contains));
        return toArray("отсутствуют необязательные колонки", csvSerializer.serialize(of(
                columns,
                transform(columns, VALUES::get)
        )));
    }

    public static Object[] createContentWithAllValuesEmpty(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return CommonConversionUploadingTestData.createContentWithAllValuesEmpty(type.getColumns(clientIdType), VALUES);
    }

    public static Collection<Object[]> createContentWithEmptyNonOptionalValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return createContentWithEmptyNonOptionalValues(type, clientIdType, null);
    }

    public static Collection<Object[]> createContentWithWhitespaceNonOptionalValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return createContentWithWhitespaceNonOptionalValues(type, clientIdType, null);
    }

    public static Collection<Object[]> createContentWithSpecialValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return createContentWithSpecialValues(type, clientIdType, null);
    }

    public static Collection<Object[]> createContentWithIncorrectValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return createContentWithIncorrectValues(type, clientIdType, null);
    }

    public static Collection<Object[]> createContentWithEmptyNonOptionalValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType, Collection<String> includeColumns) {
        List<String> columns = type.getColumns(clientIdType);
        return NON_OPTIONAL_COLUMNS.stream()
                .filter(columns::contains)
                .filter(column -> includeColumns == null || includeColumns.contains(column))
                .map(col -> toArray("пустое значение в колонке " + col, csvSerializer.serialize(of(
                        columns,
                        transformSpecial(columns, VALUES::get, col, ""),
                        transform(columns, VALUES::get)
                ))))
                .collect(toList());
    }

    public static Collection<Object[]> createContentWithWhitespaceNonOptionalValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType, Collection<String> includeColumns) {
        List<String> columns = type.getColumns(clientIdType);
        return NON_OPTIONAL_COLUMNS.stream()
                .filter(columns::contains)
                .filter(column -> includeColumns == null || includeColumns.contains(column))
                .map(col -> toArray("пробельное значение в колонке " + col, csvSerializer.serialize(of(
                        columns,
                        transformSpecial(columns, VALUES::get, col, WHITESPACE_VALUE),
                        transform(columns, VALUES::get)
                ))))
                .collect(toList());
    }

    public static Collection<Object[]> createContentWithSpecialValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType, Collection<String> includeColumns) {
        List<String> columns = type.getColumns(clientIdType);
        return SPECIAL_VALUES.entrySet().stream()
                .filter(entry -> columns.contains(entry.getKey()))
                .filter(entry -> includeColumns == null || includeColumns.contains(entry.getKey()))
                .flatMap(entry -> streamWithIndex(entry.getValue()).map(idxValue -> toArray(
                        "особое значение в колонке " + entry.getKey() + " " + idxValue.getLeft(), csvSerializer.serialize(of(
                                columns,
                                transformSpecial(columns, VALUES::get, entry.getKey(), idxValue.getRight())
                        ))
                )))
                .collect(toList());
    }

    public static Collection<Object[]> createContentWithIncorrectValues(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType, Collection<String> includeColumns) {
        List<String> columns = type.getColumns(clientIdType);
        return INCORRECT_VALUES.entrySet().stream()
                .filter(entry -> columns.contains(entry.getKey()))
                .filter(entry -> includeColumns == null || includeColumns.contains(entry.getKey()))
                .flatMap(entry -> streamWithIndex(entry.getValue()).map(idxValue -> toArray(
                        "некорректное значение в колонке " + entry.getKey() + " " + idxValue.getLeft(), csvSerializer.serialize(of(
                                columns,
                                transformSpecial(columns, VALUES::get, entry.getKey(), idxValue.getRight()),
                                (NON_OPTIONAL_COLUMNS.contains(entry.getKey()) ? transform(columns, VALUES::get) : of())
                        ))
                )))
                .collect(toList());
    }

    public static Object[] createContentWithoutData(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return CommonConversionUploadingTestData.createContentWithoutData(type.getColumns(clientIdType));
    }

    public static Object[] createContentWithMalformedData(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return CommonConversionUploadingTestData.createContentWithMalformedData(type.getColumns(clientIdType));
    }

    public static Collection<Object[]> createContentWithoutNonOptionalColumns(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType) {
        return createContentWithoutNonOptionalColumns(type, clientIdType, null);
    }

    public static Collection<Object[]> createContentWithoutNonOptionalColumns(OfflineConversionType<?> type, OfflineConversionUploadingClientIdType clientIdType, Collection<String> includeColumns) {
        List<String> columns = type.getColumns(clientIdType);
        return NON_OPTIONAL_COLUMNS.stream()
                .filter(columns::contains)
                .filter(column -> includeColumns == null || includeColumns.contains(column))
                .map(col -> {
                    List<String> cols = newArrayList(filter(columns, c -> !col.equals(c)));
                    return toArray("отсутствует колонка " + col,  csvSerializer.serialize(of(
                            cols,
                            transform(cols, VALUES::get)
                    )));
                })
                .collect(toList());
    }

    private static <U, V> List<V> transformSpecial(List<U> source, Function<U, V> fn, U specialValue, V specialReplacement) {
        return transform(source, v -> specialValue.equals(v) ? specialReplacement : fn.apply(v));
    }

    private static <V> Stream<Pair<Integer, V>> streamWithIndex(List<V> list) {
        return IntStream.range(0, list.size()).mapToObj(idx -> ImmutablePair.of(idx, list.get(idx)));
    }



    public static <T extends OfflineConversionUploadingData> List<T> createBaseData(
            OfflineConversionType<T> type, OfflineConversionUploadingClientIdType clientIdType
    ) {
        return createBaseData2Rows(type, clientIdType);
    }

    public static <T extends OfflineConversionUploadingData> List<T> createBaseData1Row(
            OfflineConversionType<T> type, OfflineConversionUploadingClientIdType clientIdType
    ) {
        return of(createBaseDataItem1(type, clientIdType));
    }

    public static <T extends OfflineConversionUploadingData> List<T> createBaseData2Rows(
            OfflineConversionType<T> type, OfflineConversionUploadingClientIdType clientIdType
    ) {
        return of(createBaseDataItem1(type, clientIdType), createBaseDataItem2(type, clientIdType));
    }

    private static <T extends OfflineConversionUploadingData> T createBaseDataItem1(
            OfflineConversionType<T> type, OfflineConversionUploadingClientIdType clientIdType
    ) {
        T data = type.createData();

        data
                .withDateTime(1481718166L)
                .withPrice("123.45")
                .withCurrency("RUB");

        switch (clientIdType) {
            case USER_ID:
                data.withUserId("user@test.com");
                break;
            case CLIENT_ID:
                data.withClientId(new BigInteger("133591247640966458"));
                break;
            case YCLID:
                data.withYclid(new BigInteger("123123123"));
                break;
        }

        if (OfflineConversionType.BASIC.equals(type)) {
            ((BasicOfflineConversionUploadingData) data)
                    .withTarget("GOAL1");
        } else if (OfflineConversionType.CALLS.equals(type)) {
            ((CallsOfflineConversionUploadingData) data)
                    .withPhoneNumber("+71234567890")
                    .withTalkDuration(136L)
                    .withHoldDuration(23L)
                    .withCallMissed(0)
                    .withTag("Tag")
                    .withFirstTimeCaller(0)
                    .withUrl("https://test.com/")
                    .withCallTrackerUrl("https://test.com/");
        }

        return data;
    }

    private static <T extends OfflineConversionUploadingData> T createBaseDataItem2(
            OfflineConversionType<T> type, OfflineConversionUploadingClientIdType clientIdType
    ) {
        T data = type.createData();

        switch (clientIdType) {
            case USER_ID:
                data.withUserId("user2@test.com");
                break;
            case CLIENT_ID:
                data.withClientId(new BigInteger("174260678848581554"));
                break;
            case YCLID:
                data.withYclid(new BigInteger("234234234"));
                break;
        }

        data
                .withDateTime(1484493791L)
                .withPrice("678.90")
                .withCurrency("USD");

        if (OfflineConversionType.BASIC.equals(type)) {
            ((BasicOfflineConversionUploadingData) data)
                    .withTarget("GOAL2");
        } else if (OfflineConversionType.CALLS.equals(type)) {
            ((CallsOfflineConversionUploadingData) data)
                    .withPhoneNumber("+71230987654")
                    .withTalkDuration(0L)
                    .withHoldDuration(12L)
                    .withCallMissed(1)
                    .withFirstTimeCaller(1);
        }

        return data;
    }
}
