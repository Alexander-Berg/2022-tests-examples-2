package ru.yandex.autotests.metrika.tests.ft.management.conversion;

import org.apache.commons.lang.StringUtils;
import ru.yandex.autotests.metrika.utils.CsvSerializer;
import ru.yandex.autotests.metrika.utils.Utils;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Random;

import static com.google.common.collect.ImmutableList.of;
import static com.google.common.collect.Lists.newArrayList;
import static com.google.common.collect.Lists.transform;
import static org.apache.commons.lang3.ArrayUtils.toArray;

public class CommonConversionUploadingTestData {

    private static final long RANDOM_SEED = 360269957642241842L;

    private static CsvSerializer csvSerializer = new CsvSerializer();

    public static Object[] createBaseContent(List<String> columns, Map<String, String> values) {
        return createBaseContent(columns, values, "базовый");
    }

    public static Object[] createBaseContent(List<String> columns, Map<String, String> values, String title) {
        return toArray(title, csvSerializer.serialize(of(
                columns,
                transform(columns, values::get)
        )));
    }

    public static Object[] createContentWithChangedHeaderCase(List<String> columns, Map<String, String> values) {
        return toArray("измененный регистр заголовков", csvSerializer.serialize(of(
                transform(columns, Utils::invertCase),
                transform(columns, values::get)
        )));
    }

    public static Object[] createContentWithNonWordCharsInHeader(List<String> columns,
                                                                 Map<String, String> columnsWithNonWordChars,
                                                                 Map<String, String> values) {
        return toArray("заголовки с посторонними символами", csvSerializer.serialize(of(
                transform(columns, columnsWithNonWordChars::get),
                transform(columns, values::get)
        )));
    }

    public static Object[] createContentWithShuffledColumns(List<String> columns, Map<String, String> values) {
        List<String> shuffledColumns = newArrayList(columns);
        Collections.shuffle(shuffledColumns, new Random(RANDOM_SEED));

        return toArray("заголовки в другом порядке", csvSerializer.serialize(of(
                shuffledColumns,
                transform(shuffledColumns, values::get)
        )));
    }

    public static Object[] createContentWithEmptyLines(List<String> columns, Map<String, String> values) {
        return toArray("пустые строки", csvSerializer.serialize(of(
                columns,
                of(),
                of(),
                transform(columns, values::get),
                of(),
                of()
        )));
    }

    public static Object[] createContentWithUntrimmedValues(List<String> columns, Map<String, String> values) {
        return toArray("значения с пробелами по краям", csvSerializer.serialize(of(
                columns,
                transform(columns, col -> "\t" + values.get(col) + " ")
        )));
    }

    public static Object[] createContentWithAllValuesEmpty(List<String> columns, Map<String, String> values) {
        return toArray("пустые значения во всех колонках", csvSerializer.serialize(of(
                columns,
                Collections.nCopies(columns.size() - 1, ""),
                transform(columns, values::get)
        )));
    }

    public static Object[] createEmptyContent() {
        return toArray("пустая загрузка", StringUtils.EMPTY);
    }

    public static Object[] createContentWithMalformedHeader() {
        return toArray("некорректный формат заголовка", "\"tes\"t");
    }

    public static Object[] createContentWithoutData(List<String> columns) {
        return toArray("загрузка без данных", csvSerializer.serialize(of(
                columns
        )));
    }

    public static String[] createContentWithMalformedData(List<String> columns) {
        return toArray("некорректный формат данных", csvSerializer.serialize(of(columns)) + csvSerializer.getLineSeparator() + "\"tes\"t");
    }
}
