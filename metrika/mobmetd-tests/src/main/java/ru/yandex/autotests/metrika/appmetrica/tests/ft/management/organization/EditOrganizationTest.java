package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.organization;


import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.irt.testutils.RandomUtils;
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
        Requirements.Story.Organizations.EDIT,
        Requirements.Story.Organizations.LIST
})
@Title("Редактирование организации")
public class EditOrganizationTest {

    private final User owner = Users.SIMPLE_USER;

    private final UserSteps support = UserSteps.onTesting(Users.SUPER_LIMITED);
    private final UserSteps user = UserSteps.onTesting(owner);

    private Organization expectedOrganization;
    private Organization newOrganizationValue;

    @Before
    public void setup() {
        expectedOrganization = defaultOrganization(owner.getUid());
        newOrganizationValue = user.onOrganizationSteps().addOrganization(expectedOrganization);
        expectedOrganization.setId(newOrganizationValue.getId());

        expectedOrganization.setName(expectedOrganization + RandomUtils.getString(10));
        newOrganizationValue = user.onOrganizationSteps().editOrganization(expectedOrganization);
    }

    @Test
    public void editOrganization() {
        assertThat("добавленная организация эквивалентна ожидаемой", newOrganizationValue,
                equivalentTo(expectedOrganization));
    }

    @Test
    public void getOrganizationTest() {
        Organization actualOrganization = user.onOrganizationSteps().get(newOrganizationValue.getId());
        assertThat("полученная организация эквивалентна ожидаемой", actualOrganization,
                equivalentTo(expectedOrganization));
    }

    @After
    public void teardown() {
        support.onOrganizationSteps().delete(newOrganizationValue.getId());
    }
}
