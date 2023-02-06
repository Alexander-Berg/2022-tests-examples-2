package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker.adwords;

import java.util.Collection;
import java.util.List;
import java.util.function.Supplier;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.utils.AdwordsConversionValues;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.RandomStringUtils.randomAlphanumeric;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.ADWORDS_DUPLICATE;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.ADWORDS_DUPLICATE_DEPRECATED;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.adwordsTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changeTrackerConversion;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.utils.AdwordsConversionValues.deprecated;
import static ru.yandex.autotests.metrika.appmetrica.utils.AdwordsConversionValues.linkId;
import static ru.yandex.autotests.metrika.appmetrica.utils.AdwordsConversionValues.semiNew;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.ADD
})
@RunWith(Parameterized.class)
@Title("Проверка дублирования трекера Google Ads")
public class AdwordsConversionDuplicateTest {

    private static final User USER = SIMPLE_USER;

    private final UserSteps userSteps = UserSteps.onTesting(USER);

    @Parameter
    public String description;

    @Parameter(1)
    public Supplier<AdwordsConversionValues> trackerConfigurationSupplier;

    @Parameter(2)
    public IExpectedError expectedError;

    private CampaignWrapper trackerToCreate;

    private Long appId;
    private String trackingId;
    private String otherTrackingId;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(
                        "Ads Link ID",
                        () -> linkId(randomAlphanumeric(10)),
                        ADWORDS_DUPLICATE))
                .add(param(
                        "Conversion ID/Label",
                        () -> deprecated(randomAlphanumeric(10), randomAlphanumeric(10)),
                        ADWORDS_DUPLICATE_DEPRECATED))
                .add(param(
                        "Both specified",
                        () -> semiNew(randomAlphanumeric(10), randomAlphanumeric(10), randomAlphanumeric(10)),
                        ADWORDS_DUPLICATE))
                .build();
    }

    private static Object[] param(String description, Supplier<AdwordsConversionValues> supplier, IExpectedError error) {
        return new Object[]{description, supplier, error};
    }

    @Before
    public void init() {
        Application ownerApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = ownerApplication.getId();

        trackerToCreate = new CampaignWrapper(adwordsTracker(appId, null, trackerConfigurationSupplier.get()));

        Campaign createdTracker = userSteps.onTrackerSteps().createTracker(appId, trackerToCreate);
        trackingId = createdTracker.getTrackingId();
    }

    @Test
    @Title("Проверка созданного трекера Google Ads в списке запрещённых")
    public void testOwnerConversionsAreReturned() {
        List<AdwordsConversionValues> actualConversions = userSteps.onTrackerSteps().getAdwordsConversions(USER);
        assertThat("Созданный трекер Google Ads есть в списке запрещенных", actualConversions,
                hasItem(AdwordsConversionValues.of(trackerToCreate.getCampaign())));
    }

    @Test
    @Title("Проверка конфликта с уже используемым трекером Google Ads при создании трекера")
    public void checkTrackerCreation() {
        userSteps.onTrackerSteps().createTrackerAndExpectError(appId, trackerToCreate, expectedError);
    }

    @Test
    @Title("Проверка конфликта с уже используемым трекером Google Ads при редактировании трекера")
    public void checkTrackerEdit() {
        AdwordsConversionValues originalConfig = AdwordsConversionValues.of(trackerToCreate.getCampaign());
        AdwordsConversionValues newConfig = trackerConfigurationSupplier.get();
        assumeThat("Случайные конфигурации Google Ads не совпадают", originalConfig, not(equalTo(newConfig)));

        CampaignWrapper otherTrackerToCreate = new CampaignWrapper(adwordsTracker(appId, null, newConfig));
        Campaign otherCreatedTracker = userSteps.onTrackerSteps().createTracker(appId, otherTrackerToCreate);
        otherTrackingId = otherCreatedTracker.getTrackingId();

        EditAction<Campaign, Campaign> editAction = changeTrackerConversion(originalConfig);
        CampaignWrapper updatedOtherTracker = new CampaignWrapper(editAction.getUpdate(otherCreatedTracker));

        userSteps.onTrackerSteps().editTrackerAndExpectError(appId, otherTrackingId, updatedOtherTracker, expectedError);
    }

    @Test
    @Title("Проверка конфликта с уже используемым трекером Google Ads при восстановлении трекера")
    public void checkTrackerRestoration() {
        userSteps.onTrackerSteps().removeTracker(appId, trackingId);

        Campaign otherCreatedTracker = userSteps.onTrackerSteps().createTracker(appId, trackerToCreate);
        otherTrackingId = otherCreatedTracker.getTrackingId();

        userSteps.onTrackerSteps().restoreTrackerAndExpectError(appId, trackingId, expectedError);
    }

    @After
    public void teardown() {
        userSteps.onTrackerSteps().removeTrackerAndIgnoreResult(appId, trackingId);
        userSteps.onTrackerSteps().removeTrackerAndIgnoreResult(appId, otherTrackingId);
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
