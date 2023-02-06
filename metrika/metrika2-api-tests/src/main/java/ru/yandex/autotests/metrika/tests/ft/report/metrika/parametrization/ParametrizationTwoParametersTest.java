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
@Title("Параметризация с двумя параметрами")
@RunWith(Parameterized.class)
public class ParametrizationTwoParametersTest extends ParametrizationBaseTest {

    private static final String DIMENSION = "ym:s:browser";
    private static final String METRIC = "ym:s:goal<goal_id>converted<currency>Revenue";

    @Parameterized.Parameters(name = "{2} {3} {4}")
    public static Collection createParameters() {
        return asList(new Object[][]{
                {DIMENSION, METRIC, METRIC, GOAL_ID_AND_CURRENCY, EMPTY},
                {DIMENSION, METRIC, METRIC, GOAL_ID, CURRENCY},
                {DIMENSION, METRIC, METRIC, CURRENCY, GOAL_ID},
                {DIMENSION, METRIC, METRIC, EMPTY, GOAL_ID_AND_CURRENCY},
        });
    }
}
