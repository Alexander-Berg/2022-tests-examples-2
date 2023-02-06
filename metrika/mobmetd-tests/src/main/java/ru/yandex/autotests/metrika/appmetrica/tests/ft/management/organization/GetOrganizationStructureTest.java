package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.organization;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.organization.model.Organization;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultOrganization;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

@Features(Requirements.Feature.Management.ORGANIZATIONS)
@Stories({
        Requirements.Story.Organizations.INFO
})
@Title("Получение информации об организации")
public class GetOrganizationStructureTest {
    private static final User OWNER = SIMPLE_USER;
    private static final User ANOTHER_USER = SIMPLE_USER_2;

    private final UserSteps support = UserSteps.onTesting(SUPER_LIMITED);
    private final UserSteps owner = UserSteps.onTesting(OWNER);
    private final UserSteps anotherUser = UserSteps.onTesting(ANOTHER_USER);

    private Organization expectedOrganization;

    private Application application1;
    private Application application2;
    private Application application3;

    @Before
    public void setup() {
        expectedOrganization = owner.onOrganizationSteps().addOrganization(defaultOrganization(OWNER.getUid()));
        application1 = owner.onApplicationSteps().addApplication(getDefaultApplication());
        application2 = owner.onApplicationSteps().addApplication(getDefaultApplication());
        application3 = owner.onApplicationSteps().addApplication(getDefaultApplication());

        owner.onOrganizationStructureSteps().addToOrganization(expectedOrganization.getId(), application1.getId());
        owner.onOrganizationStructureSteps().addToOrganization(expectedOrganization.getId(), application2.getId());
        owner.onOrganizationStructureSteps().addToOrganization(expectedOrganization.getId(), application3.getId());

        owner.onGrantSteps().createGrant(application1.getId(), new GrantWrapper(forUser(ANOTHER_USER).grant(VIEW)));
        owner.onGrantSteps().createGrant(application2.getId(), new GrantWrapper(forUser(ANOTHER_USER).grant(EDIT)));
    }

    @Test
    public void getGuestOrganizations() {
        var actualOrganizationStructure = anotherUser.onOrganizationStructureSteps().get(expectedOrganization.getId());
        assumeThat("организация содержит application1", actualOrganizationStructure.getApplications(),
                hasItem(equivalentTo(application1.withPermission(null))));
        assumeThat("организация содержит application2", actualOrganizationStructure.getApplications(),
                hasItem(equivalentTo(application2.withPermission(null))));
        assumeThat("организация не содержит application3", actualOrganizationStructure.getApplications(),
                not(hasItem(equivalentTo(application3.withPermission(null)))));
        assertThat("организация с приложениями эквивалентна ожидаемой", actualOrganizationStructure.getOrganization(),
                equivalentTo(expectedOrganization));
    }

    @Test
    public void getOwnOrganizations() {
        var actualOrganizationStructure = owner.onOrganizationStructureSteps().get(expectedOrganization.getId());
        assumeThat("организация содержит application1", actualOrganizationStructure.getApplications(),
                hasItem(equivalentTo(application1.withPermission(null))));
        assumeThat("организация содержит application2", actualOrganizationStructure.getApplications(),
                hasItem(equivalentTo(application2.withPermission(null))));
        assumeThat("организация не содержит application3", actualOrganizationStructure.getApplications(),
                hasItem(equivalentTo(application3.withPermission(null))));
        assertThat("организация с приложениями эквивалентна ожидаемой", actualOrganizationStructure.getOrganization(),
                equivalentTo(expectedOrganization));
    }

    @After
    public void teardown() {
        support.onOrganizationSteps().delete(expectedOrganization.getId());
        support.onApplicationSteps().deleteApplicationAndIgnoreResult(application1.getId());
        support.onApplicationSteps().deleteApplicationAndIgnoreResult(application2.getId());
        support.onApplicationSteps().deleteApplicationAndIgnoreResult(application3.getId());
    }
}
