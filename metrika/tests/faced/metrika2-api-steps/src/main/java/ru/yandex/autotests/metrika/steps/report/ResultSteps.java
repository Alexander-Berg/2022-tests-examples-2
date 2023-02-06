package ru.yandex.autotests.metrika.steps.report;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.collections4.functors.EqualPredicate;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.poi.ss.usermodel.Row;

import ru.yandex.autotests.httpclient.lite.core.steps.BackEndBaseSteps;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.beans.schemes.AnalyticsV3DataGaGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ResponseWrapper;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataComparisonDrilldownGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataComparisonGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;
import ru.yandex.autotests.metrika.converters.DimensionToNameMapper;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiException;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiWrapperException;
import ru.yandex.autotests.metrika.matchers.PairResponseMatcher;
import ru.yandex.autotests.metrika.utils.ReflectionUtils;
import ru.yandex.autotests.metrika.utils.Utils;
import ru.yandex.metrika.api.constructor.response.ComparisonQueryAB;
import ru.yandex.metrika.api.constructor.response.ComparisonRowDrillDownAB;
import ru.yandex.metrika.api.constructor.response.ComparisonRowStaticAB;
import ru.yandex.metrika.api.constructor.response.DrillDownRow;
import ru.yandex.metrika.api.constructor.response.DynamicQueryExternal;
import ru.yandex.metrika.api.constructor.response.DynamicRow;
import ru.yandex.metrika.api.constructor.response.QueryExternal;
import ru.yandex.metrika.api.constructor.response.StaticRow;

import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.base.Preconditions.checkState;
import static com.google.common.base.Throwables.propagate;
import static java.lang.String.format;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.collections4.ListUtils.indexOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.areBothSuccessful;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.isSimilarErrorCode;
import static ru.yandex.autotests.metrika.converters.CSVRecordToListConverter.csvToList;
import static ru.yandex.autotests.metrika.converters.CSVRecordToStringListConverter.csvToStringList;
import static ru.yandex.autotests.metrika.converters.CellIteratorToListConverter.cellToList;
import static ru.yandex.autotests.metrika.converters.CellIteratorToStringListConverter.cellToStringList;
import static ru.yandex.autotests.metrika.converters.DimensionToHumanReadableStringMapper.dimensionToHumanReadableStringMapper;
import static ru.yandex.autotests.metrika.matchers.ReportDataMatcher.expectNotEmptyReport;
import static ru.yandex.autotests.metrika.utils.ReflectionUtils.getProperty;
import static ru.yandex.autotests.metrika.utils.Utils.extractMetricValue;
import static ru.yandex.autotests.metrika.utils.Utils.extractStringDimensionValue;
import static ru.yandex.autotests.metrika.utils.Utils.getSlice;
import static ru.yandex.autotests.metrika.utils.Utils.zip;

/**
 * Created by konkov on 29.08.2014.
 */
public class ResultSteps extends BackEndBaseSteps {

    public static final String HEADER_MARKER = "Итого и средние";

    private int getDimensionIndex(QueryExternal query, String dimensionName)
            throws MetrikaApiException {
        int index = indexOf(query.getDimensions(), new EqualPredicate<>(dimensionName));

        if (index == -1) {
            throw new MetrikaApiException(String.format("Измерение %s не найдено в запросе", dimensionName));
        }

        return index;
    }

    private int getDimensionIndex(ComparisonQueryAB query, String dimensionName)
            throws MetrikaApiException {
        int index = indexOf(query.getDimensions(), new EqualPredicate<>(dimensionName));

        if (index == -1) {
            throw new MetrikaApiException(String.format("Измерение %s не найдено в запросе", dimensionName));
        }

        return index;
    }

    private int getDimensionIndex(DynamicQueryExternal query, String dimensionName)
            throws MetrikaApiException {
        int index = indexOf(query.getDimensions(), new EqualPredicate<>(dimensionName));

        if (index == -1) {
            throw new MetrikaApiException(String.format("Измерение %s не найдено в запросе", dimensionName));
        }

        return index;
    }

    private int getMetricIndex(ComparisonQueryAB query, String metricName)
            throws MetrikaApiException {
        int index = indexOf(query.getMetrics(), new EqualPredicate<>(metricName));

        if (index == -1) {
            throw new MetrikaApiException(String.format("Метрика %s не найдена в запросе", metricName));
        }

        return index;
    }

    private int getMetricIndex(DynamicQueryExternal query, String metricName)
            throws MetrikaApiException {
        int index = indexOf(query.getMetrics(), new EqualPredicate<>(metricName));

        if (index == -1) {
            throw new MetrikaApiException(String.format("Метрика %s не найдена в запросе", metricName));
        }

        return index;
    }

