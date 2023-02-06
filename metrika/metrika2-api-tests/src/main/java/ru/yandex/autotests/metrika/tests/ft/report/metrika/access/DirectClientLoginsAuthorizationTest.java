package ru.yandex.autotests.metrika.tests.ft.report.metrika.access;

import java.util.List;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.errors.ManagementError.USER_NOT_FOUND_RU;
import static ru.yandex.autotests.metrika.errors.ReportError.DIRECT_CLIENT_LOGINS;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 28.07.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.DIRECT_CLIENT_LOGINS_AUTHORIZATION,
        Requirements.Story.Report.Parameter.DIRECT_CLIENT_LOGINS
})
@Title("Авторизация по direct_client_logins")
public class DirectClientLoginsAuthorizationTest {

    private UserSteps user;

    private static final Counter ACCESSIBLE_COUNTER = SENDFLOWERS_RU;
    private static final String DIMENSION_NAME = "ym:ad:gender";
    private static final String METRIC_NAME = "ym:ad:clicks";
    private static final String START_DATE = DateConstants.Advertising.START_DATE;
    private static final String END_DATE = DateConstants.Advertising.END_DATE;

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Test
    @Title("Доступный direct_client_logins")
    public void checkAccessibleDirectClientLoginsTest() {
        List<String> clientLogins = user.onManagementSteps().onClientSteps().getClientLogins(
                new ClientsParameters()
                        .withCounters(ACCESSIBLE_COUNTER.get(ID))
                        .withDate1(START_DATE)
                        .withDate2(END_DATE),
                ulogin(ACCESSIBLE_COUNTER.get(U_LOGIN)));

        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withId(ACCESSIBLE_COUNTER.get(ID))
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                        .withDirectClientLogins(clientLogins));

        assertThat("данные в отчете присутствуют", result.getData(), iterableWithSize(greaterThan(0)));
    }

    @Test
    @Title("Без direct_client_logins")
    public void checkWithoutDirectClientLoginsTest() {
        user.onReportSteps().getTableReportAndExpectError(
                DIRECT_CLIENT_LOGINS,
                new TableReportParameters()
                        .withId(ACCESSIBLE_COUNTER.get(ID))
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE));
    }

    @Test
    @Title("Несуществующий direct_client_logins")
    public void checkNotExistantDirectClientLoginsTest() {
        user.onReportSteps().getTableReportAndExpectError(
                USER_NOT_FOUND_RU,
                new TableReportParameters()
                        .withId(ACCESSIBLE_COUNTER.get(ID))
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                        .withDirectClientLogins(asList("1")));
    }
}
