package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.organization;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.organization.model.Organization;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultOrganization;

@Features(Requirements.Feature.Management.ORGANIZATIONS)
@Stories({
        Requirements.Story.Organizations.DELETE
})
@Title("Удаление организации")
public class DeleteOrganizationNegativeTest {
    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps support = UserSteps.onTesting(Users.SUPER_LIMITED);
    private final UserSteps owner = UserSteps.onTesting(OWNER);

    private Organization addedOrganization;

    @Before
    public void setup() {
        addedOrganization = owner.onOrganizationSteps().addOrganization(defaultOrganization(OWNER.getUid()));
    }

    @Test
    public void deleteOrganization() {
        owner.onOrganizationSteps().deleteAndExpectError(addedOrganization.getId(), FORBIDDEN);
    }

    @After
    public void teardown() {
        support.onOrganizationSteps().delete(addedOrganization.getId());
    }
}
