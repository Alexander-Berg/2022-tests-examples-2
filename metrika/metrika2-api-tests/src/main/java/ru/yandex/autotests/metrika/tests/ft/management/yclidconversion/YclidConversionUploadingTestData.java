package ru.yandex.autotests.metrika.tests.ft.management.yclidconversion;

import com.google.common.collect.ImmutableMap;
import ru.yandex.autotests.metrika.data.management.v1.yclidconversion.YclidConversionUploadingData;
import ru.yandex.autotests.metrika.tests.ft.management.conversion.CommonConversionUploadingTestData;

import java.util.List;
import java.util.Map;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData.COLUMN_TARGET;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionUploadingData.*;
import static ru.yandex.autotests.metrika.data.management.v1.yclidconversion.YclidConversionUploadingData.COLUMN_YCLID;

public class YclidConversionUploadingTestData {

    private static final List<String> COLUMNS = of(COLUMN_PRICE, COLUMN_CURRENCY, COLUMN_YCLID, COLUMN_TARGET, COLUMN_DATE_TIME);

    private static final Map<String, String> COLUMNS_WITH_NON_WORD_CHARS = ImmutableMap.<String, String>builder()
            .put(COLUMN_YCLID, " Yclid ")
            .put(COLUMN_DATE_TIME, "Date Time")
            .put(COLUMN_PRICE, "'Price'")
            .put(COLUMN_CURRENCY, "\"Currency\"")
            .put(COLUMN_TARGET, "[Target]")
            .build();

    private static final Map<String, String> VALUES = ImmutableMap.<String, String>builder()
            .put(COLUMN_YCLID, "123456")
            .put(COLUMN_TARGET, "GOAL1")
            .put(COLUMN_DATE_TIME, "1481718166")
            .put(COLUMN_PRICE, "123.45")
            .put(COLUMN_CURRENCY, "RUB")
            .build();

    private static final Map<String, String> VALUES_WITH_UNSIGNED_LONG = ImmutableMap.<String, String>builder()
            .put(COLUMN_YCLID, "18115295755433708648")
            .put(COLUMN_TARGET, "GOAL1")
            .put(COLUMN_DATE_TIME, "1481718166")
            .put(COLUMN_PRICE, "123.45")
            .put(COLUMN_CURRENCY, "RUB")
            .build();

    public static Object[] createBaseContent() {
        return CommonConversionUploadingTestData.createBaseContent(COLUMNS, VALUES);
    }

    public static List<YclidConversionUploadingData> createBaseData1Row() {
        return of(createBaseDataItem1());
    }

    public static List<YclidConversionUploadingData> createBaseData2Rows(
    ) {
        return of(createBaseDataItem1(), createBaseDataItem2());
    }

    public static Object[] createContentWithChangedHeaderCase() {
        return CommonConversionUploadingTestData.createContentWithChangedHeaderCase(COLUMNS, VALUES);
    }

    public static Object[] createContentWithNonWordCharsInHeader() {
        return CommonConversionUploadingTestData.createContentWithNonWordCharsInHeader(COLUMNS, COLUMNS_WITH_NON_WORD_CHARS,
                VALUES);
    }

    public static Object[] createContentWithShuffledColumns() {
        return CommonConversionUploadingTestData.createContentWithShuffledColumns(COLUMNS, VALUES);
    }

    public static Object[] createContentWithEmptyLines() {
        return CommonConversionUploadingTestData.createContentWithEmptyLines(COLUMNS, VALUES);
    }

    public static Object[] createContentWithUntrimmedValues() {
        return CommonConversionUploadingTestData.createContentWithUntrimmedValues(COLUMNS, VALUES);
    }

    public static Object[] createContentWithAllValuesEmpty() {
        return CommonConversionUploadingTestData.createContentWithAllValuesEmpty(COLUMNS, VALUES);
    }

    public static Object[] createContentWithoutData() {
        return CommonConversionUploadingTestData.createContentWithoutData(COLUMNS);
    }

    public static Object[] createContentWithMalformedData() {
        return CommonConversionUploadingTestData.createContentWithMalformedData(COLUMNS);
    }

    public static Object[] createContentWithULongYclid() {
        return CommonConversionUploadingTestData.createBaseContent(COLUMNS, VALUES_WITH_UNSIGNED_LONG,
                "yclid больше чем 2^63");
    }

    private static YclidConversionUploadingData createBaseDataItem1() {
        return new YclidConversionUploadingData()
                .withYclid("123456")
                .withDateTime(1481718166L)
                .withPrice("123.45")
                .withCurrency("RUB")
                .withTarget("GOAL1");
    }

    private static YclidConversionUploadingData createBaseDataItem2() {
        return new YclidConversionUploadingData()
                .withYclid("987654")
                .withDateTime(1484493791L)
                .withPrice("678.90")
                .withCurrency("USD")
                .withTarget("GOAL2");
    }
}