    public <T> List<List<String>> getDimensionsNamesOnly(ResponseWrapper<T> result) {
        checkNotNull(result);
        try {
            List<Object> data = result.getData();
            checkState(!data.isEmpty());

            Object dataItem = data.get(0);
            if (PropertyUtils.isReadable(dataItem, "dimensions")) {
                //список измерений
                return data.stream()
                        .map(d -> {
                            List<Map<String, String>> dimensions = getProperty(d, "dimensions");
                            return dimensions.stream()
                                    .map(dimensionToHumanReadableStringMapper())
                                    .collect(Collectors.toList());
                        })
                        .collect(Collectors.toList());

            } else if (PropertyUtils.isReadable(dataItem, "dimension")) {
                //одно измерение - берем единственное и заворачиваем в список
                return data.stream()
                        .map(d -> ReflectionUtils.<Map<String, String>>getProperty(d, "dimension"))
                        .map(dimensionToHumanReadableStringMapper())
                        .map(Collections::singletonList)
                        .collect(toList());
            } else {
                throw new MetrikaApiWrapperException(
                        format("Не обнаружено свойство data.dimensions или data.dimension у объекта класса %s",
                                dataItem.getClass().getName()));
            }
        } catch (Throwable e) {
            throw propagate(e);
        }
    }

    /**
     * Получение индекса заданной метрики
     *
     * @param query результат запроса
     * @param metricName наименование метрики
     * @return индекс заданной метрики
     * @throws MetrikaApiException
     */
    public int getMetricIndex(QueryExternal query, String metricName)
            throws MetrikaApiException {
        int index = indexOf(query.getMetrics(), new EqualPredicate<>(metricName));

        if (index == -1) {
            throw new MetrikaApiException(String.format("Метрика %s не найдена в запросе", metricName));
        }

        return index;
    }

