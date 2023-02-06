package ru.yandex.autotests.metrika.tests.ft.report.metrika.parametrization;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;

/**
 * Created by konkov on 28.11.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.PARAMETRIZATION})
@Title("Параметризация с одним параметром")
@RunWith(Parameterized.class)
public class ParametrizationSingleParameterTest extends ParametrizationBaseTest {

    private static final String DIMENSION = "ym:s:browser";
    private static final String METRIC = "ym:s:users";
    private static final String PARAM_DIM = "ym:s:goal<goal_id>IsReached";
    private static final String PARAM_METRIC = "ym:s:goal<goal_id>reaches";

    @Parameterized.Parameters(name = "{2} {3} {4}")
    public static Collection createParameters() {
        return asList(new Object[][]{
                {PARAM_DIM, METRIC, PARAM_DIM, GOAL_ID, EMPTY},
                {PARAM_DIM, METRIC, PARAM_DIM, EMPTY, GOAL_ID},
                {DIMENSION, PARAM_METRIC, PARAM_METRIC, GOAL_ID, EMPTY},
                {DIMENSION, PARAM_METRIC, PARAM_METRIC, EMPTY, GOAL_ID},
        });
    }
}
