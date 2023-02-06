package ru.yandex.autotests.metrika.tests.ft.report.metrika.parentids;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataComparisonDrilldownGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonDrilldownReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.ComparisonRowDrillDownAB;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static java.lang.String.format;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_UPLOADINGS;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Parameter.PARENT_ID, Requirements.Story.Report.Type.DRILLDOWN})
@Title("Отчет ComparisonDrilldown, parent_id и expand")
@RunWith(Parameterized.class)
@Issue("METR-24859")
public class ComparisonDrillDownTest {

    private static final Counter COUNTER = TEST_UPLOADINGS;
    private static final String START_DATE = "2017-02-25";
    private static final String END_DATE = "2017-03-24";

    private UserSteps user;

    private ComparisonRowDrillDownAB resultRow;

    @Parameterized.Parameter
    public List<String> dimensions;

    @Parameterized.Parameter(1)
    public List<String> metrics;

    @Parameterized.Parameter(2)
    public List<String> parentIds;

    @Parameterized.Parameter(3)
    public String expandDimensionValue;

    @Parameterized.Parameter(4)
    public Boolean expand;

    @Parameterized.Parameters(name = "parent_id={2}")
    public static Collection<Object[]> createParameters() {
        return of(toArray(
                of(
                        "ym:s:offlineCallTag",
                        "ym:s:offlineCallFirstTimeCaller",
                        "ym:s:offlineCallMissed"
                ),
                of(
                        "ym:s:visits",
                        "ym:s:offlineCalls",
                        "ym:s:offlineCallsFirstTimeCallerPercentage"
                ),
                of(
                        "Calluser",
                        "no"
                ),
                "Пропущенный",
                false
        ));
    }

    @Before
    public void setup() {
        user = new UserSteps();

        StatV1DataComparisonDrilldownGETSchema result = user.onReportSteps()
                .getComparisonDrilldownReportAndExpectSuccess(new ComparisonDrilldownReportParameters()
                        .withId(COUNTER)
                        .withDimensions(dimensions)
                        .withMetrics(metrics)
                        .withDate1_a(START_DATE)
                        .withDate2_a(END_DATE)
                        .withDate1_b(START_DATE)
                        .withDate2_b(END_DATE)
                        .withParentIds(parentIds)
                        .withAccuracy("high"));

        resultRow = user.onResultSteps().findRow(result, expandDimensionValue);
    }

    @Test
    public void checkExpand() {
        assertThat(format("дочерние записи %sприсутствуют", expand ? "" : "не "),
                resultRow.getExpand(),
                equalTo(expand));
    }
}
