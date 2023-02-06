package ru.yandex.autotests.metrika.tests.ft.report.metrika.activity;

import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataVisitsByProtocolGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.parameters.report.v1.VisitsByProtocolParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.lessThan;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.JEELEX_MOSCOW;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features({Requirements.Feature.REPORT})
@Stories({Requirements.Story.Report.QUERY})
@Title("Получение статистики визитов по http и https")
@RunWith(Parameterized.class)
public class VisitsByProtocolTest {

    private final UserSteps user = new UserSteps().withDefaultAccuracy();

    @Parameterized.Parameter()
    public String title;

    @Parameterized.Parameter(1)
    public long counterId;

    @Parameterized.Parameter(2)
    public boolean withRobots;

    @Parameterized.Parameter(3)
    public boolean moreHttps;

    @Parameterized.Parameters(name = "Счетчик: {0}, id: {1}, роботы: {2}, https больше http: {3}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(YANDEX_METRIKA_2_0.toString(), YANDEX_METRIKA_2_0.getId(), false, true),
                        of(YANDEX_METRIKA_2_0.toString(), YANDEX_METRIKA_2_0.getId(), true, true),
                        of(JEELEX_MOSCOW.toString(), JEELEX_MOSCOW.getId(), false, false),
                        of(JEELEX_MOSCOW.toString(), JEELEX_MOSCOW.getId(), true, false))
                .build();
    }

    @Test
    public void checkVisitsByProtokol() {
        VisitsByProtocolParameters params = new VisitsByProtocolParameters(counterId, withRobots);
        StatV1DataVisitsByProtocolGETSchema result = user.onReportSteps().getVisitsByProtocolAndExpectSuccess(params);
        if (moreHttps)
            assertThat("https больше, чем http", result.getHttpsVisits(), greaterThan(result.getHttpVisits()));
        else
            assertThat("https меньше, чем http", result.getHttpsVisits(), lessThan(result.getHttpVisits()));

    }
}
