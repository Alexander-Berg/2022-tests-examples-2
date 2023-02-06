package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.organization;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.organization.model.Organization;
import ru.yandex.metrika.mobmet.organization.model.OrganizationStructure;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultOrganization;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.ORGANIZATIONS)
@Stories({
        Requirements.Story.Organizations.REMOVE_FROM_ORGANIZATION
})
@Title("Удаление приложения из организации")
public class RemoveFromOrganizationTest {
    private static final User OWNER = SIMPLE_USER;

    private final UserSteps support = UserSteps.onTesting(SUPER_LIMITED);
    private final UserSteps owner = UserSteps.onTesting(OWNER);
    private final UserSteps anotherUser = UserSteps.onTesting(SIMPLE_USER_2);

    private Organization expectedOrganization;
    private OrganizationStructure expectedOrganizationStructure;

    private Application application;

    @Before
    public void setup() {
        expectedOrganization = owner.onOrganizationSteps().addOrganization(defaultOrganization(OWNER.getUid()));
        expectedOrganizationStructure = new OrganizationStructure()
                .withOrganization(expectedOrganization);

        application = owner.onApplicationSteps().addApplication(getDefaultApplication());
        owner.onOrganizationStructureSteps().addToOrganization(expectedOrganization.getId(), application.getId());
    }

    @Test
    public void ownerTest() {
        owner.onOrganizationStructureSteps().removeFromOrganization(expectedOrganization.getId(), application.getId());
        var actualOrganizationStructure = owner.onOrganizationStructureSteps().get(expectedOrganization.getId());
        assertThat("организация с приложениями эквивалентна ожидаемой", actualOrganizationStructure,
                equivalentTo(expectedOrganizationStructure));
    }

    @Test
    public void supportTest() {
        owner.onOrganizationStructureSteps().removeFromOrganization(expectedOrganization.getId(), application.getId());
        var actualOrganizationStructure = owner.onOrganizationStructureSteps().get(expectedOrganization.getId());
        assertThat("организация с приложениями эквивалентна ожидаемой", actualOrganizationStructure,
                equivalentTo(expectedOrganizationStructure));
    }

    @Test
    public void anotherUserTest() {
        anotherUser.onOrganizationStructureSteps().deleteFromOrganizationAndExpectError(expectedOrganization.getId(),
                application.getId(), FORBIDDEN);
    }

    @After
    public void teardown() {
        support.onOrganizationSteps().delete(expectedOrganization.getId());
        support.onApplicationSteps().deleteApplicationAndIgnoreResult(application.getId());
    }
}
