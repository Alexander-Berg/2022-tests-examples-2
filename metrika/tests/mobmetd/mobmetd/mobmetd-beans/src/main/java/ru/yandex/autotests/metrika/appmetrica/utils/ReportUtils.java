package ru.yandex.autotests.metrika.appmetrica.utils;

import org.apache.commons.lang3.StringUtils;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataGETSchema;
import ru.yandex.metrika.api.constructor.response.DrillDownRow;
import ru.yandex.metrika.api.constructor.response.DynamicRow;
import ru.yandex.metrika.api.constructor.response.StaticRow;
import ru.yandex.metrika.spring.profile.DBType;
import ru.yandex.metrika.spring.profile.ProfileData;
import ru.yandex.metrika.spring.profile.ProfileQuery;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.toList;

public class ReportUtils {

    private static String[] QUOTED_TOKENS = new String[]{"\\", "'"};
    private static String[] REPLACEMENT_TOKENS = new String[]{"\\\\", "\\'"};

    public static String buildDimensionFilter(String dimension, String value) {
        if (value == null) {
            return dimension + "==null";
        } else {
            return dimension + "=='" + escapeApiFilterValue(value) + "'";
        }
    }

    public static List<String> getDrilldownDimensions(StatV1DataDrilldownGETSchema result) {
        return result.getData().stream()
                .map(row -> ReportUtils.extractStringDimensionValue(row.getDimension()))
                .collect(toList());
    }

    public static List<List<String>> getTableDimensions(StatV1DataGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(ReportUtils::extractStringDimensionValue).collect(toList()))
                .collect(toList());
    }

    public static List<List<String>> getBytimeDimensions(StatV1DataBytimeGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(ReportUtils::extractStringDimensionValue).collect(toList()))
                .collect(toList());
    }

    public static List<List<Double>> getTableMetrics(StatV1DataGETSchema result) {
        return result.getData().stream().map(StaticRow::getMetrics).collect(toList());
    }

    public static List<List<Double>> getDrilldownMetrics(StatV1DataDrilldownGETSchema result) {
        return result.getData().stream().map(DrillDownRow::getMetrics).collect(toList());
    }

    public static List<List<List<Double>>> getBytimeMetrics(StatV1DataBytimeGETSchema result) {
        return result.getData().stream().map(DynamicRow::getMetrics).collect(toList());
    }

    public static List<Double> getTableMetricsTotals(StatV1DataGETSchema result) {
        return result.getTotals();
    }

    public static List<Double> getDrilldownMetricsTotals(StatV1DataDrilldownGETSchema result) {
        return result.getTotals();
    }

    public static List<List<Double>> getBytimeMetricsTotals(StatV1DataBytimeGETSchema result) {
        return result.getTotals();
    }

    /**
     * Извлекает значение измерения (группировки) в виде строки, null не преобразуется,
     * сложные/комплексные значения преобразуются в строку объединением элементов.
     *
     * @param from значение измерения (группировки)
     * @return строковое представление
     */
    public static String extractStringDimensionValue(Map<String, ?> from) {
        Object value = extractDimensionValue(from);

        if (value instanceof Iterable) {
            StringBuilder stringBuilder = new StringBuilder();
            for (Object item : ((Iterable) value)) {
                if (item instanceof Map) {
                    /* Выход из цикла сделан для того, чтобы значения измерений (группировок) не склеивались.
                       Например:
                       Ответ содержит id'шники целей. Пусть будут id: 1, 2, 3, 4, 5. Если не выходить из цикла,
                       то вернется строка 12345 и тест будет провален, ибо такой цели нет. Для тестов же нам
                       будет достаточно только первого элемента. */
                    stringBuilder.append(extractDimensionValue((Map<String, Object>) item));
                    break;
                } else {
                    stringBuilder.append(Objects.toString(item, StringUtils.EMPTY));
                }
            }
            return stringBuilder.toString();
        } else {
            return Objects.toString(value, null);
        }
    }

    public static Object extractDimensionValue(Map<String, ?> dimension) {
        return dimension.containsKey("id")
                ? dimension.get("id")
                : dimension.get("name");
    }

    public static List<String> collectCHQueries(ProfileData profileData) {
        return profileData.getQueries().stream()
                .filter(q -> DBType.CLICKHOUSE.equals(q.getDbType()))
                .map(ProfileQuery::getQuery)
                .collect(Collectors.toList());
    }

    /**
     * Скопировано из ReportParamGenerationUtils, mobmetd
     */
    private static String escapeApiFilterValue(String value) {
        return StringUtils.replaceEach(value, QUOTED_TOKENS, REPLACEMENT_TOKENS);
    }

    private ReportUtils() {

    }
}