    /**
     * Получение измерений для таблицы
     *
     * @param result схема данных из которой извлекаются измерения
     * @return двумерный массив измерений
     */
    public List<List<String>> getDimensions(StatV1DataGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(Utils::extractStringDimensionValue).collect(toList()))
                .collect(toList());
    }

    /**
     * Пучучение измерений из ответа GA
     *
     * @param result схема данных из которой извлекаются измерения
     * @return двумерный массив измерений
     */
    public List<List<String>> getDimensions(AnalyticsV3DataGaGETSchema result) {
        int dimensionsSize = result.getQuery().getDimensions().size();

        return result.getRows().stream()
                .map(row -> extractStringDimensionValue(row, dimensionsSize))
                .collect(toList());
    }

    /**
     * извлечение массива значений заданного атрибута из результата запроса
     *
     * @param dimension наименование атрибута
     * @param result    результат запроса
     * @return массив строковых представлений значений измерений
     */
    public List<String> getDimensionNameOnly(String dimension, StatV1DataGETSchema result) {
        int index = getDimensionIndex(result.getQuery(), dimension);

        List<List<String>> allDimensions = getDimensionsNameOnly(result);

        return getSlice(allDimensions, index);
    }

    /**
     * Получение только наименований измерений для таблицы
     *
     * @param result схема данных из которой извлекаются измерения
     * @return двумерный массив измерений
     */
    public List<List<String>> getDimensionsNameOnly(StatV1DataGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(dimensionToHumanReadableStringMapper())
                        .collect(toList()))
                .collect(toList());
    }

    /**
     * возвращает значение имени измерения в том виде, в котором его возвращает апи в json,
     * без костылей для экселя, которые эмулируют верстку директовских идентификаторов в интерфейсе.
     * @param result
     * @return
     */
    public List<List<String>> getDimensionsOnlyName(StatV1DataGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(new DimensionToNameMapper())
                        .collect(toList()))
                .collect(toList());
    }

    /**
     * Получение только наименований измерений для таблицы
     *
     * @param result схема данных из которой извлекаются измерения
     * @return массив измерений
     */
    public List<String> getDimensionsNameOnly(StatV1DataDrilldownGETSchema result) {
        return result.getData().stream()
                .map(DrillDownRow::getDimension)
                .map(dimensionToHumanReadableStringMapper())
                .collect(toList());
    }

    /**
     * Получение только наименований измерений для таблицы
     *
     * @param result схема данных из которой извлекаются измерения
     * @return массив измерений
     */
    public List<String> getDimensionsNameOnly(StatV1DataComparisonDrilldownGETSchema result) {
        return result.getData().stream()
                .map(ComparisonRowDrillDownAB::getDimension)
                .map(dimensionToHumanReadableStringMapper())
                .collect(toList());
    }

    /**
     * Получение только наименований измерений для таблицы
     *
     * @param result схема данных из которой извлекаются измерения
     * @return двумерный массив измерений
     */
    public List<List<String>> getDimensionsNameOnly(StatV1DataComparisonGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(dimensionToHumanReadableStringMapper())
                        .collect(toList()))
                .collect(toList());
    }

    /**
     * Получение только наименований измерений для таблицы
     *
     * @param result схема данных из которой извлекаются измерения
     * @return двумерный массив измерений
     */
    public List<List<String>> getDimensionsNameOnly(StatV1DataBytimeGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(dimensionToHumanReadableStringMapper())
                        .collect(toList()))
                .collect(toList());
    }

    /**
     * Получение метрик для таблицы
     *
     * @param result схема данных из которой извлекаются метрики
     * @return двумерный массив метрик
     */
    public List<List<Double>> getMetrics(StatV1DataGETSchema result) {
        return with(result.getData()).extract(on(StaticRow.class).getMetrics());
    }

    /**
     * Получение метрик из ответа GA
     *
     * @param result схема данных из которой извлекаются метрики
     * @return двумерный массив метрик
     */
    public List<List<Double>> getMetrics(AnalyticsV3DataGaGETSchema result) {
        int dimensionsSize = result.getQuery().getDimensions().size();

        return result.getRows().stream()
                .map(m -> extractMetricValue(m, dimensionsSize)).collect(toList());
    }

    /**
     * Получение всех значений заданной метрики из результата
     *
     * @param metricName наименование метрики
     * @param result     схема данных из которой извлекаются метрики
     * @return массив значений заданной метрики
     */
    public List<Double> getMetrics(String metricName, StatV1DataGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);

        List<List<Double>> allMetrics = getMetrics(result);

        return getSlice(allMetrics, index);
    }

    /**
     * Получение всех значений заданной метрики из результата
     *
     * @param metricName наименование метрики
     * @param result     схема данных из которой извлекаются метрики
     * @return массив значений заданной метрики
     */
    public List<Double> getMetrics(String metricName, StatV1DataDrilldownGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);

        List<List<Double>> allMetrics = getMetrics(result);

        return getSlice(allMetrics, index);
    }

    /**
     * Получение всех значений заданной метрики из результата
     *
     * @param metricName наименование метрики
     * @param result     схема данных из которой извлекаются метрики
     * @return массив содержащий два массива значений метрик, соответствующих сегментам a и b
     */
    public List<List<Double>> getMetrics(String metricName, StatV1DataComparisonGETSchema result) {
        int index_a = getMetricIndex(result.getQuery(), metricName);
        int index_b = index_a + result.getQuery().getMetrics().size();

        List<List<Double>> allMetrics = getMetrics(result);

        return asList(getSlice(allMetrics, index_a), getSlice(allMetrics, index_b));
    }

    /**
     * Получение всех значений заданной метрики из результата
     *
     * @param metricName наименование метрики
     * @param result     схема данных из которой извлекаются метрики
     * @return массив содержащий два массива значений метрик, соответствующих сегментам a и b
     */
    public List<List<Double>> getMetrics(String metricName, StatV1DataComparisonDrilldownGETSchema result) {
        int index_a = getMetricIndex(result.getQuery(), metricName);
        int index_b = index_a + result.getQuery().getMetrics().size();

        List<List<Double>> allMetrics = getMetrics(result);

        return asList(getSlice(allMetrics, index_a), getSlice(allMetrics, index_b));
    }

    /**
     * Получение всех значений заданной метрики из результата
     *
     * @param metricName наименование метрики
     * @param result     схема данных из которой извлекаются метрики
     * @return массив значений заданной метрики
     */
    public List<List<Double>> getMetrics(String metricName, StatV1DataBytimeGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);

        List<List<List<Double>>> allMetrics = getMetrics(result);

        return getSlice(allMetrics, index);
    }

    /**
     * Получение измерений для данных по времени
     *
     * @param result схема данных из которой извлекаются измерения
     * @return двумерный массив измерений
     */
    public List<List<String>> getDimensions(StatV1DataBytimeGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(Utils::extractStringDimensionValue).collect(toList()))
                .collect(toList());
    }

    /**
     * Получение метрик для данных по времени
     *
     * @param result схема данных из которой извлекаются метрики
     * @return трехмерный массив метрик
     */
    public List<List<List<Double>>> getMetrics(StatV1DataBytimeGETSchema result) {
        return with(result.getData()).extract(on(DynamicRow.class).getMetrics());
    }

    /**
     * Получение значений измерений для данных сравнения таблиц
     *
     * @param result результат запроса сравнения таблиц
     * @return двумерный массив значений измерений
     */
    public List<List<String>> getDimensions(StatV1DataComparisonGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(Utils::extractStringDimensionValue).collect(toList()))
                .collect(toList());
    }

    /**
     * Получение значений метрик для данных сравнения таблиц
     *
     * @param result схема данных из которой извлекаются метрики
     * @return двумерный массив метрик
     */
    public List<List<Double>> getMetrics(StatV1DataComparisonGETSchema result) {
        List<List<Double>> a = with(result.getData()).extract(on(ComparisonRowStaticAB.class).getMetrics().getA());
        List<List<Double>> b = with(result.getData()).extract(on(ComparisonRowStaticAB.class).getMetrics().getB());

        return zip(a, b);
    }

    /**
     * Получение измерений для сравнения drill down
     *
     * @param result схема данных из которой извлекаются измерения
     * @return одномерный массив измерений
     */
    public List<String> getDimensions(StatV1DataComparisonDrilldownGETSchema result) {
        return result.getData().stream()
                .map(row -> extractStringDimensionValue(row.getDimension()))
                .collect(toList());
    }

    /**
     * Получение метрик для сравнения drill down
     *
     * @param result схема данных из которой извлекаются метрики
     * @return двумерный массив метрик
     */
    public List<List<Double>> getMetrics(StatV1DataComparisonDrilldownGETSchema result) {
        List<List<Double>> a = with(result.getData()).extract(on(ComparisonRowDrillDownAB.class).getMetrics().getA());
        List<List<Double>> b = with(result.getData()).extract(on(ComparisonRowDrillDownAB.class).getMetrics().getB());

        return zip(a, b);
    }

    /**
     * Получение измерений для drill down
     *
     * @param result схема данных из которой извлекаются измерения
     * @return массив измерений
     */
    public List<String> getDimensions(StatV1DataDrilldownGETSchema result) {
        return result.getData().stream()
                .map(row -> extractStringDimensionValue(row.getDimension()))
                .collect(toList());
    }

    /**
     * Получение метрик для drill down
     *
     * @param result схема данных из которой извлекаются метрики
     * @return двумерный массив метрик
     */
    public List<List<Double>> getMetrics(StatV1DataDrilldownGETSchema result) {
        return with(result.getData()).extract(on(DrillDownRow.class).getMetrics());
    }

    /**
     * Получение измерений и метрик для данных в формате csv
     *
     * @param result схема данных из которой извлекаются измерения и метрики
     * @return двумерный массив измерений и метрик
     */
    public List<List<String>> getDimensionsAndMetricsFromCsv(StatV1DataCsvSchema result) {

        List<List<String>> data = getStringDataFromCsv(result);

        /* Первые строки - заголовок, пропустим их
        Если есть строка, вначале которой стоит "Итого и средние", то берем, все, что после нее
        Если такой строки нет, то отбрасываем только первую строку.
         */

        List<String> headers = with(data).first(hasItem(containsString(HEADER_MARKER)));

        int headerLines = headers != null
                ? data.indexOf(headers) + 1
                : 1;

        if (headerLines > data.size()) {
            return new ArrayList<>();
        }

        return data.subList(headerLines, data.size());
    }

    /**
     * Получение измерений и метрик для данных в формате xlsx
     *
     * @param result схема данных из которой извлекаются измерения и метрики
     * @return двумерный массив измерений и метрик
     */
    public List<List<String>> getDimensionsAndMetricsFromXlsx(StatV1DataXlsxSchema result) {

        List<List<String>> data = getStringDataFromXlsx(result);


        /* Первые строки - заголовок, пропустим их
        Если есть строка, вначале которой стоит "Итого и средние", то берем, все, что после нее
        Если такой строки нет, то берем все через строку, после первой пустой строки
         */
        List<String> headers = with(data).first(hasItem(containsString(HEADER_MARKER)));
        List<String> emptyString = data.stream().filter(list -> list.get(0).equals("")).findFirst().get();

        int headerLines = headers != null
                ? data.indexOf(headers) + 1
                : data.indexOf(emptyString) + 2;

        if (headerLines > data.size()) {
            return new ArrayList<>();
        }

        return data.subList(headerLines, data.size());
    }

    /**
     * Получение всех данных для отчетов в формате xlsx в <b>строковом</b> виде
     *
     * @param result схема данных из которой извлекаются измерения и метрики
     * @return двумерный массив со всеми данными
     */
    public List<List<String>> getStringDataFromXlsx(StatV1DataXlsxSchema result) {
        Iterable<Row> iterable = () -> result.getData().rowIterator();

        return StreamSupport.stream(iterable.spliterator(), false)
                .map(Row::cellIterator)
                .map(cellToStringList())
                .collect(toList());

    }

    public List<List<Object>> getDataFromXlsx(StatV1DataXlsxSchema result) {
        Iterable<Row> iterable = () -> result.getData().rowIterator();

        return StreamSupport.stream(iterable.spliterator(), false)
                .map(Row::cellIterator)
                .map(cellToList())
                .collect(toList());

    }

    /**
     * Получение всех данных для отчетов в формате csv
     *
     * @param result схема данных из которой извлекаются измерения и метрики
     * @return двумерный массив со всеми данными
     */
    public List<List<String>> getStringDataFromCsv(StatV1DataCsvSchema result) {
        return result.getData().stream()
                .map(csvToStringList())
                .collect(toList());
    }

    public List<List<Object>> getDataFromCsv(StatV1DataCsvSchema result) {
        return result.getData().stream()
                .map(csvToList())
                .collect(toList());
    }

    /**
     * Получение строки произвольного отчета по произвольному условию
     *
     * @param rows строки отчета
     * @param predicate условие нахождения строки
     * @param <TRow> тип строки отчета
     * @return найденная строка отчета
     */
    public <TRow> TRow findRow(List<TRow> rows, Predicate<TRow> predicate) {
        TRow resultRow = rows.stream()
                .filter(predicate)
                .findFirst()
                .orElse(null);

        TestSteps.assumeThat("строка в отчете найдена", resultRow, notNullValue());
        return resultRow;
    }

    /**
     * Получение строки отчета по значениям группировок
     *
     * @param result отчет
     * @param dimensionValueNames значения группировок в человекочитаемом виде
     * @return строка отчета
     */
    public StaticRow findRow(StatV1DataGETSchema result, Set<String> dimensionValueNames) {
        return findRow(result.getData(), row -> row.getDimensions().stream()
                .map(dimensionToHumanReadableStringMapper())
                .collect(Collectors.toSet()).equals(dimensionValueNames));
    }

    /**
     * Получение строки отчета drilldown по значению группировки
     *
     * @param result отчет
     * @param dimensionValueName значение группировки в человекочитаемом виде
     * @return строка отчета
     */
    public DrillDownRow findRow(StatV1DataDrilldownGETSchema result, String dimensionValueName) {
        return findRow(result.getData(), row -> StringUtils.equals(
                dimensionToHumanReadableStringMapper().apply(row.getDimension()),
                dimensionValueName));
    }

    /**
     * Получение строки отчета по времени по значениям группировок
     *
     * @param result отчет
     * @param dimensionValueNames значения группировок в человекочитаемом виде
     * @return строка отчета
     */
    public DynamicRow findRow(StatV1DataBytimeGETSchema result, Set<String> dimensionValueNames) {
        return findRow(result.getData(), row -> row.getDimensions().stream()
                .map(dimensionToHumanReadableStringMapper())
                .collect(Collectors.toSet()).equals(dimensionValueNames));
    }

    /**
     * Получение строки отчета-сравнения по значениям группировок
     *
     * @param result отчет
     * @param dimensionValueNames значения группировок в человекочитаемом виде
     * @return строка отчета
     */
    public ComparisonRowStaticAB findRow(StatV1DataComparisonGETSchema result, Set<String> dimensionValueNames) {
        return findRow(result.getData(), row -> row.getDimensions().stream()
                .map(dimensionToHumanReadableStringMapper())
                .collect(Collectors.toSet()).equals(dimensionValueNames));
    }

    /**
     * Получение строки отчета-сравнения drilldown по значению группировки
     *
     * @param result отчет
     * @param dimensionValueName значение группировки в человекочитаемом виде
     * @return строка отчета
     */
    public ComparisonRowDrillDownAB findRow(StatV1DataComparisonDrilldownGETSchema result, String dimensionValueName) {
        return findRow(result.getData(), row -> StringUtils.equals(
                dimensionToHumanReadableStringMapper().apply(row.getDimension()),
                dimensionValueName));
    }

    /**
     * извлечение массива значений заданного измерения из результата запроса
     *
     * @param dimension наименование измерения
     * @param result    результат запроса
     * @return массив строковых представлений значений измерений
     */
    public List<String> getDimensionValues(String dimension, StatV1DataGETSchema result) {
        int index = getDimensionIndex(result.getQuery(), dimension);

        List<List<String>> allDimensions = getDimensions(result);

        return getSlice(allDimensions, index);
    }

    /**
     * извлечение массива значений заданного измерения из результата запроса
     *
     * @param dimension наименование измерения
     * @param result    результат запроса
     * @return массив строковых представлений значений измерений
     */
    public List<String> getDimensionValues(String dimension, StatV1DataComparisonGETSchema result) {
        int index = getDimensionIndex(result.getQuery(), dimension);

        List<List<String>> allDimensions = getDimensions(result);

        return getSlice(allDimensions, index);
    }

    /**
     * извлечение массива значений заданного измерения из результата запроса
     *
     * @param dimension наименование измерения
     * @param result    результат запроса
     * @return массив строковых представлений значений измерений
     */
    public List<String> getDimensionValues(String dimension, StatV1DataBytimeGETSchema result) {
        int index = getDimensionIndex(result.getQuery(), dimension);

        List<List<String>> allDimensions = getDimensions(result);

        return getSlice(allDimensions, index);
    }


    /**
     * Получение флага доверия к данным
     *
     * @param result отчет из которого извлекаются данные
     * @return массив флагов
     */
    public List<List<Boolean>> getMetricsConfidenceFlags(StatV1DataGETSchema result) {
        return with(result.getData())
                .extract(on(StaticRow.class).getMetricsConfidenceFlags());
    }

    /**
     * Получение флага доверия к данным
     *
     * @param metricName наименование метрики
     * @param result     отчет из которого извлекаются данные
     * @return массив флагов
     */
    public List<Boolean> getMetricsConfidenceFlags(String metricName, StatV1DataGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);
        List<List<Boolean>> flags = getMetricsConfidenceFlags(result);

        return getSlice(flags, index);
    }

    /**
     * Получение флага доверия к данным
     *
     * @param result отчет из которого извлекаются данные
     * @return массив флагов
     */
    public List<List<Boolean>> getMetricsConfidenceFlags(StatV1DataDrilldownGETSchema result) {
        return with(result.getData())
                .extract(on(DrillDownRow.class).getMetricsConfidenceFlags());
    }

    /**
     * Получение флага доверия к данным
     *
     * @param metricName наименование метрики
     * @param result     отчет из которого извлекаются данные
     * @return массив флагов
     */
    public List<Boolean> getMetricsConfidenceFlags(String metricName, StatV1DataDrilldownGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);
        List<List<Boolean>> flags = getMetricsConfidenceFlags(result);

        return getSlice(flags, index);
    }

    /**
     * Получение флага доверия к данным
     *
     * @param result отчет из которого извлекаются данные
     * @return массив флагов
     */
    public List<List<Boolean>> getMetricsConfidenceFlags(StatV1DataComparisonDrilldownGETSchema result) {
        List<List<Boolean>> flagsA = with(result.getData())
                .extract(on(ComparisonRowDrillDownAB.class).getMetrics().getAConfidenceFlags());

        List<List<Boolean>> flagsB = with(result.getData())
                .extract(on(ComparisonRowDrillDownAB.class).getMetrics().getBConfidenceFlags());

        return zip(flagsA, flagsB);
    }

    /**
     * Получение флага доверия к данным
     *
     * @param metricName наименование метрики
     * @param result     отчет из которого извлекаются данные
     * @return массив флагов
     */
    public List<Boolean> getMetricsConfidenceFlags(String metricName, StatV1DataComparisonDrilldownGETSchema result) {
        //извлекаем только для сегмента A
        int index = getMetricIndex(result.getQuery(), metricName);
        List<List<Boolean>> flags = getMetricsConfidenceFlags(result);

        return getSlice(flags, index);
    }

    /**
     * Получение флага доверия к данным
     *
     * @param result отчет из которого извлекаются данные
     * @return массив флагов
     */
    public List<List<Boolean>> getMetricsConfidenceFlags(StatV1DataComparisonGETSchema result) {
        List<List<Boolean>> flagsA = with(result.getData())
                .extract(on(ComparisonRowStaticAB.class).getMetrics().getAConfidenceFlags());

        List<List<Boolean>> flagsB = with(result.getData())
                .extract(on(ComparisonRowStaticAB.class).getMetrics().getBConfidenceFlags());

        return zip(flagsA, flagsB);
    }

    /**
     * Получение флага доверия к данным
     *
     * @param metricName наименование метрики
     * @param result     отчет из которого извлекаются данные
     * @return массив флагов
     */
    public List<Boolean> getMetricsConfidenceFlags(String metricName, StatV1DataComparisonGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);
        List<List<Boolean>> flags = with(result.getData())
                .extract(on(ComparisonRowStaticAB.class).getMetrics().getAConfidenceFlags());

        return getSlice(flags, index);
    }

    /**
     * Получение порога доверия к данным
     *
     * @param result отчет из которого извлекаются данные
     * @return массив значений порога
     */
    public List<List<Long>> getMetricsConfidenceThreshold(StatV1DataGETSchema result) {
        return with(result.getData())
                .extract(on(StaticRow.class).getMetricsConfidenceThreshold());
    }

    /**
     * Получение порога доверия к данным
     *
     * @param metricName наименование метрики
     * @param result     отчет из которого извлекаются данные
     * @return массив значений порога
     */
    public List<Long> getMetricsConfidenceThreshold(String metricName, StatV1DataGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);
        List<List<Long>> thresholds = getMetricsConfidenceThreshold(result);

        return getSlice(thresholds, index);
    }

    /**
     * Получение порога доверия к данным
     *
     * @param result отчет из которого извлекаются данные
     * @return массив значений порога
     */
    public List<List<Long>> getMetricsConfidenceThreshold(StatV1DataDrilldownGETSchema result) {
        return with(result.getData())
                .extract(on(DrillDownRow.class).getMetricsConfidenceThreshold());
    }

    /**
     * Получение порога доверия к данным
     *
     * @param metricName наименование метрики
     * @param result     отчет из которого извлекаются данные
     * @return массив значений порога
     */
    public List<Long> getMetricsConfidenceThreshold(String metricName, StatV1DataDrilldownGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);
        List<List<Long>> thresholds = getMetricsConfidenceThreshold(result);

        return getSlice(thresholds, index);
    }

    /**
     * Получение порога доверия к данным
     *
     * @param result отчет из которого извлекаются данные
     * @return массив значений порога
     */
    public List<List<Long>> getMetricsConfidenceThreshold(StatV1DataComparisonDrilldownGETSchema result) {
        return with(result.getData())
                .extract(on(ComparisonRowDrillDownAB.class).getMetrics().getAConfidenceThreshold());
    }

    /**
     * Получение порога доверия к данным
     *
     * @param metricName наименование метрики
     * @param result     отчет из которого извлекаются данные
     * @return массив значений порога
     */
    public List<Long> getMetricsConfidenceThreshold(String metricName, StatV1DataComparisonDrilldownGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);
        List<List<Long>> thresholds = getMetricsConfidenceThreshold(result);

        return getSlice(thresholds, index);
    }

    /**
     * Получение порога доверия к данным
     *
     * @param result отчет из которого извлекаются данные
     * @return массив значений порога
     */
    public List<List<Long>> getMetricsConfidenceThreshold(StatV1DataComparisonGETSchema result) {
        return with(result.getData())
                .extract(on(ComparisonRowStaticAB.class).getMetrics().getAConfidenceThreshold());
    }

    /**
     * Получение порога доверия к данным
     *
     * @param metricName наименование метрики
     * @param result     отчет из которого извлекаются данные
     * @return массив значений порога
     */
    public List<Long> getMetricsConfidenceThreshold(String metricName, StatV1DataComparisonGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);
        List<List<Long>> thresholds = getMetricsConfidenceThreshold(result);

        return getSlice(thresholds, index);
    }

    /**
     * получить значения измерений для тех строк, где данным можно доверять.
     *
     * @param result     - отчет из которого извлекаются данные
     * @param metricName - метрика, на основании которой проверяется доверие.
     * @return - массив значений измерений, значение попадает в массив, если метрика не поддерживает
     * режим доверия, либо если она поддерживает режим доверия и значению метрики можно доверять -
     * соответствующий флаг равен true.
     */
    public List<List<String>> getDimensionsWithConfidence(StatV1DataGETSchema result, String metricName) {
        int metricIndex = getMetricIndex(result.getQuery(), metricName);

        return result.getData().stream()
                .filter(row -> row.getMetricsConfidenceFlags().get(metricIndex))
                .map(row -> row.getDimensions().stream()
                        .map(Utils::extractStringDimensionValue)
                        .collect(toList()))
                .collect(toList());
    }

    /**
     * получение значений заданного измерения из тех строк, где данным можно доверять
     *
     * @param dimensionName - наименование измерения, чьи значения извлекаются
     * @param result        - отчет из которого извлекаются данные
     * @param metricName    - метрика, на основании которой проверяется доверие.
     * @return - массив значений измерений, значение попадает в массив, если метрика не поддерживает
     * режим доверия, либо если она поддерживает режим доверия и значению метрики можно доверять -
     * соответствующий флаг равен true.
     */
    public List<String> getDimensionValuesWithConfidence(String dimensionName,
                                                         StatV1DataGETSchema result,
                                                         String metricName) {

        int dimensionIndex = getDimensionIndex(result.getQuery(), dimensionName);

        List<List<String>> allDimensions = getDimensionsWithConfidence(result, metricName);

        return getSlice(allDimensions, dimensionIndex);
    }

    /**
     * получить значения измерений для тех строк, где данным можно доверять.
     *
     * @param result     - отчет из которого извлекаются данные
     * @param metricName - метрика, на основании которой проверяется доверие.
     * @return - массив значений измерений, значение попадает в массив, если метрика не поддерживает
     * режим доверия, либо если она поддерживает режим доверия и значению метрики можно доверять -
     * соответствующий флаг равен true.
     */
    public List<List<String>> getDimensionsWithConfidence(StatV1DataComparisonGETSchema result, String metricName) {
        int metricIndex = getMetricIndex(result.getQuery(), metricName);

        return result.getData().stream()
                .filter(row -> row.getMetrics().getAConfidenceFlags().get(metricIndex))
                .map(row -> row.getDimensions().stream()
                        .map(Utils::extractStringDimensionValue)
                        .collect(toList()))
                .collect(toList());
    }

    /**
     * получение значений заданного измерения из тех строк, где данным можно доверять
     *
     * @param dimensionName - наименование измерения, чьи значения извлекаются
     * @param result        - отчет из которого извлекаются данные
     * @param metricName    - метрика, на основании которой проверяется доверие.
     * @return - массив значений измерений, значение попадает в массив, если метрика не поддерживает
     * режим доверия, либо если она поддерживает режим доверия и значению метрики можно доверять -
     * соответствующий флаг равен true.
     */
    public List<String> getDimensionValuesWithConfidence(String dimensionName,
                                                         StatV1DataComparisonGETSchema result,
                                                         String metricName) {

        int dimensionIndex = getDimensionIndex(result.getQuery(), dimensionName);

        List<List<String>> allDimensions = getDimensionsWithConfidence(result, metricName);

        return getSlice(allDimensions, dimensionIndex);
    }

    /**
     * получение значений измерения из тех строк, где данным можно доверять
     *
     * @param result     - отчет из которого извлекаются данные
     * @param metricName - метрика, на основании которой проверяется доверие.
     * @return - массив значений измерений, значение попадает в массив, если метрика не поддерживает
     * режим доверия, либо если она поддерживает режим доверия и значению метрики можно доверять -
     * соответствующий флаг равен true.
     */
    public List<String> getDimensionValuesWithConfidence(StatV1DataDrilldownGETSchema result, String metricName) {
        int metricIndex = getMetricIndex(result.getQuery(), metricName);

        return result.getData().stream()
                .filter(row -> row.getMetricsConfidenceFlags().get(metricIndex))
                .map(row -> extractStringDimensionValue(row.getDimension()))
                .collect(toList());
    }

    /**
     * получение значений измерения из тех строк, где данным можно доверять
     *
     * @param result     - отчет из которого извлекаются данные
     * @param metricName - метрика, на основании которой проверяется доверие.
     * @return - массив значений измерений, значение попадает в массив, если метрика не поддерживает
     * режим доверия, либо если она поддерживает режим доверия и значению метрики можно доверять -
     * соответствующий флаг равен true.
     */
    public List<String> getDimensionValuesWithConfidence(StatV1DataComparisonDrilldownGETSchema result, String metricName) {
        int metricIndex = getMetricIndex(result.getQuery(), metricName);

        return result.getData().stream()
                .filter(row -> row.getMetrics().getAConfidenceFlags().get(metricIndex))
                .map(row -> extractStringDimensionValue(row.getDimension()))
                .collect(toList());
    }

    /**
     * Извлечение итоговых значений из результата сравнения сегментов
     *
     * @param result - отчет из которого извлекаются данные
     * @return массив итоговых значений, сначала идут значения для сегмента A, затем для сегмента B
     */
    public List<Double> getTotals(StatV1DataComparisonGETSchema result) {
        List<Double> totals = new ArrayList<>();

        totals.addAll(result.getTotals().getA());
        totals.addAll(result.getTotals().getB());

        return totals;
    }

    /**
     * Извлечение итоговых значений из результата сравнения drill down
     *
     * @param result - отчет из которого извлекаются данные
     * @return массив итоговых значений, сначала идут значения для сегмента A, затем для сегмента B
     */
    public List<Double> getTotals(StatV1DataComparisonDrilldownGETSchema result) {
        List<Double> totals = new ArrayList<>();

        totals.addAll(result.getTotals().getA());
        totals.addAll(result.getTotals().getB());

        return totals;
    }

    /**
     * Осуществляет проверку ожидания сходного кода ошибки.
     * Выбрасывает исключение и ломает тест, если один из результатов содержит ошибку, а другой нет.
     *
     * @param testingBean   - результат запроса к тестируемой среде
     * @param referenceBean - результат запроса к образцовой среде
     */
    public void assumeSimilarErrorCode(Object testingBean, Object referenceBean) {
        TestSteps.assumeThat("обе среды ответили одинаковым кодом",
                testingBean, isSimilarErrorCode(referenceBean));
    }

    /**
     * Осуществляет проверку ожидания того, что оба ответа успешные.
     *
     * @param testingBean   - результат запроса к тестируемой среде
     * @param referenceBean - результат запроса к образцовой среде
     */
    public void assumeSuccessBoth(Object testingBean, Object referenceBean) {
        TestSteps.assumeThat("оба запроса были успешны",
                ImmutablePair.of(referenceBean, testingBean),
                areBothSuccessful());
    }

    /**
     * Осуществляет проверку ожидания того, что оба ответа содержат непустой отчет
     *
     * @param testingBean   - результат запроса к тестируемой среде
     * @param referenceBean - результат запроса к образцовой среде
     */
    public void assumeNotEmptyBoth(Object testingBean, Object referenceBean) {
        TestSteps.assumeThat("оба ответа содержат непустой отчет",
                ImmutablePair.of(referenceBean, testingBean),
                new PairResponseMatcher(expectNotEmptyReport(), expectNotEmptyReport()));
    }

}
