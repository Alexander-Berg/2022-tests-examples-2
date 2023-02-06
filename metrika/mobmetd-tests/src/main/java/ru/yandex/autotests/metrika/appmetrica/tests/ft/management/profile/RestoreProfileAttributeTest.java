package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.profile;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.parameters.ProfileAttributesParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.ProfileCustomAttributeWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.profiles.model.ProfileCustomAttribute;
import ru.yandex.metrika.segments.apps.misc.profile.ProfileAttributeType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultCustomAttribute;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.PROFILE)
@Stories(Requirements.Story.Profile.Attributes.RESTORE)
@Title("Восстановление атрибутов профилей")
@RunWith(Parameterized.class)
public class RestoreProfileAttributeTest {

    private final static UserSteps user = UserSteps.onTesting(SIMPLE_USER);

    @Parameterized.Parameter
    public ProfileCustomAttributeWrapper attribute;

    private Long appId;

    private ProfileCustomAttributeWrapper createdAttribute;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(params(defaultCustomAttribute(ProfileAttributeType.BOOL)))
                .add(params(defaultCustomAttribute(ProfileAttributeType.NUMBER)))
                .add(params(defaultCustomAttribute(ProfileAttributeType.STRING)))
                .add(params(defaultCustomAttribute(ProfileAttributeType.COUNTER)))
                .build();
    }

    @Before
    public void setup() {
        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        createdAttribute = ProfileCustomAttributeWrapper.wrap(user.onProfileSteps().createCustom(appId, attribute));
        user.onProfileSteps().deleteCustom(appId, createdAttribute);
    }

    @Test
    public void restore() {
        user.onProfileSteps().restoreCustom(appId, createdAttribute);
        List<ProfileCustomAttribute> actualAttributes = user.onProfileSteps()
                .getCustomAttributes(appId, new ProfileAttributesParameters());
        assertThat("атрибут профиля присутствует в списке активных атрибутов",
                actualAttributes, hasItem(createdAttribute.getAttribute()));
    }

    @After
    public void teardown() {
        user.onProfileSteps().deleteCustomAndIgnoreResult(appId, createdAttribute);
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] params(ProfileCustomAttribute attribute) {
        return new Object[]{ProfileCustomAttributeWrapper.wrap(attribute)};
    }
}
