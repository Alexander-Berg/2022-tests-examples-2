package ru.yandex.autotests.metrika.tests.ft.report.metrika.access;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.StaticParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithViewPermission;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by sonick on 18.12.15.
 * <p>
 * https://st.yandex-team.ru/TESTIRT-7999
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.RANKED_COUNTERS})
@Title("Доступ к блатным счетчикам, позитивные тесты")
@RunWith(Parameterized.class)
public class RankPositiveTests {
    private static final String METRIC = "ym:s:visits";

    private static final User OWNER = USER_DELEGATOR;
    private static final User DELEGATE = USER_DELEGATE_PERMANENT;
    private static final User SUPER = SUPER_USER;
    private static final User GUEST = SIMPLE_USER2;
    private static final User MANAGER_GUEST = MANAGER;
    private static final User MANAGER_DIRECT_GUEST = MANAGER_DIRECT;
    private static final User SUPPORT_GUEST = SUPPORT;

    private static UserSteps user;
    private static UserSteps userOwner;
    private static UserSteps userSuper;

    private static Long counterId;
    private static final Long RANK = 4L;

    @Parameter(0)
    public String title;

    @Parameter(1)
    public User currentUser;

    @Parameters(name = "Доступ: {0}, пользователь: {1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {"владелец", OWNER},
                {"представитель", DELEGATE},
                {"суперпользователь", SUPER},
                {"гостевой доступ", GUEST},
                {"менеджер с гостевым доступом", MANAGER_GUEST},
                {"менеджер-директ с гостевым доступом", MANAGER_DIRECT_GUEST},
                {"саппорт с гостевым доступом", SUPPORT_GUEST},
        });
    }

    @BeforeClass
    public static void init() {
        userOwner = new UserSteps().withDefaultAccuracy().withUser(OWNER);
        userSuper = new UserSteps().withDefaultAccuracy().withUser(SUPER);

        //создать счетчик c заданным доступом
        counterId = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounterWithViewPermission(
                        GUEST, MANAGER_GUEST, MANAGER_DIRECT_GUEST)).getId();

        userOwner.onManagementSteps().onGrantsSteps()
                .setGrantAndExpectSuccess(counterId,
                        new GrantE().withUserLogin(SUPPORT_GUEST.toString()).withPerm(GrantType.VIEW), ignoreQuota(true));

        //изменить ранг счетчика
        userSuper.onManagementSteps().onCountersSteps().setRankAndExpectSuccess(counterId, RANK);
        Long actualRank = userOwner.onManagementSteps().onCountersSteps().getRankAndExpectSuccess(counterId);
        assumeThat("ранг счетчика изменился верно", actualRank, equalTo(RANK));
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy().withUser(currentUser);
    }

    @Test
    public void accessUserSuccess() {
        user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withId(counterId)
                        .withMetric(METRIC));
    }

    @AfterClass
    public static void cleanup() {
        //удалить счетчик
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
