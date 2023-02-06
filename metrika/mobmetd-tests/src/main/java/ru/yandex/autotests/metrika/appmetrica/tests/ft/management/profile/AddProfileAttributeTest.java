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
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultCustomAttribute;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.ProfileCustomAttributeWrapper.wrap;

@Features(Requirements.Feature.Management.PROFILE)
@Stories(Requirements.Story.Profile.Attributes.ADD)
@Title("Добавление атрибутов профилей")
@RunWith(Parameterized.class)
public class AddProfileAttributeTest {

    private final static UserSteps user = UserSteps.onTesting(SIMPLE_USER);

    @Parameterized.Parameter
    public ProfileCustomAttributeWrapper attribute;

    private Long appId;

    private ProfileCustomAttribute createdAttribute;

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
    }

    @Test
    public void add() {
        createdAttribute = user.onProfileSteps().createCustom(appId, attribute);

        assertThat("атрибут профиля корректно создан", createdAttribute, equivalentTo(attribute.getAttribute()));
        List<ProfileCustomAttribute> actualAttributes = user.onProfileSteps()
                .getCustomAttributes(appId, new ProfileAttributesParameters());
        assertThat("атрибут профиля присутствует в списке активных атрибутов", actualAttributes, hasItem(createdAttribute));
    }

    @After
    public void teardown() {
        user.onProfileSteps().deleteCustomAndIgnoreResult(appId, ProfileCustomAttributeWrapper.wrap(createdAttribute));
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] params(ProfileCustomAttribute attribute) {
        return new Object[]{wrap(attribute)};
    }
}
