package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.profile;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.ProfileCustomAttributeWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.profiles.model.ProfileCustomAttribute;
import ru.yandex.metrika.segments.apps.misc.profile.ProfileAttributeType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultCustomAttribute;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.ProfileCustomAttributeWrapper.wrap;

@Features(Requirements.Feature.Management.PROFILE)
@Stories({
        Requirements.Story.Profile.Attributes.ADD,
        Requirements.Story.Profile.Attributes.DELETE,
        Requirements.Story.Profile.Attributes.RESTORE
})
@Title("Ошибки при работе с атрибутами профилей")
public class ProfileAttributeNegativeTest {

    private final static UserSteps user = UserSteps.onTesting(SIMPLE_USER);

    private Long appId;

    private ProfileCustomAttribute attribute1;
    private ProfileCustomAttribute attribute2;

    @Before
    public void setup() {
        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void testDublicate() {
        ProfileCustomAttributeWrapper wrapper = wrap(defaultCustomAttribute(ProfileAttributeType.STRING));
        attribute1 = user.onProfileSteps().createCustom(appId, wrapper);
        user.onProfileSteps().createCustomAndExpectError(appId, wrapper, PROFILE_DUPLICATE);
    }

    @Test
    public void testAlreadyActiveOnCreate() {
        attribute1 = user.onProfileSteps().createCustom(appId,
                wrap(defaultCustomAttribute(ProfileAttributeType.STRING)));

        user.onProfileSteps().createCustomAndExpectError(appId,
                wrap(
                        defaultCustomAttribute(ProfileAttributeType.COUNTER)
                                .withName(attribute1.getName())
                ),
                PROFILE_ADD_ACTIVE_NAME);
    }

    @Test
    public void testAlreadyActiveOnRestore() {
        attribute1 = user.onProfileSteps().createCustom(appId,
                wrap(defaultCustomAttribute(ProfileAttributeType.STRING)));
        user.onProfileSteps().deleteCustom(appId, wrap(attribute1));

        attribute2 = user.onProfileSteps().createCustom(appId,
                wrap(
                        defaultCustomAttribute(ProfileAttributeType.COUNTER)
                                .withName(attribute1.getName())
                ));

        user.onProfileSteps().restoreCustomAndExpectError(appId, wrap(attribute1), PROFILE_RESTORE_ACTIVE_NAME);
    }

    @After
    public void teardown() {
        if (attribute1 != null) {
            user.onProfileSteps().deleteCustomAndIgnoreResult(appId, wrap(attribute1));
        }
        if (attribute2 != null) {
            user.onProfileSteps().deleteCustomAndIgnoreResult(appId, wrap(attribute2));
        }
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
