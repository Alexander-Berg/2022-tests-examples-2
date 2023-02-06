package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.events;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.events.model.EventManagementMetadata;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.INVALID_EVENT_NAME;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getTestEventComment;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getTestEventName;

@Features(Requirements.Feature.Management.Application.EVENTS)
@Stories({
        Requirements.Story.Application.EventsManagement.EDIT
})
@Title("Управление событием (негативный)")
public class ManageEventNegativeTest {

    private static final UserSteps user = UserSteps.onTesting(SIMPLE_USER);

    private Application application;

    @Before
    public void setup() {
        application = user.onApplicationSteps().addApplication(getDefaultApplication());
    }

    @Test
    public void checkFilterNotCreated() {
        user.onEventsManagementSteps().updateEventFiltersAndExpectError(
                application.getId(),
                getTestEventName(),
                new EventManagementMetadata()
                        .withDrop(true)
                        .withComment(getTestEventComment()),
                INVALID_EVENT_NAME);
    }

    @After
    public void teardown() {
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(application.getId());
    }

}
