package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.application;

import java.util.List;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.parameters.ApplicationsAdminRequest;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationUnderCampaign;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.hasProperty;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getApplicationWithAppNamePrefix;

@Features(Requirements.Feature.Management.APPLICATION)
@Stories({
        Requirements.Story.Application.INFO,
        Requirements.Story.Application.LIST
})
@Title("Получение списка приложений (админка)")
public class GetApplicationByAdminTest {

    private static final String APP_NAME_PREFIX = GetApplicationByAdminTest.class.getSimpleName();

    private final static User USER = SIMPLE_USER;
    private final static UserSteps user = UserSteps.onTesting(USER);
    private final static UserSteps admin = UserSteps.onTesting(SUPER_LIMITED);

    private static Application app;
    private static AppTargetUrl targetUrl;
    private static Campaign tracker;

    @BeforeClass
    public static void setup() {
        app = user.onApplicationSteps().addApplication(getApplicationWithAppNamePrefix(APP_NAME_PREFIX));
        CampaignWrapper trackerToAdd = new CampaignWrapper(defaultTracker());
        targetUrl = user.onTrackerSteps().getOrCreateTargetUrl(app.getId(), defaultTargetUrl());
        trackerToAdd.getCampaign().getPlatforms().get(0).setTargetUrlId(targetUrl.getId());
        tracker = user.onTrackerSteps().createTracker(app.getId(), trackerToAdd);
    }

    @Test
    public void searchById() {
        ApplicationsAdminRequest request = new ApplicationsAdminRequest().withAppId(app.getId());
        List<ApplicationUnderCampaign> apps = admin.onAdminSteps().getApplications(request);

        assertThat("Ответ содержит только добавленное приложение", apps, equivalentTo(singletonList(toUnderCampaign(app))));
    }

    @Test
    public void searchByName() {
        ApplicationsAdminRequest request = new ApplicationsAdminRequest().withName(app.getName());
        List<ApplicationUnderCampaign> apps = admin.onAdminSteps().getApplications(request);

        assertThat("Ответ содержит только добавленное приложение", apps, equivalentTo(singletonList(toUnderCampaign(app))));
    }

    @Test
    public void searchByApiKey128() {
        ApplicationsAdminRequest request = new ApplicationsAdminRequest().withApiKey128(app.getApiKey128());
        List<ApplicationUnderCampaign> apps = admin.onAdminSteps().getApplications(request);

        assertThat("Ответ содержит только добавленное приложение", apps, equivalentTo(singletonList(toUnderCampaign(app))));
    }

    @Test
    public void searchByLogin() {
        String ownerLogin = USER.get(User.LOGIN);
        ApplicationsAdminRequest request = new ApplicationsAdminRequest()
                .withOwnerLogin(ownerLogin)
                .withStatus("active");
        List<ApplicationUnderCampaign> apps = admin.onAdminSteps().getApplications(request);

        assumeThat("Правильный владелец", apps, everyItem(hasProperty("ownerLogin", equivalentTo(ownerLogin))));
        assertThat("Ответ содержит добавленное приложение", apps, hasItem(equivalentTo(toUnderCampaign(app))));
    }

    @Test
    public void searchByUid() {
        Long ownerUid = Long.valueOf(USER.get(User.UID));
        ApplicationsAdminRequest request = new ApplicationsAdminRequest()
                .withOwnerUid(ownerUid)
                .withStatus("active");
        List<ApplicationUnderCampaign> apps = admin.onAdminSteps().getApplications(request);

        assumeThat("Правильный владелец", apps, everyItem(hasProperty("uid", equivalentTo(ownerUid))));
        assertThat("Ответ содержит добавленное приложение", apps, hasItem(equivalentTo(toUnderCampaign(app))));
    }

    @Test
    public void searchByTrackingId() {
        ApplicationsAdminRequest request = new ApplicationsAdminRequest().withTrackingId(tracker.getTrackingId());
        List<ApplicationUnderCampaign> apps = admin.onAdminSteps().getApplications(request);

        ApplicationUnderCampaign expected = toUnderCampaign(app)
                .withTrackingId(tracker.getTrackingId())
                .withCampaignName(tracker.getName());
        assertThat("Ответ содержит только добавленное приложение", apps, equivalentTo(singletonList(expected)));
    }

    @AfterClass
    public static void teardown() {
        user.onTrackerSteps().removeTrackerAndIgnoreResult(app.getId(), tracker.getTrackingId());
        user.onTrackerSteps().deleteTargetUrlAndIgnoreResult(app.getId(), targetUrl.getId());
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(app.getId());
    }

    private ApplicationUnderCampaign toUnderCampaign(Application app) {
        ApplicationUnderCampaign result = new ApplicationUnderCampaign();
        return result
                // поля испльзуемые на фронте
                .withId(app.getId())
                .withName(app.getName())
                .withUid(app.getUid())
                .withOwnerLogin(app.getOwnerLogin())
                .withStatus(app.getStatus())
                // тут можно было бы написать все остальные поля, но лень
                .withTimeZoneName(app.getTimeZoneName());
    }
}
