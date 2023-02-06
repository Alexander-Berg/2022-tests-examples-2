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

import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultOrganization;

@Features(Requirements.Feature.Management.ORGANIZATIONS)
@Stories({
        Requirements.Story.Organizations.EDIT,
        Requirements.Story.Organizations.LIST
})
@Title("Добавление организации (негативный)")
public class EditOrganizationNegativeTest {

    private static final User OWNER = Users.SIMPLE_USER;
    private static final User ANOTHER_USER = Users.SIMPLE_USER_2;

    private final UserSteps support = UserSteps.onTesting(Users.SUPER_LIMITED);
    private final UserSteps owner = UserSteps.onTesting(OWNER);
    private final UserSteps anotherUser = UserSteps.onTesting(ANOTHER_USER);

    private Organization addedOrganization;

    @Before
    public void setup() {
        addedOrganization = owner.onOrganizationSteps().addOrganization(defaultOrganization(OWNER.getUid()));
    }

    @Test
    public void anotherUserTryEdit() {
        addedOrganization.setName(addedOrganization + RandomUtils.getString(10));
        addedOrganization.setOwnerUid(ANOTHER_USER.getUid());
        anotherUser.onOrganizationSteps().editOrganizationAndExpectError(addedOrganization, FORBIDDEN);
    }

    @After
    public void teardown() {
        support.onOrganizationSteps().delete(addedOrganization.getId());
    }
}


