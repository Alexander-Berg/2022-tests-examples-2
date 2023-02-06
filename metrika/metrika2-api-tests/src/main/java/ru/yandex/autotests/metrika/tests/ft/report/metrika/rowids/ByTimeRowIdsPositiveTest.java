package ru.yandex.autotests.metrika.tests.ft.report.metrika.rowids;

import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.BeforeClass;
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

import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by okunev on 30.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.ROW_IDS})
@Title("Отчет 'по времени': выбор строк: проверка получения строки по корректному id")
public class ByTimeRowIdsPositiveTest {

    private static final String METRIC = "ym:s:users";
    private static final String DIMENSION = "ym:s:minute";
    private static final int ROWS_COUNT = 2;

    private static UserSteps user;
    private static final Counter counter = YANDEX_METRIKA_2_0;

    private StatV1DataBytimeGETSchema result;
    private List<List<String>> dimensionsExpected;

    @BeforeClass
    public static void beforeClass() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void before() {
        BytimeReportParameters reportParameters = new BytimeReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setMetric(METRIC);
        reportParameters.setDimension(DIMENSION);

        result = user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
        dimensionsExpected = user.onResultSteps().getDimensions(result).subList(0, ROWS_COUNT);

        reportParameters.setRowIds(dimensionsExpected);

        result = user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void bytimeRowidsCheckRows() {
        List<List<String>> dimensionsActual = user.onResultSteps().getDimensions(result);

        assertThat("результат содержит указанные строки", dimensionsActual,
                both(iterableWithSize(ROWS_COUNT)).and(Matchers.<Iterable>equalTo(dimensionsExpected)));
    }

}
