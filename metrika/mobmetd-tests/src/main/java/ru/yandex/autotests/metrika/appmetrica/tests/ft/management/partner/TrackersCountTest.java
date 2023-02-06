package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPartner;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.tracker;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_VIEW;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Created by graev on 23/01/2017.
 */
@Features(Requirements.Feature.Management.PARTNERS)
@Stories({
        Requirements.Story.Partner.TRACKER_COUNT
})
@Title("Количество трекеров партнера")
@RunWith(Parameterized.class)
public final class TrackersCountTest {

    private static final GrantCreator GRANTS = GrantCreator.forUser(SIMPLE_USER);

    @Parameterized.Parameter
    public User owner;

    @Parameterized.Parameter(1)
    public User user;

    @Parameterized.Parameter(2)
    public GrantWrapper grant;

    private UserSteps ownerSteps;

    private UserSteps userSteps;

    private Long appId;

    private Long partnerId;

    private Long targetUrlId;

    private String trackerId;

    @Parameterized.Parameters(name = "Создатель {0}; Пользователь {1}; {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(SIMPLE_USER),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(VIEW)),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT)),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(AGENCY_VIEW)),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(AGENCY_EDIT))
        );
    }

    @Before
    public void setup() {
        ownerSteps = UserSteps.onTesting(owner);
        userSteps = UserSteps.onTesting(user);

        TrackingPartner partner = ownerSteps.onPartnerSteps().createPartner(new PartnerWrapper(defaultPartner()));
        partnerId = partner.getId();

        Application application = ownerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = application.getId();

        ownerSteps.onGrantSteps().createGrantIfAny(appId, grant, partnerId);

        AppTargetUrl targetUrl = ownerSteps.onTrackerSteps().getOrCreateTargetUrl(appId, defaultTargetUrl());
        targetUrlId = targetUrl.getId();

        Campaign tracker = ownerSteps.onTrackerSteps().createTracker(appId,
                new CampaignWrapper(tracker(appId, partnerId, targetUrlId)));
        trackerId = tracker.getTrackingId();
    }

    @Test
    public void checkCampaignCountInPartner() {
        final TrackingPartner partner = userSteps.onPartnerSteps().getPartner(partnerId);

        TestSteps.assertThat("партнер содержит ровно один трекер", partner.getCampaignsCount(),
                equalTo(1L));
    }

    @Test
    public void checkCampaignCountInPartnerList() {
        final TrackingPartner partner = userSteps.onPartnerSteps().getPartnerFromList(partnerId);

        TestSteps.assertThat("партнер из списка содержит ровно один трекер",
                partner.getCampaignsCount(), equalTo(1L));
    }

    @After
    public void teardown() {
        ownerSteps.onTrackerSteps().removeTrackerAndIgnoreResult(appId, trackerId);
        ownerSteps.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, targetUrlId);
        ownerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, grant);
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
        ownerSteps.onPartnerSteps().deletePartner(partnerId);
    }

    private static Object[] param(User user) {
        return param(user, user, null);
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant) {
        return toArray(owner, user, new GrantWrapper(grant));
    }

}
