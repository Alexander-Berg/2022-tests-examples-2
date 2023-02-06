package ru.yandex.autotests.metrika.tests.ft.report.analytics.filters;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 31.03.2016.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры (google analytics): логические операторы для измерений")
@RunWith(Parameterized.class)
public class AnalyticsFilterSyntaxLogicOperatorsTest extends AnalyticsFilterSyntaxBaseTest {
    private final static String DIMENSION_COUNTRY = "ga:country";
    private final static String DIMENSION_REFERAL = "ga:referralPath";
    private final static String METRIC = "ga:pageviews";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_COUNTRY, METRIC,
                        dimension(DIMENSION_COUNTRY).equalTo("Russia")
                                .and(dimension(DIMENSION_REFERAL).equalTo("/"))},
                {DIMENSION_COUNTRY, METRIC,
                        dimension(DIMENSION_COUNTRY).equalTo("Russia")
                                .or(dimension(DIMENSION_REFERAL).equalTo("/"))},

                {DIMENSION_COUNTRY, METRIC,
                        dimension(DIMENSION_COUNTRY).equalTo("Ukraine")
                                .or(dimension(DIMENSION_COUNTRY).equalTo("Russia")
                                .and(dimension(DIMENSION_COUNTRY).equalTo("Finland")))}


        });
    }
}
