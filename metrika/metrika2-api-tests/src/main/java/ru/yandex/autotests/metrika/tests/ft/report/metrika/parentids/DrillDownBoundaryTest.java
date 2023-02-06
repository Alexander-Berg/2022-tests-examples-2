package ru.yandex.autotests.metrika.tests.ft.report.metrika.parentids;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.DrillDownRow;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.core.Every.everyItem;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 21.10.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.DRILLDOWN)
@Title("Ограничения в отчете Drilldown")
public class DrillDownBoundaryTest {

    private static final Counter counter = CounterConstants.NO_DATA;
    public static final String ERROR_MESSAGE_TEMPLATE = "Row id size equals to dimensions size: %s";
    private static final int KEYS_LIMIT = 10;
    private static final int PARENT_IDS_LIMIT = KEYS_LIMIT - 1;
    private static final String METRIC_NAME = "ym:s:users";
    private static UserSteps user;

    private static List<String> dimensions = asList(
            "ym:s:startURLPath",
            "ym:s:startURLPathLevel1",
            "ym:s:startURLPathLevel2",
            "ym:s:startURLPathLevel3",
            "ym:s:startURLPathLevel4",
            "ym:s:startURLPathLevel5",
            "ym:s:endURLPath",
            "ym:s:endURLPathLevel1",
            "ym:s:endURLPathLevel2",
            "ym:s:endURLPathLevel3",
            "ym:s:endURLPathLevel4",
            "ym:s:endURLPathLevel5"
    );

    private DrillDownReportParameters reportParameters;

    private static List<String> getParentIds(int length) {
        List<String> parentIds = new ArrayList<>();

        for (int i = 0; i < length; i++) {
            parentIds.add(String.format("A%s", i));
        }

        return parentIds;
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new DrillDownReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setLimit(1);
        reportParameters.setMetric(METRIC_NAME);
    }

    @Test
    public void checkMaximumAllowedParentList() {

        reportParameters.setDimensions(dimensions.subList(0, KEYS_LIMIT));
        reportParameters.setParentIds(getParentIds(PARENT_IDS_LIMIT));

        user.onReportSteps().getDrilldownReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void checkMoreThanLongestParentList() {

        reportParameters.setDimensions(dimensions.subList(0, KEYS_LIMIT));
        reportParameters.setParentIds(getParentIds(PARENT_IDS_LIMIT + 1));

        user.onReportSteps().getDrilldownReportAndExpectError(
                400L, String.format(ERROR_MESSAGE_TEMPLATE, KEYS_LIMIT),
                reportParameters);
    }

    @Test
    public void checkLongestParentList() {

        int dimensionNumber = KEYS_LIMIT / 2;

        reportParameters.setDimensions(dimensions.subList(0, dimensionNumber));
        reportParameters.setParentIds(getParentIds(dimensionNumber - 1));

        user.onReportSteps().getDrilldownReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void checkParentListLongAsDimensionList() {

        int dimensionNumber = KEYS_LIMIT / 2;

        reportParameters.setDimensions(dimensions.subList(0, dimensionNumber));
        reportParameters.setParentIds(getParentIds(dimensionNumber));

        user.onReportSteps().getDrilldownReportAndExpectError(
                400L, String.format(ERROR_MESSAGE_TEMPLATE, dimensionNumber),
                reportParameters);
    }

    @Test
    public void checkParentListLongerThanDimensionList() {

        int dimensionNumber = KEYS_LIMIT / 2;

        reportParameters.setDimensions(dimensions.subList(0, dimensionNumber));
        reportParameters.setParentIds(getParentIds(dimensionNumber + 1));

        user.onReportSteps().getDrilldownReportAndExpectError(
                400L, String.format("Wrong parameter: 'parent_id', value: '%s', message: Too many elements",
                        reportParameters.getParentId()),
                reportParameters);
    }

    @Test
    public void checkOneDimension() {

        reportParameters.setDimensions(dimensions.subList(0, 1));
        reportParameters.setParentIds(getParentIds(0));

        StatV1DataDrilldownGETSchema result =
                user.onReportSteps().getDrilldownReportAndExpectSuccess(reportParameters);

        assertThat("нельзя получить следующий уровень дерева", result.getData(),
                everyItem(having(on(DrillDownRow.class).getExpand(), equalTo(false))));
    }

}
