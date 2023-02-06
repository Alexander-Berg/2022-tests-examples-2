package ru.yandex.autotests.metrika.tests.ft.report.metrika.abexperiment;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.StaticRow;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.REFERENCE_ROW_ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.DIRECT;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ExperimentParameters.experimentId;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ReferenceRowIdParameters.referenceRowId;

@Features({Requirements.Feature.REPORT})
@Stories({Requirements.Story.Report.Type.TABLE})
@Title("Отчет 'таблица': сравнение эксперимента с эталоном; ошибки extendedMetrics")
public class ABExperimentErrorsTest {
    private static final Counter COUNTER = DIRECT;
    private static final UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final String DIMENSION_EXPERIMENTS = "ym:s:experimentAB<experiment_ab>";
    private final Double ALPHA_BOUNCES = 1.5;
    private final Double ALPHA_GOALS = 1.;
    private final Double ALPHA_VISITS = 1.2;
    private List<StaticRow> data;

    @Before
    public void before() {
        IFormParameters parameters = FreeFormParameters.makeParameters()
                .append(new TableReportParameters()
                        .withDimension(DIMENSION_EXPERIMENTS)
                        .withId(COUNTER.getId())
                        .withMetrics(asList(
                                "ym:s:users",
                                "ym:s:visits",
                                "ym:s:goal<goal_id>bounces",
                                "ym:s:goal<goal_id>visits",
                                "ym:s:goal<goal_id>users",
                                "ym:s:goal<goal_id>bounceRate",
                                "ym:s:pageDepth",
                                "ym:s:goal<goal_id>conversionRate")))
                .append(experimentId(COUNTER))
                .append(goalId(COUNTER))
                .append(referenceRowId(COUNTER.get(REFERENCE_ROW_ID)));
        data = user.onReportSteps().getTableReportAndExpectSuccess(parameters).getData();
    }

    @Test
    public void testExperimentHasReferenceRow() {
        assertThat(data, hasItem(
                allOf(
                        hasProperty("extendedMetrics", empty()),
                        hasProperty("dimensions", everyItem(hasEntry(is("id"), isIn(COUNTER.get(REFERENCE_ROW_ID)))))
                )
        ));
    }

    @Test
    public void testCorrectErrors() {
        final int visitsIndex = 1;
        final int bouncesByGoalIndex = 2;
        final int visitsByGoalIndex = 3;
        final int bounceRateByGoalIndex = 5;
        final int conversionRateByGoalIndex = 7;
        int referencePosition = -1;
        for (int i = 0; i < data.size(); i++) {
            if (data.get(i).getExtendedMetrics() == null || data.get(i).getExtendedMetrics().isEmpty()) {
                referencePosition = i;
                break;
            }
        }
        StaticRow referenceRow = data.get(referencePosition);
        for (int i = 0; i < data.size(); i++) {
            if (i != referencePosition) {
                StaticRow row = data.get(i);
                assertThat("Ошибка ym:s:goal<goal_id>conversionRate считается по ym:s:goal<goal_id>visits",
                        ALPHA_GOALS * Math.sqrt(1 / row.getMetrics().get(visitsByGoalIndex) + 1 / referenceRow.getMetrics().get(visitsByGoalIndex)),
                        closeTo(row.getExtendedMetrics().get(conversionRateByGoalIndex).getError(), 0.0000001));
                assertThat("Ошибка ym:s:goal<goal_id>bounceRate считается по ym:s:goal<goal_id>bounces",
                        ALPHA_BOUNCES * Math.sqrt(1 / row.getMetrics().get(bouncesByGoalIndex) + 1 / referenceRow.getMetrics().get(bouncesByGoalIndex)),
                        closeTo(row.getExtendedMetrics().get(bounceRateByGoalIndex).getError(), 0.0000001));
                assertThat("Ошибка ym:s:visits считается по себе",
                        ALPHA_VISITS * Math.sqrt(1 / row.getMetrics().get(visitsIndex) + 1 / referenceRow.getMetrics().get(visitsIndex)),
                        closeTo(row.getExtendedMetrics().get(visitsIndex).getError(), 0.0000001));
            }
        }
    }
}
