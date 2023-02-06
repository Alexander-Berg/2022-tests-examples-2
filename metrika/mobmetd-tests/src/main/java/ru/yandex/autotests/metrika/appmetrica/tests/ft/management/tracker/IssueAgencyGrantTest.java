package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import java.util.Collection;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.awaitility.Awaitility.given;
import static ru.yandex.autotests.metrika.appmetrica.data.Partner.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.DIRECT;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.ZORKA;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.tracker;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper.wrap;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_VIEW;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Created by graev on 08/12/2016.
 */

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.ADD
})
@Title("Выдача агентских прав при создании трекера")
@RunWith(Parameterized.class)
public final class IssueAgencyGrantTest {

    private static final User MANAGER = SUPER_LIMITED;
    private static final User USER = SIMPLE_USER;
    private static final GrantCreator GRANTS = forUser(USER);

    private static final UserSteps owner = UserSteps.onTesting(SIMPLE_USER_2);
    private static final UserSteps manager = UserSteps.onTesting(MANAGER);

    @Parameterized.Parameter
    public GrantWrapper priorGrant;

    @Parameterized.Parameter(1)
    public GrantWrapper expectedGrant;

    private Campaign addedTracker;

    private AppTargetUrl targetUrl;

    private Long appId;

    @Parameterized.Parameters(name = "{0}. {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(null, GRANTS.grant(AGENCY_VIEW, DIRECT)))
                .add(param(GRANTS.grant(AGENCY_VIEW, ZORKA, DIRECT), GRANTS.grant(AGENCY_VIEW, ZORKA, DIRECT)))
                .add(param(GRANTS.grant(AGENCY_VIEW, ZORKA), GRANTS.grant(AGENCY_VIEW, ZORKA, DIRECT)))
                .add(param(GRANTS.grant(VIEW), GRANTS.grant(VIEW)))
                .add(param(GRANTS.grant(EDIT), GRANTS.grant(EDIT)))
                .add(param(GRANTS.grant(AGENCY_EDIT, ZORKA), GRANTS.grant(AGENCY_EDIT, ZORKA, DIRECT)))
                .build();
    }

    @Before
    public void setup() {
        // Убеждаемся, что USER это представитель партнера DIRECT
        manager.onTrackerSteps().createAgencyAccountIfNotExists(DIRECT.get(ID), USER.get(LOGIN));

        // Добавляем приложение
        Application addedApplication = owner.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        // Делаем на него грант если нужно
        if (priorGrant.getGrant() != null) {
            owner.onGrantSteps().createGrant(addedApplication.getId(), priorGrant);
        }

        // Создаем трекер
        targetUrl = owner.onTrackerSteps().getOrCreateTargetUrl(addedApplication.getId(), defaultTargetUrl());
        Campaign trackerToAdd = tracker(addedApplication.getId(), DIRECT.get(ID), targetUrl.getId());

        // Создаем трекер
        addedTracker = owner.onTrackerSteps().createTracker(addedApplication.getId(), wrap(trackerToAdd));
    }

    @Test
    public void checkActualGrantInfo() {
        given().ignoreExceptions().await()
                .atMost(10, TimeUnit.SECONDS).until(apiGrant(), equivalentTo(expectedGrant.getGrant()));
    }

    private Callable<MobmetGrantE> apiGrant() {
        return () -> {
            try {
                return owner.onGrantSteps().getGrant(appId, USER.get(LOGIN));
            } catch (AssertionError error) {
                throw new RuntimeException(error); // allow awaitibility to ignore exception
            }
        };
    }

    @After
    public void teardown() {
        owner.onTrackerSteps().removeTrackerAndIgnoreResult(appId, addedTracker.getTrackingId());
        owner.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, targetUrl.getId());
        owner.onGrantSteps().deleteGrantIgnoringResult(appId, USER.get(LOGIN));
        owner.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
        manager.onTrackerSteps().unbindAgencyAccountAndIgnoreResult(DIRECT.get(ID), USER.get(LOGIN));
    }

    public static Object[] param(MobmetGrantE prior, MobmetGrantE expected) {
        return toArray(new GrantWrapper(prior), new GrantWrapper(expected));
    }
}
