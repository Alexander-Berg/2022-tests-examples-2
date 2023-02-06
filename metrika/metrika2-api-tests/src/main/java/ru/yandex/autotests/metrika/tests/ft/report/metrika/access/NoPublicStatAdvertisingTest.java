package ru.yandex.autotests.metrika.tests.ft.report.metrika.access;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithPublicStatPermission;

/**
 * Created by konkov on 28.07.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.ADVERTISING})
@Title("Недоступность отчетов по кликам Директа при публичном доступе на счетчик")
public class NoPublicStatAdvertisingTest {

    private UserSteps userOwner;
    private UserSteps user;

    private static final Counter COUNTER = SENDFLOWERS_RU;

    private static final String DIMENSION_NAME = "ym:ad:directBannerGroup";
    private static final String METRIC_NAME = "ym:ad:clicks";
    private static final String START_DATE = DateConstants.Advertising.START_DATE;
    private static final String END_DATE = DateConstants.Advertising.END_DATE;

    private Long counterId;
    private List<String> clientLogins;

    @Before
    public void setup() {
        userOwner = new UserSteps().withDefaultAccuracy();
        user = new UserSteps().withDefaultAccuracy().withUser(SIMPLE_USER);

        counterId = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounterWithPublicStatPermission()).getId();

        clientLogins = userOwner.onManagementSteps().onClientSteps().getClientLogins(
                new ClientsParameters()
                        .withCounters(COUNTER.get(ID))
                        .withDate1(START_DATE)
                        .withDate2(END_DATE),
                ulogin(COUNTER.get(U_LOGIN)));
    }

    @Test
    public void noAdvertisingReportWithPublicStatTest() {
        user.onReportSteps().getTableReportAndExpectError(
                ACCESS_DENIED,
                new TableReportParameters()
                        .withId(counterId)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withDirectClientLogins(clientLogins));
    }

    @After
    public void teardown() {
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
