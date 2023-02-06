package ru.yandex.autotests.metrika.tests.ft.report.metrika.access;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;

/**
 * Created by konkov on 14.10.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Parameter.IDS})
@Title("Авторизация по ids")
public class IdsAuthorizationTest {
    private static final Counter publicCounter = METRIKA_DEMO;
    private static final Counter ownCounter = YANDEX_BY_TESTER;
    private static final Counter accessibleCounter = TEST_COUNTER;
    private static final Counter privateCounter = KVAZI_KAZINO;

    private static final UserSteps user = new UserSteps().withDefaultAccuracy().withUser(SIMPLE_USER);

    private static final String METRIC_NAME = "ym:s:visits";
    private static final String START_DATE = "2015-09-01";
    private static final String END_DATE = "2015-09-01";

    @Test
    public void accessGrantedTest() {
        user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withIds(asList(publicCounter, ownCounter, accessibleCounter))
                        .withMetric(METRIC_NAME)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE));
    }

    @Test
    public void accessDeniedTest() {
        user.onReportSteps().getTableReportAndExpectError(
                ACCESS_DENIED,
                new TableReportParameters()
                        .withIds(asList(publicCounter, ownCounter, accessibleCounter, privateCounter))
                        .withMetric(METRIC_NAME)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE));
    }
}
