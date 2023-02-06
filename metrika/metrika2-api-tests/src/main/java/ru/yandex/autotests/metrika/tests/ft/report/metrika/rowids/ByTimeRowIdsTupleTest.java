package ru.yandex.autotests.metrika.tests.ft.report.metrika.rowids;

import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.List;

import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by orantius on 12.12.16.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.ROW_IDS})
@Title("Отчет 'по времени': выбор строк: проверка получения строки по корректному id с участием измерений, тип значений которых является туплом")
public class ByTimeRowIdsTupleTest {
    /**
     * оказывается, проблема воспроизводится не в любом отчете: например, на счетчике метрики
     * или без фильтра для row_ids запрос не оптимизируется в неправильный и отчет работает.
     * но на примере из METRIKASUPP-7620 не поправленная версия апи падает.
     */
    private static final String METRIC = "ym:s:visits";
    private static final List<String> DIMENSIONS = Arrays.asList("ym:s:lastSourceEngine", "ym:s:lastUTMSource");
    private static final Counter COUNTER = Counters.HUBHOST;

    private static UserSteps user;
    private StatV1DataBytimeGETSchema result;
    private List<List<String>> dimensionsExpected;


    @Before
    public void before() {
        user = new UserSteps().withDefaultAccuracy();
        BytimeReportParameters reportParameters = new BytimeReportParameters()
                .withId(COUNTER)
                .withDate1("2016-12-01")
                .withDate2("2016-12-10")
                .withMetric(METRIC)
                .withDimensions(DIMENSIONS)
                .withFilters(dimension("ym:s:lastUTMSource").defined().build())
                .withLimit(10);

        StatV1DataGETSchema table = user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
        dimensionsExpected = user.onResultSteps().getDimensions(table);

        reportParameters.setRowIds(dimensionsExpected);

        result = user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void bytimeRowidsCheckRows() {
        List<List<String>> dimensionsActual = user.onResultSteps().getDimensions(result);

        assertThat("результат содержит указанные строки", dimensionsActual,
                Matchers.<Iterable>equalTo(dimensionsExpected));
    }

}
