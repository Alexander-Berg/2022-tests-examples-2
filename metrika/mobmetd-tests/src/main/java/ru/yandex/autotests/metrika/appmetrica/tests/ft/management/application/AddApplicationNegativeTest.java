package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.application;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationCreationInfo;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getApplicationWithTimezoneName;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getApplicationWithoutCategory;

/**
 * Created by konkov on 14.09.2016.
 */
@Features(Requirements.Feature.Management.APPLICATION)
@Stories({
        Requirements.Story.Application.ADD,
})
@Title("Добавление приложения (негативный)")
public class AddApplicationNegativeTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);
    private Long applicationId;

    @Before
    public void setup() {
    }

    @Test
    public void checkEmptyTimeZoneApplication() {
        ApplicationCreationInfo application = getApplicationWithTimezoneName("");
        Application addedApplication = user.onApplicationSteps().addApplicationAndExpectError(APP_EMPTY_TIMEZONE, application);
        applicationId = addedApplication != null ? addedApplication.getId() : null;
    }

    @Test
    public void checkInvalidTimeZoneApplication() {
        ApplicationCreationInfo application = getApplicationWithTimezoneName("invalid");
        Application addedApplication = user.onApplicationSteps().addApplicationAndExpectError(APP_INVALID_TIMEZONE, application);
        applicationId = addedApplication != null ? addedApplication.getId() : null;
    }

    @Test
    public void checkEmptyCategoryFails() {
        ApplicationCreationInfo application = getApplicationWithoutCategory();
        Application addedApplication = user.onApplicationSteps().addApplicationAndExpectError(APP_EMPTY_CATEGORY, application);
        applicationId = addedApplication != null ? addedApplication.getId() : null;
    }

    @After
    public void teardown() {
        if (applicationId != null) {
            user.onApplicationSteps().deleteApplication(applicationId);
        }
    }
}
