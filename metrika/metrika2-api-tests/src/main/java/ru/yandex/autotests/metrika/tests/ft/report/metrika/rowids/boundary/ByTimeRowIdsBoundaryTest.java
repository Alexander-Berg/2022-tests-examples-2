package ru.yandex.autotests.metrika.tests.ft.report.metrika.rowids.boundary;

import ch.lambdaj.Lambda;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.List;
import java.util.stream.IntStream;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by okunev on 30.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.ROW_IDS})
@Title("Отчет 'по времени': выбор строк: проверка граничных значений")
public class ByTimeRowIdsBoundaryTest {

    private static final String METRIC = "ym:s:users";
    private static final String DIMENSIONS = "ym:s:startURL,ym:s:endURL";
    private static final int DIMENSIONS_COUNT = DIMENSIONS.split(",").length;
    private static final String DATE1 = "2014-09-01";
    private static final String DATE2 = "2014-09-07";
    private static final int ROW_IDS_MINIMUM = 1;
    private static final int ROW_IDS_MAXIMUM = 100;

    private static UserSteps user;
    private static final Counter counter = CounterConstants.NO_DATA;

    private BytimeReportParameters reportParameters;
    private List<List<Integer>> rowIds;

    @BeforeClass
    public static void beforeClass() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void before() {
        reportParameters = new BytimeReportParameters()
                .withId(counter.get(ID))
                .withMetric(METRIC)
                .withDimension(DIMENSIONS)
                .withDate1(DATE1)
                .withDate2(DATE2);

        rowIds = IntStream.range(0, ROW_IDS_MAXIMUM + 1).boxed().map(Arrays::asList).collect(toList());
    }

    @Test
    public void bytimeRowidsCheckMinimumPositive() {
        reportParameters.setRowIds(rowIds.subList(0, ROW_IDS_MINIMUM));

        user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void bytimeRowidsCheckMinimumAllDimensionsPositive() {
        reportParameters.setRowIds(asList(Lambda.<String>flatten(rowIds).subList(0, DIMENSIONS_COUNT)));

        user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void bytimeRowidsCheckMinimumNegative() {
        reportParameters.setRowIds(asList(Lambda.<String>flatten(rowIds).subList(0, DIMENSIONS_COUNT + 1)));

        user.onReportSteps().getBytimeReportAndExpectError(
                ReportError.TOO_MANY_DIMENSIONS_IN_ROW_IDS,
                reportParameters);
    }

    @Test
    public void bytimeRowidsCheckMaximumNegative() {
        reportParameters.setRowIds(rowIds);

        user.onReportSteps().getBytimeReportAndExpectError(
                ReportError.TOO_MANY_KEYS_IN_ROW_IDS,
                reportParameters);
    }

    @Test
    public void bytimeRowidsCheckMaximumPositive() {
        reportParameters.setRowIds(rowIds.subList(0, ROW_IDS_MAXIMUM));

        user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }

}
