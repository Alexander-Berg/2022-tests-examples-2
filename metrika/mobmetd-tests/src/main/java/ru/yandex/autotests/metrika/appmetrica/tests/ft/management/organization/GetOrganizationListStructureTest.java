package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.organization;

import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.organization.model.OrganizationStructure;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultOrganization;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

@Features(Requirements.Feature.Management.ORGANIZATIONS)
@Stories({
        Requirements.Story.Organizations.INFO
})
@Title("Получение списка организаций с приложениями")
public class GetOrganizationListStructureTest {
    private static final User TEST_USER = SIMPLE_USER;
    private static final User ANOTHER_USER = SIMPLE_USER_2;

    private final UserSteps support = UserSteps.onTesting(SUPER_LIMITED);
    private final UserSteps testUser = UserSteps.onTesting(TEST_USER);
    private final UserSteps anotherUser = UserSteps.onTesting(ANOTHER_USER);

    private OrganizationStructure testUserOrganizationStructure;
    private OrganizationStructure guestOrganizationStructure;

    private Application application;

    @Before
    public void setup() {
        var testUserOrganization =
                testUser.onOrganizationSteps().addOrganization(defaultOrganization(TEST_USER.getUid()));
        var guestOrganization = anotherUser.onOrganizationSteps().addOrganization(
                defaultOrganization(ANOTHER_USER.getUid()));

        application = anotherUser.onApplicationSteps().addApplication(getDefaultApplication());
        anotherUser.onOrganizationStructureSteps().addToOrganization(guestOrganization.getId(), application.getId());
        anotherUser.onGrantSteps().createGrant(application.getId(), new GrantWrapper(forUser(TEST_USER).grant(VIEW)));

        testUserOrganizationStructure = new OrganizationStructure()
                .withOrganization(testUserOrganization);
        guestOrganizationStructure = new OrganizationStructure()
                .withOrganization(guestOrganization)
                .withApplications(List.of(application.withPermission(null)));
    }

    @Test
    public void getOrganizationList() {
        List<OrganizationStructure> organizations = testUser.onOrganizationStructureSteps().getList();
        assumeThat("список содержит testUserOrganization", organizations,
                hasItem(equivalentTo(testUserOrganizationStructure)));
        assertThat("список содержит guestOrganization", organizations,
                hasItem(equivalentTo(guestOrganizationStructure)));
    }

    @After
    public void teardown() {
        support.onOrganizationSteps().delete(testUserOrganizationStructure.getOrganization().getId());
        support.onOrganizationSteps().delete(guestOrganizationStructure.getOrganization().getId());
        support.onApplicationSteps().deleteApplicationAndIgnoreResult(application.getId());
    }
}
