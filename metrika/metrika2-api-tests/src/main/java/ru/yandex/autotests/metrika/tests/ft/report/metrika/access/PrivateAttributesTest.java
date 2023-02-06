package ru.yandex.autotests.metrika.tests.ft.report.metrika.access;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.errors.ReportError.RESTRICTED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterName;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterSite;
import static ru.yandex.metrika.api.management.client.external.GrantType.PUBLIC_STAT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Created by konkov on 22.01.2015.
 * <p/>
 * https://st.yandex-team.ru/TESTIRT-4020
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.ATTRIBUTES_ACCESS})
@Title("Тесты на ограничение доступа к метрикам/измерениям")
public class PrivateAttributesTest {

    private static final String METRIC = "ym:s:users";
    private static final String RESTRICTED_DIMENSION = "ym:s:directClickBanner";

    /**
     * владелец счетчика
     */
    private static final User OWNER = USER_DELEGATOR;

    /**
     * представитель владельца счетчика
     */
    private static final User DELEGATE = USER_DELEGATE_PERMANENT;

    /**
     * пользователь с гостевым доступом
     */
    private static final User GUEST = SIMPLE_USER2;

    /**
     * иной залогиненный пользователь
     */
    private static final User OTHER = SIMPLE_USER;

    private static UserSteps userOwner;
    private static UserSteps userDelegate;
    private static UserSteps userGuest;
    private static UserSteps userOther;

    private static Long counterId;

    @BeforeClass
    public static void init() {
        userOwner = new UserSteps().withDefaultAccuracy().withUser(OWNER);
        userDelegate = new UserSteps().withDefaultAccuracy().withUser(DELEGATE);
        userGuest = new UserSteps().withDefaultAccuracy().withUser(GUEST);
        userOther = new UserSteps().withDefaultAccuracy().withUser(OTHER);

        //создать счетчик c заданным доступом
        counterId = userOwner.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getCounter()).getId();
    }

    private static CounterFull getCounter() {
        return new CounterFull()
                .withName(getCounterName())
                .withSite(getCounterSite())
                .withGrants(asList(
                        new GrantE()
                                .withUserLogin(GUEST.get(LOGIN))
                                .withPerm(VIEW),
                        new GrantE()
                                .withUserLogin(EMPTY)
                                .withPerm(PUBLIC_STAT)
                ));
    }

    private static IFormParameters getReportParameters() {
        TableReportParameters reportParameters = new TableReportParameters();

        reportParameters.setId(counterId);
        reportParameters.setDimension(RESTRICTED_DIMENSION);
        reportParameters.setMetric(METRIC);

        return reportParameters;
    }

    @Test
    @Title("Доступ владельца счетчика")
    public void accessOwner() {
        userOwner.onReportSteps().getTableReportAndExpectSuccess(getReportParameters());
    }

    @Test
    @Title("Доступ представителя владельца счетчика")
    public void accessOwnersDelegate() {
        userDelegate.onReportSteps().getTableReportAndExpectSuccess(getReportParameters(), ulogin(OWNER.get(LOGIN)));
    }

    @Test
    @Title("Гостевой доступ")
    public void accessGuest() {
        userGuest.onReportSteps().getTableReportAndExpectSuccess(getReportParameters());
    }

    @Test
    @Title("Доступ иного пользователя")
    public void accessOther() {
        userOther.onReportSteps()
                .getTableReportAndExpectError(RESTRICTED, getReportParameters());
    }

    @AfterClass
    public static void cleanup() {
        //удалить счетчик
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
