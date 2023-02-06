package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.PARTNER_IS_REFERENCED_BY_TRACKERS;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.copy;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPartner;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPlatform;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.randomUrlAddress;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper.wrap;
import static ru.yandex.metrika.segments.apps.misc.PartnerType.ORDINARY;

/**
 * Created by graev on 21/12/2016.
 */
@Features(Requirements.Feature.Management.PARTNERS)
@Stories({
        Requirements.Story.Partner.ADD,
        Requirements.Story.Partner.LIST,
        Requirements.Story.Partner.INFO
})
@Title("Добавление интеграционного партнера")
public final class AddIntegratedPartnerTest {

    private UserSteps supportUser = UserSteps.onTesting(SUPER_LIMITED);
    private UserSteps simpleUser = UserSteps.onTesting(SIMPLE_USER);

    private TrackingPartner expectedPartner;

    private TrackingPartner addedPartner;

    private long addedAppId;
    private long addedTargetUrlId;
    private String addedTrackerId;

    @Before
    public void setup() {
        TrackingPartner partnerToAdd = defaultPartner()
                .withIconUrl(randomUrlAddress());
        expectedPartner = copy(partnerToAdd).withType(ORDINARY);
        addedPartner = supportUser.onPartnerSteps().createIntegratedPartner(wrap(partnerToAdd));

        addedAppId = supportUser.onApplicationSteps().addApplication(getDefaultApplication()).getId();

        addedTargetUrlId = supportUser.onTrackerSteps().createTargetUrl(addedAppId, defaultTargetUrl()).getId();

        Campaign trackerToAdd = defaultTracker()
                .withApiKey(addedAppId)
                .withPartnerId(addedPartner.getId())
                .withPartnerType(ORDINARY)
                .withPlatforms(singletonList(
                        defaultPlatform(MobPlatform.ANDROID)
                                .withTargetUrlId(addedTargetUrlId)));
        addedTrackerId = supportUser.onTrackerSteps().createTracker(
                addedAppId, new CampaignWrapper(trackerToAdd)
        ).getTrackingId();
    }

    @Test
    public void checkAddedPartner() {
        assertThat("добавленный партнер эквивалентен ожидаемому", addedPartner,
                equivalentTo(expectedPartner));
    }

    @Test
    public void checkSupportUserCanReadIntegratedPartner() {
        assertThat("support пользователь может прочитать интеграционного партнера", addedPartner,
                equivalentTo(expectedPartner));
    }

    @Test
    public void checkSimpleUserCanReadIntegratedPartner() {
        TrackingPartner partner = simpleUser.onPartnerSteps().getPartner(addedPartner.getId());
        assertThat("обычный пользователь может прочитать интеграционного партнера", partner,
                equivalentTo(expectedPartner));
    }

    @Test
    public void checkSimpleCanNotCreateIntegratedPartner() {
        simpleUser.onPartnerSteps()
                .createIntegratedPartnerAndExpectError(wrap(defaultPartner()), FORBIDDEN);
    }

    @Test
    public void checkErrorOnDeletePartnerWithTracker() {
        supportUser.onPartnerSteps().deleteIntegratedPartnerAndExpectError(
                addedPartner.getId(), PARTNER_IS_REFERENCED_BY_TRACKERS);
    }

    @After
    public void teardown() {
        supportUser.onTrackerSteps().deleteTargetUrlAndIgnoreResult(addedAppId, addedTargetUrlId);
        supportUser.onTrackerSteps().removeTrackerAndIgnoreResult(addedAppId, addedTrackerId);
        supportUser.onPartnerSteps().deleteIntegratedPartnerIgnoringResult(addedPartner.getId());
        supportUser.onApplicationSteps().deleteApplicationAndIgnoreResult(addedAppId);
    }
}
