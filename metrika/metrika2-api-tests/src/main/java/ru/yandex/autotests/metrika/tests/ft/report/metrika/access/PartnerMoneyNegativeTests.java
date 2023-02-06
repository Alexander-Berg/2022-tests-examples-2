package ru.yandex.autotests.metrika.tests.ft.report.metrika.access;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Collections;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.PARTNER_TEST_2;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.METRIKA_TEST_COUNTERS;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_GRANTEE;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.errors.ManagementError.NO_ACCESS_TO_ATTRIBUTE;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.yan;

@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.PARTNER_MONEY})
@Title("Доступ к отчетам по данным РСЯ (негативные тесты)")
@RunWith(Parameterized.class)
public class PartnerMoneyNegativeTests {

    private static final User OWNER = METRIKA_TEST_COUNTERS;
    private static final User GUEST_VIEW = USER_GRANTEE;

    private static final Long COUNTER_ID = PARTNER_TEST_2.getId();

    protected static final UserSteps userTest = new UserSteps().withDefaultAccuracy();

    private static UserSteps user;
    private static UserSteps userOwner;
    private static CounterFull counter;

    @Parameterized.Parameter(0)
    public String title;
    @Parameterized.Parameter(1)
    public User currentUser;
    @Parameterized.Parameter(2)
    public String metricName;
    @Parameterized.Parameters(name = "Доступ: {0}, пользователь: {1}, метрика {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of("гостевой доступ на чтение", GUEST_VIEW))
                .values(userTest.onMetadataSteps().getMetrics(yan()))
                .build();
    }

    @BeforeClass
    public static void init() {
        userOwner = new UserSteps().withDefaultAccuracy().withUser(OWNER);

        counter = userOwner.onManagementSteps().onCountersSteps().getCounterInfo(COUNTER_ID);
        counter.withGrants(Collections.singletonList(
                new GrantE().withUserLogin(GUEST_VIEW.get(LOGIN)).withPerm(GrantType.VIEW).withPartnerDataAccess(false)
        ));
        userOwner.onManagementSteps().onCountersSteps().editCounter(COUNTER_ID, counter, ignoreQuota(true));
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy().withUser(currentUser);
    }

    @Test
    public void accessUserFail() {
        user.onReportSteps().getTableReportAndExpectError(
                NO_ACCESS_TO_ATTRIBUTE,
                new TableReportParameters()
                        .withId(COUNTER_ID)
                        .withMetric(metricName));
    }

    @AfterClass
    public static void cleanup() {
        deleteGrants();
    }

    private static void deleteGrants() {
        counter.withGrants(Collections.emptyList());
        userOwner.onManagementSteps().onCountersSteps().editCounter(COUNTER_ID, counter);
    }
}
