package ru.yandex.autotests.metrika.tests.ft.report.metrika.rowids;

import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 11.11.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.ROW_IDS})
@Title("Отчет 'по времени': выбор строк: проверка с фильтром эквивалентным row_ids")
public class ByTimeRowIdsFilterTest {

    private static final String METRIC = "ym:s:visits";
    private static final String DIMENSION = "ym:s:minute";
    private static final String START_DATE = "2015-09-01";
    private static final String END_DATE = "2015-09-02";

    private static UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final Counter COUNTER = YANDEX_METRIKA_2_0;

    private String rowId;

    @Before
    public void before() {
        StatV1DataBytimeGETSchema result = user.onReportSteps()
                .getBytimeReportAndExpectSuccess(
                        new BytimeReportParameters()
                                .withId(COUNTER.get(ID))
                                .withMetric(METRIC)
                                .withDimension(DIMENSION)
                                .withDate1(START_DATE)
                                .withDate2(END_DATE));

        rowId = user.onResultSteps().getDimensions(result).get(0).get(0);
    }

    @Test
    public void bytimeRowidsCheckRowsWithFilter() {

        StatV1DataBytimeGETSchema result = user.onReportSteps()
                .getBytimeReportAndExpectSuccess(
                        new BytimeReportParameters()
                                .withId(COUNTER.get(ID))
                                .withMetric(METRIC)
                                .withDimension(DIMENSION)
                                .withRowIds(asList(asList(rowId)))
                                .withFilters(dimension(DIMENSION).equalTo(rowId).build())
                                .withDate1(START_DATE)
                                .withDate2(END_DATE));

        List<List<String>> dimensionsActual = user.onResultSteps().getDimensions(result);

        assertThat("результат содержит указанные строки", dimensionsActual,
                both(iterableWithSize(1)).and(Matchers.<Iterable>equalTo(asList(asList(rowId)))));
    }
}
