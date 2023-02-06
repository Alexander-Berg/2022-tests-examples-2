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
import ru.yandex.metrika.mobmet.profiles.model.ProfilePredefinedAttribute;
import ru.yandex.metrika.mobmet.profiles.model.ProfileStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.*;
import java.util.stream.Collectors;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultCustomAttribute;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.segments.apps.misc.profile.ProfileAttributeType.*;

@Features(Requirements.Feature.Management.PROFILE)
@Stories(Requirements.Story.Profile.Attributes.LIST)
@Title("Получение списка атрибутов профилей")
@RunWith(Parameterized.class)
public class ProfileAttributesListTest {

    private final static UserSteps user = UserSteps.onTesting(SIMPLE_USER);

    @Parameterized.Parameter
    public List<ProfileCustomAttributeWrapper> customAttributesToAdd;

    private Long appId;

    private List<ProfileCustomAttribute> expectedAllAttributes;

    private List<ProfileCustomAttribute> expectedActiveAttributes;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param())
                .add(param(
                        defaultCustomAttribute(STRING),
                        defaultCustomAttribute(NUMBER),
                        defaultCustomAttribute(COUNTER).withStatus(ProfileStatus.DELETED)))
                .build();
    }

    @Before
    public void setup() {
        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        List<ProfileCustomAttribute> attributes = new ArrayList<>();
        customAttributesToAdd.forEach(wrapper -> {
            ProfileCustomAttribute result = user.onProfileSteps().createCustom(appId, wrapper);
            attributes.add(result);
        });

        attributes.sort(Comparator.comparing(ProfileCustomAttribute::getName));

        expectedAllAttributes = attributes;

        expectedActiveAttributes = expectedAllAttributes.stream()
                .filter(attribute -> attribute.getStatus() == ProfileStatus.ACTIVE)
                .collect(Collectors.toList());
    }

    @Test
    public void testPredefined() {
        List<ProfilePredefinedAttribute> predefined = user.onProfileSteps().getPredefinedAttributes(appId);
        assertThat("получение списка предопределённых атрибутов", predefined, not(empty()));
    }

    @Test
    public void checkCustomWithoutDeleted() {
        List<ProfileCustomAttribute> attributes = user.onProfileSteps().getCustomAttributes(appId, new ProfileAttributesParameters());
        assertThat("получение списка активных атрибутов пользователя", attributes, equivalentTo(expectedActiveAttributes));
    }

    @Test
    public void checkOnlyDisabledAttributesList() {
        List<ProfileCustomAttribute> attributes = user.onProfileSteps()
                .getCustomAttributes(appId, new ProfileAttributesParameters().includeDeleted());
        assertThat("получение списка удалённых атрибутов пользователя", attributes, equivalentTo(expectedAllAttributes));
    }

    @After
    public void teardown() {
        expectedActiveAttributes.forEach(attribute ->
                user.onProfileSteps().deleteCustom(appId, ProfileCustomAttributeWrapper.wrap(attribute)));
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(ProfileCustomAttribute... attributes) {
        List<ProfileCustomAttributeWrapper> attributeWrappers = Arrays.stream(attributes)
                .map(ProfileCustomAttributeWrapper::wrap)
                .collect(Collectors.toList());
        return new Object[]{attributeWrappers};
    }
}
