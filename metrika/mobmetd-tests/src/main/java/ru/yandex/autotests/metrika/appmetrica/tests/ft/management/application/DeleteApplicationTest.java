package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.application;

import java.util.List;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.DELETED;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

/**
 * Created by konkov on 14.09.2016.
 */
@Features(Requirements.Feature.Management.APPLICATION)
@Stories({
        Requirements.Story.Application.DELETE
})
@Title("Удаление приложения")
public class DeleteApplicationTest {

    private final UserSteps user = UserSteps.onTesting();
    private Application application;

    @Before
    public void setup() {
        application = user.onApplicationSteps().addApplication(getDefaultApplication());

        user.onApplicationSteps().deleteApplication(application.getId());
    }

    @Test
    public void deletedApplicationShouldBeNotAvailable() {
        user.onApplicationSteps().getApplicationAndExpectError(DELETED, application.getId());
    }

    @Test
    public void deletedApplicationShouldNotBeInList() {
        List<Application> applications = user.onApplicationSteps().getApplications();

        assertThat("удаленное приложение не присутствует в списке", applications,
                not(hasItem(equivalentTo(application))));
    }

}
