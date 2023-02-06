package ru.yandex.autotests.advapi.steps.report;

import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.collections4.functors.EqualPredicate;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import ru.yandex.advapi.V1StatDataBytimeGETSchema;
import ru.yandex.advapi.V1StatDataDrilldownGETSchema;
import ru.yandex.advapi.V1StatDataGETSchema;
import ru.yandex.autotests.advapi.Utils;
import ru.yandex.autotests.advapi.beans.ResponseWrapper;
import ru.yandex.autotests.advapi.converters.DimensionToNameMapper;
import ru.yandex.autotests.advapi.exceptions.MetrikaApiException;
import ru.yandex.autotests.advapi.exceptions.MetrikaApiWrapperException;
import ru.yandex.autotests.httpclient.lite.core.steps.BackEndBaseSteps;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.commons.response.PairResponseMatcher;
import ru.yandex.metrika.api.constructor.response.*;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.BiFunction;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.base.Preconditions.checkState;
import static com.google.common.base.Throwables.propagate;
import static java.lang.String.format;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.collections4.ListUtils.indexOf;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.advapi.Utils.extractStringDimensionValue;
import static ru.yandex.autotests.advapi.Utils.getSlice;
import static ru.yandex.autotests.advapi.converters.DimensionToHumanReadableStringMapper.dimensionToHumanReadableStringMapper;
import static ru.yandex.autotests.advapi.matchers.ReportDataMatcher.expectNotEmptyReport;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.areBothSuccessful;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.isSimilarErrorCode;

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

    private int getDimensionIndex(DynamicQueryExternal query, String dimensionName)
            throws MetrikaApiException {
        int index = indexOf(query.getDimensions(), new EqualPredicate<>(dimensionName));

        if (index == -1) {
            throw new MetrikaApiException(String.format("Измерение %s не найдено в запросе", dimensionName));
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
                        .map(d -> (Map<String, String>) getProperty(d, "dimension"))
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
     * @param query      результат запроса
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
    public List<List<String>> getDimensions(V1StatDataGETSchema result) {
        return result.getData()
                .stream()
                .map(row ->
                        row.getDimensions()
                                .stream()
                                .map(Utils::extractStringDimensionValue)
                                .collect(toList())
                ).collect(toList());
    }

    /**
     * извлечение массива значений заданного атрибута из результата запроса
     *
     * @param dimension наименование атрибута
     * @param result    результат запроса
     * @return массив строковых представлений значений измерений
     */
    public List<String> getDimensionNameOnly(String dimension, V1StatDataGETSchema result) {
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
    public List<List<String>> getDimensionsNameOnly(V1StatDataGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(dimensionToHumanReadableStringMapper())
                        .collect(toList()))
                .collect(toList());
    }

    /**
     * возвращает значение имени измерения в том виде, в котором его возвращает апи в json,
     * без костылей для экселя, которые эмулируют верстку директовских идентификаторов в интерфейсе.
     *
     * @param result
     * @return
     */
    public List<List<String>> getDimensionsOnlyName(V1StatDataGETSchema result) {
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
    public List<String> getDimensionsNameOnly(V1StatDataDrilldownGETSchema result) {
        return result.getData().stream()
                .map(DrillDownRow::getDimension)
                .map(dimensionToHumanReadableStringMapper())
                .collect(toList());
    }

    /**
     * Получение только наименований измерений для таблицы
     *
     * @param result схема данных из которой извлекаются измерения
     * @return двумерный массив измерений
     */
    public List<List<String>> getDimensionsNameOnly(V1StatDataBytimeGETSchema result) {
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
    public List<List<Double>> getMetrics(V1StatDataGETSchema result) {
        return with(result.getData()).extract(on(StaticRow.class).getMetrics());
    }

    /**
     * Получение всех значений заданной метрики из результата
     *
     * @param metricName наименование метрики
     * @param result     схема данных из которой извлекаются метрики
     * @return массив значений заданной метрики
     */
    public List<Double> getMetrics(String metricName, V1StatDataGETSchema result) {
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
    public List<Double> getMetrics(String metricName, V1StatDataDrilldownGETSchema result) {
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
    public List<List<Double>> getMetrics(String metricName, V1StatDataBytimeGETSchema result) {
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
    public List<List<String>> getDimensions(V1StatDataBytimeGETSchema result) {
        return result.getData().stream()
                .map(row -> row.getDimensions()
                        .stream()
                        .map(Utils::extractStringDimensionValue)
                        .collect(toList())
                ).collect(toList());
    }

    /**
     * Получение метрик для данных по времени
     *
     * @param result схема данных из которой извлекаются метрики
     * @return трехмерный массив метрик
     */
    public List<List<List<Double>>> getMetrics(V1StatDataBytimeGETSchema result) {
        return with(result.getData()).extract(on(DynamicRow.class).getMetrics());
    }

    /**
     * Получение измерений для drill down
     *
     * @param result схема данных из которой извлекаются измерения
     * @return массив измерений
     */
    public List<String> getDimensions(V1StatDataDrilldownGETSchema result) {
        return result.getData()
                .stream()
                .map(row -> extractStringDimensionValue(row.getDimension()))
                .collect(toList());
    }

    /**
     * Получение метрик для drill down
     *
     * @param result схема данных из которой извлекаются метрики
     * @return двумерный массив метрик
     */
    public List<List<Double>> getMetrics(V1StatDataDrilldownGETSchema result) {
        return with(result.getData()).extract(on(DrillDownRow.class).getMetrics());
    }

    /**
     * Получение строки произвольного отчета по произвольному условию
     *
     * @param rows      строки отчета
     * @param predicate условие нахождения строки
     * @param <TRow>    тип строки отчета
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
     * @param result              отчет
     * @param dimensionValueNames значения группировок в человекочитаемом виде
     * @return строка отчета
     */
    public StaticRow findRow(V1StatDataGETSchema result, Set<String> dimensionValueNames) {
        return findRow(
                result.getData(),
                row -> row.getDimensions()
                        .stream()
                        .map(dimensionToHumanReadableStringMapper())
                        .collect(Collectors.toSet())
                        .equals(dimensionValueNames)
        );
    }

    /**
     * Получение строки отчета drilldown по значению группировки
     *
     * @param result             отчет
     * @param dimensionValueName значение группировки в человекочитаемом виде
     * @return строка отчета
     */
    public DrillDownRow findRow(V1StatDataDrilldownGETSchema result, String dimensionValueName) {
        return findRow(result.getData(), row -> StringUtils.equals(
                dimensionToHumanReadableStringMapper().apply(row.getDimension()),
                dimensionValueName));
    }

    /**
     * Получение строки отчета по времени по значениям группировок
     *
     * @param result              отчет
     * @param dimensionValueNames значения группировок в человекочитаемом виде
     * @return строка отчета
     */
    public DynamicRow findRow(V1StatDataBytimeGETSchema result, Set<String> dimensionValueNames) {
        return findRow(result.getData(), row -> row.getDimensions().stream()
                .map(dimensionToHumanReadableStringMapper())
                .collect(Collectors.toSet()).equals(dimensionValueNames));
    }

    /**
     * извлечение массива значений заданного измерения из результата запроса
     *
     * @param dimension наименование измерения
     * @param result    результат запроса
     * @return массив строковых представлений значений измерений
     */
    public List<String> getDimensionValues(String dimension, V1StatDataGETSchema result) {
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
    public List<String> getDimensionValues(String dimension, V1StatDataBytimeGETSchema result) {
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
    public List<List<Boolean>> getMetricsConfidenceFlags(V1StatDataGETSchema result) {
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
    public List<Boolean> getMetricsConfidenceFlags(String metricName, V1StatDataGETSchema result) {
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
    public List<List<Boolean>> getMetricsConfidenceFlags(V1StatDataDrilldownGETSchema result) {
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
    public List<Boolean> getMetricsConfidenceFlags(String metricName, V1StatDataDrilldownGETSchema result) {
        int index = getMetricIndex(result.getQuery(), metricName);
        List<List<Boolean>> flags = getMetricsConfidenceFlags(result);
        return getSlice(flags, index);
    }

    /**
     * Получение порога доверия к данным
     *
     * @param result отчет из которого извлекаются данные
     * @return массив значений порога
     */
    public List<List<Long>> getMetricsConfidenceThreshold(V1StatDataGETSchema result) {
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
    public List<Long> getMetricsConfidenceThreshold(String metricName, V1StatDataGETSchema result) {
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
    public List<List<Long>> getMetricsConfidenceThreshold(V1StatDataDrilldownGETSchema result) {
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
    public List<Long> getMetricsConfidenceThreshold(String metricName, V1StatDataDrilldownGETSchema result) {
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
    public List<List<String>> getDimensionsWithConfidence(V1StatDataGETSchema result, String metricName) {
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
                                                         V1StatDataGETSchema result,
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
    public List<String> getDimensionValuesWithConfidence(V1StatDataDrilldownGETSchema result, String metricName) {
        int metricIndex = getMetricIndex(result.getQuery(), metricName);

        return result.getData().stream()
                .filter(row -> row.getMetricsConfidenceFlags().get(metricIndex))
                .map(row -> extractStringDimensionValue(row.getDimension()))
                .collect(toList());
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

    /**
     * Складывает данные скроллов.
     */
    public List<Long> scrollsPlus(List<Long> scrollsA, List<Long> scrollsB) {
        return Utils.zip(scrollsA, scrollsB, (a, b) -> a + b);
    }

    /**
     * Вычитает данные скроллов.
     */
    public List<Long> scrollsMinus(List<Long> scrollsA, List<Long> scrollsB) {
        return Utils.zip(scrollsA, scrollsB, (a, b) -> a - b);
    }

    /**
     * Складывает данные ссылок. Для каждого ключа, вычисляет список значений суммированием.
     */
    public Map<String, List<Integer>> linksPlus(Map<String, List<Integer>> linksA, Map<String, List<Integer>> linksB) {
        return composeLinks(linksA, linksB, (itemA, itemB) -> itemA + itemB);
    }

    /**
     * Вычитает данные ссылок. Для каждого ключа, вычисляет список значений вычитанием.
     */
    public Map<String, List<Integer>> linksMinus(Map<String, List<Integer>> linksA, Map<String, List<Integer>> linksB) {
        return composeLinks(linksA, linksB, (itemA, itemB) -> itemA - itemB);
    }

    private Map<String, List<Integer>> composeLinks(Map<String, List<Integer>> linksA, Map<String, List<Integer>> linksB, BiFunction<Integer, Integer, Integer> linkItemsFunction) {
        return Utils.zip(linksA, linksB,
                (linkA, linkB) -> Utils.zip(linkA, linkB,
                        linkItemsFunction));
    }

    /**
     * Вычитает фуннели для форм.
     *
     * @param funnelsA список фуннелей с форм одного ответа
     * @param funnelsB список фуннелей с форм другого ответа
     * @return список фуннелей для форм. каждый фуннель - разность двух соответствующих фуннелей
     */
    public List<List<Long>> funnelsMinus(List<List<Long>> funnelsA, List<List<Long>> funnelsB) {
        return composeFunnels(funnelsA, funnelsB, (funnelItemA, funnelItemB) -> funnelItemA - funnelItemB);
    }

    /**
     * Суммирует фуннели для форм.
     *
     * @param funnelsA список фуннелей с форм одного ответа
     * @param funnelsB список фуннелей с форм другого ответа
     * @return список фуннелей для форм. каждый фуннель - сумма двух соответствующих фуннелей
     */

    public List<List<Long>> funnelsPlus(List<List<Long>> funnelsA, List<List<Long>> funnelsB) {
        return composeFunnels(funnelsA, funnelsB, (funnelItemA, funnelItemB) -> funnelItemA + funnelItemB);
    }

    private List<List<Long>> composeFunnels(List<List<Long>> funnelsA, List<List<Long>> funnelsB, BiFunction<Long, Long, Long> itemFunction) {
        return Utils.zip(funnelsA, funnelsB, (funnelA, funnelB) -> Utils.zip(funnelA, funnelB, itemFunction));
    }

    public static <T> T getProperty(Object object, String name) {
        try {
            return (T) PropertyUtils.getProperty(object, name);
        } catch (Throwable e) {
            throw propagate(e);
        }
    }
}
