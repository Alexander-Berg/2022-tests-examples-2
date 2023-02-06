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

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultOrganization;

@Features(Requirements.Feature.Management.ORGANIZATIONS)
@Stories({
        Requirements.Story.Organizations.ADD,
        Requirements.Story.Organizations.LIST
})
@Title("Добавление организации")
public class AddOrganizationTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps support = UserSteps.onTesting(Users.SUPER_LIMITED);
    private final UserSteps owner = UserSteps.onTesting(OWNER);

    private Organization expectedOrganization;
    private Organization addedOrganization;

    @Before
    public void setup() {
        expectedOrganization = defaultOrganization(OWNER.getUid());
        addedOrganization = owner.onOrganizationSteps().addOrganization(expectedOrganization);
    }

    @Test
    public void addOrganization() {
        assertThat("добавленная организация эквивалентна ожидаемой", addedOrganization,
                equivalentTo(expectedOrganization));
    }

    @Test
    public void getAddedOrganization() {
        Organization actualOrganization = owner.onOrganizationSteps().get(addedOrganization.getId());
        assertThat("полученная организация эквивалентна ожидаемой", actualOrganization,
                equivalentTo(expectedOrganization));
    }

    @After
    public void teardown() {
        support.onOrganizationSteps().delete(addedOrganization.getId());
    }
}


