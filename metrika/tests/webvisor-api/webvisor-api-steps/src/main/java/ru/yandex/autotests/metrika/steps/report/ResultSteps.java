package ru.yandex.autotests.metrika.steps.report;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.BiFunction;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import com.google.common.collect.Sets;
import org.apache.commons.collections4.functors.EqualPredicate;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.poi.ss.usermodel.Row;
import org.hamcrest.Matcher;

import ru.yandex.autotests.httpclient.lite.core.steps.BackEndBaseSteps;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataClickGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataFormGETPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkMapGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataScrollGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataHitsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
import ru.yandex.autotests.metrika.converters.CollectionToClicksConverter;
import ru.yandex.autotests.metrika.data.inpage.Click;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiException;
import ru.yandex.autotests.metrika.matchers.PairResponseMatcher;
import ru.yandex.autotests.metrika.utils.Utils;
import ru.yandex.metrika.api.constructor.response.QueryExternal;
import ru.yandex.metrika.ui.maps.external.ActivityPageReportExternalInnerForm;
import ru.yandex.metrika.ui.maps.external.ActivityPageReportExternalInnerInputKeyExternal;
import ru.yandex.metrika.ui.maps.external.UrlWrapper;

import static ch.lambdaj.Lambda.flatten;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.collections4.ListUtils.indexOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.areBothSuccessful;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.isSimilarErrorCode;
import static ru.yandex.autotests.metrika.converters.CSVRecordToListConverter.csvToList;
import static ru.yandex.autotests.metrika.converters.CSVRecordToStringListConverter.csvToStringList;
import static ru.yandex.autotests.metrika.converters.CellIteratorToListConverter.cellToList;
import static ru.yandex.autotests.metrika.converters.CellIteratorToStringListConverter.cellToStringList;
import static ru.yandex.autotests.metrika.converters.DimensionToHumanReadableStringMapper.dimensionToHumanReadableStringMapper;
import static ru.yandex.autotests.metrika.matchers.ReportDataMatcher.expectNotEmptyReport;
import static ru.yandex.autotests.metrika.matchers.inpage.InpageNotEmptyMatchers.getNotEmptyInpageMatcher;
import static ru.yandex.autotests.metrika.utils.Utils.getSlice;

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
     * извлечение массива значений заданного измерения из результата запроса
     *
     * @param dimension наименование измерения
     * @param result    результат запроса
     * @return массив строковых представлений значений измерений
     */
    public List<String> getDimensionValues(String dimension, WebvisorV2DataVisitsGETSchema result) {
        int index = getDimensionIndex(result.getQuery(), dimension);

        List<List<String>> allDimensions = result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(Utils::extractStringDimensionValue)
                        .collect(toList()))
                .collect(toList());

        return getSlice(allDimensions, index);
    }

    /**
     * извлечение массива значений заданного измерения из результата запроса
     * для комплексных значений - массивов измерений
     *
     * @param dimension наименование измерения, значение его должно представлять собой массив измерений
     * @param result    результат запроса
     * @return массив, каждый элемент которого массив строковых представлений значений
     */
    public List<List<String>> getComplexDimensionValues(String dimension, WebvisorV2DataVisitsGETSchema result) {
        int index = getDimensionIndex(result.getQuery(), dimension);

        return result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(Utils::extractDimensionValue)
                        .collect(toList()))
                .map(row -> ((List<Map<String, String>>) row.get(index)).stream()
                        .map(Utils::extractStringDimensionValue)
                        .collect(toList()))
                .collect(toList());
    }

    /**
     * извлечение массива значений заданного измерения из результата запроса
     *
     * @param dimension наименование измерения
     * @param result    результат запроса
     * @return массив строковых представлений значений измерений
     */
    public List<String> getDimensionValues(String dimension, WebvisorV2DataHitsGETSchema result) {
        int index = getDimensionIndex(result.getQuery(), dimension);

        List<List<String>> allDimensions = result.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(Utils::extractStringDimensionValue).collect(toList()))
                .collect(toList());

        return getSlice(allDimensions, index);
    }

    /**
     * Преобразует данные кликов в виде массива в данные с объектами кликов
     *
     * @param shippingFirstDayData - исходный результат с кликами в виде списка чисел
     * @return - данные с кликами в виде объектов
     */
    public Map<String, Set<Click>> transformInpageClickData(Map<String, Collection<Integer>> shippingFirstDayData) {
        return shippingFirstDayData.entrySet().stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        e -> Sets.newHashSet(CollectionToClicksConverter.convert(e.getValue()))
                ));
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
     * Получение данных для карты скроллинга
     *
     * @param result схема из которой извлекаются данные
     * @return одномерный массив данных
     */
    public List<Long> getInpageScrollData(MapsV1DataScrollGETSchema result) {
        return result.getData();
    }

    /**
     * Получение хитов для карты скроллинга
     *
     * @param result схема данных из которой извлекаются хиты
     * @return одномерный массив хитов
     */
    public List<Long> getInpageScrollHits(MapsV1DataScrollGETSchema result) {
        return result.getHits();
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
     * Осуществляет проверку ожидания того, что оба ответа inpage содержат непустой отчет
     *
     * @param testingBean   - результат запроса к тестируемой среде
     * @param referenceBean - результат запроса к образцовой среде
     */
    public void assumeInpageReportsNotEmptyBoth(Object testingBean, Object referenceBean){
        Matcher matcher = getNotEmptyInpageMatcher(testingBean);

        TestSteps.assumeThat("оба ответа содержат непустой отчет",
                ImmutablePair.of(referenceBean, testingBean),
                new PairResponseMatcher(matcher, matcher));
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
     * Получение адресов для карты ссылок
     *
     * @param result схема данных из которой извлекаются адреса
     * @return одномерный массив адресов
     */
    public List<String> getInpageUrls(MapsV1DataLinkGETSchema result) {
        return result.getData().stream().map(UrlWrapper::getUrl).collect(toList());
    }

    /**
     * Получение данных для карты кликов
     *
     * @param result схема из которой извлекаются данные
     * @return одномерный массив данных
     */
    public List<List<Integer>> getInpageClickData(MapsV1DataClickGETSchema result) {
        return result.getData().getData().stream()
                .flatMap(mapStream -> mapStream.values().stream())
                .map(c -> c.stream().collect(toList()))
                .collect(toList());
    }

    /**
     * Получение данных для карты кликов за первый день в виде кликов
     * @param result схема, из которой извлекаются данные
     * @return данные за первый день с кликами в виде объектов
     */
    public Map<String, Set<Click>> getInpageClickFirstDayClicks(MapsV1DataClickGETSchema result) {
        return transformInpageClickData(getInpageClickFirstDayData(result));
    }

    /**
     * Получение данных для карты кликов за первый день
     * @param result схема, из которой извлекаются данные
     * @return данные за первый день
     */
    public Map<String, Collection<Integer>> getInpageClickFirstDayData(MapsV1DataClickGETSchema result) {
        TestSteps.assumeThat("ответ содержит непустой отчет", result, getNotEmptyInpageMatcher(result));
        return result.getData().getData().get(0);
    }

    /**
     * Получение "воронок" для аналитики форм
     *
     * @param result схема данных из которой извлекаются "воронки"
     * @return двумерный массив значений "воронок"
     */
    public List<List<Long>> getInpageFormFunnels(MapsV1DataFormGETPOSTSchema result) {
        return with(result.getForms()).extract(on(ActivityPageReportExternalInnerForm.class).getFunnels());
    }

    /**
     * Получение имен полей ввода для аналитики форм
     *
     * @param result схема данных из которой извлекаются имена полей ввода
     * @return одномерный массив имен полей ввода
     */
    public List<String> getInpageFormInputNames(MapsV1DataFormGETPOSTSchema result) {
        return with(flatten(with(result.getForms()).extract(on(ActivityPageReportExternalInnerForm.class).getInputs())))
                .extract(on(ActivityPageReportExternalInnerInputKeyExternal.class).getName());
    }

    /**
     * Получение данных для карты ссылок
     *
     * @param result схема из которой извлекаются данные
     * @return одномерный массив данных
     */
    public List<List<Double>> getInpageLinkData(MapsV1DataLinkMapGETSchema result) {
        return with(result.getData().getL().values()).stream()
                .map(v -> v.stream().map(d -> (double) (int) d).collect(toList())).collect(toList());
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
     * Достает funnel из ответа аналитики форм
     */
    public List<List<Long>> getFormsFunnels(MapsV1DataFormGETPOSTSchema result) {
        return result.getForms().stream().map(ActivityPageReportExternalInnerForm::getFunnels).collect(Collectors.toList());
    }

    /**
     * Вычитает фуннели для форм.
     * @param funnelsA список фуннелей с форм одного ответа
     * @param funnelsB список фуннелей с форм другого ответа
     * @return список фуннелей для форм. каждый фуннель - разность двух соответствующих фуннелей
     */
    public List<List<Long>> funnelsMinus(List<List<Long>> funnelsA, List<List<Long>> funnelsB) {
        return composeFunnels(funnelsA, funnelsB, (funnelItemA, funnelItemB) -> funnelItemA - funnelItemB);
    }

    /**
     * Суммирует фуннели для форм.
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

}
