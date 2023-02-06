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
import ru.yandex.metrika.api.management.client.external.DelegateE;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;

import static com.google.common.collect.ImmutableList.of;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.PARTNER_TEST_1;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.yan;

@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.PARTNER_MONEY})
@Title("Доступ к отчетам по данным РСЯ")
@RunWith(Parameterized.class)
public class PartnerMoneyPositiveTests {

    private static final User OWNER = METRIKA_TEST_COUNTERS;
    private static final User GUEST_VIEW = SIMPLE_USER;
    private static final User GUEST_EDIT = SIMPLE_USER2;
    private static final User OWNER_DELEGATE = USER_DELEGATE_PERMANENT;
    private static final User GUEST_VIEW_DELEGATE = USER_DELEGATOR;
    private static final User GUEST_EDIT_DELEGATE = USER_DELEGATOR2;

    private static final Long COUNTER_ID = PARTNER_TEST_1.getId();

    protected static final UserSteps userTest = new UserSteps().withDefaultAccuracy();

    private static UserSteps user;
    private static UserSteps userOwner;
    private static UserSteps userGuestEdit;
    private static UserSteps userGuestView;
    private static CounterFull counter;


    @Parameter(0)
    public String title;

    @Parameter(1)
    public User currentUser;

    @Parameter(2)
    public String metricName;
    @Parameters(name = "Доступ: {0}, пользователь: {1}, метрика {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of("владелец", OWNER),
                        of("гостевой доступ на редактирование", GUEST_EDIT),
                        of("гостевой доступ на чтение", GUEST_VIEW),
                        of("представитель владельца", OWNER_DELEGATE),
                        of("представитель гостя с доступом на редактирование", GUEST_EDIT_DELEGATE),
                        of("представитель гостя с доступом на чтение", GUEST_VIEW_DELEGATE),
                        of("суперпользователь", SUPER_USER),
                        of("менеджер", MANAGER),
                        of("менеджер-директ", MANAGER_DIRECT),
                        of("саппорт", SUPPORT))
                .values(userTest.onMetadataSteps().getMetrics(yan()))
                .build();
    }

    @BeforeClass
    public static void init() {
        userOwner = new UserSteps().withDefaultAccuracy().withUser(OWNER);
        userGuestEdit = new UserSteps().withDefaultAccuracy().withUser(GUEST_EDIT);
        userGuestView = new UserSteps().withDefaultAccuracy().withUser(GUEST_VIEW);

        counter = userOwner.onManagementSteps().onCountersSteps().getCounterInfo(COUNTER_ID);
        counter.withGrants(Arrays.asList(
                new GrantE().withUserLogin(GUEST_VIEW.get(LOGIN)).withPerm(GrantType.VIEW).withPartnerDataAccess(true),
                new GrantE().withUserLogin(GUEST_EDIT.get(LOGIN)).withPerm(GrantType.EDIT)
        ));
        userOwner.onManagementSteps().onCountersSteps().editCounter(COUNTER_ID, counter, ignoreQuota(true));

        userOwner.onManagementSteps().onDelegatesSteps().addDelegateAndExpectSuccess(new DelegateE().withUserLogin(OWNER_DELEGATE.get(LOGIN)), ignoreQuota(true));
        userGuestEdit.onManagementSteps().onDelegatesSteps().addDelegateAndExpectSuccess(new DelegateE().withUserLogin(GUEST_EDIT_DELEGATE.get(LOGIN)), ignoreQuota(true));
        userGuestView.onManagementSteps().onDelegatesSteps().addDelegateAndExpectSuccess(new DelegateE().withUserLogin(GUEST_VIEW_DELEGATE.get(LOGIN)), ignoreQuota(true));
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy().withUser(currentUser);
    }

    @Test
    public void accessUserSuccess() {
        user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withId(COUNTER_ID)
                        .withMetric(metricName));
    }

    @AfterClass
    public static void cleanup() {
        deleteGrants();
        deleteDelegates();

    }

    private static void deleteDelegates() {
        userOwner.onManagementSteps().onDelegatesSteps().deleteDelegateAndExpectSuccess(OWNER_DELEGATE.get(LOGIN));
        userGuestEdit.onManagementSteps().onDelegatesSteps().deleteDelegateAndExpectSuccess(GUEST_EDIT_DELEGATE.get(LOGIN));
        userGuestView.onManagementSteps().onDelegatesSteps().deleteDelegateAndExpectSuccess(GUEST_VIEW_DELEGATE.get(LOGIN));
    }

    private static void deleteGrants() {
        counter.withGrants(Collections.emptyList());
        userOwner.onManagementSteps().onCountersSteps().editCounter(COUNTER_ID, counter);
    }
}
