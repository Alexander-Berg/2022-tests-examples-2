package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.application;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.ApplicationCreationInfoWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationCreationInfo;
import ru.yandex.qatools.allure.annotations.*;

import java.util.Collection;
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.TimeZoneInfo.getSamaraTimeZone;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.formatIsoDtf;

/**
 * Created by konkov on 14.09.2016.
 */
@Features(Requirements.Feature.Management.APPLICATION)
@Stories({
        Requirements.Story.Application.ADD,
        Requirements.Story.Application.INFO,
        Requirements.Story.Application.LIST
})
@Title("Добавление приложения")
@Issues({
        @Issue("MOBMET-5363")
})
@RunWith(Parameterized.class)
public class AddApplicationTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);
    private Application addedApplication;
    private Long applicationId;

    @Parameter()
    public ApplicationCreationInfoWrapper appToAdd;

    @Parameter(1)
    public Application expectedApp;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(getDefaultApplication()))
                .add(param(getApplicationWithTimezone(getSamaraTimeZone())))
                .add(param(getApplicationWithGDPRAgreementAccepted()))
                .add(param(getApplicationWithEmail()))
                .build();
    }

    @Before
    public void setup() {
        addedApplication = user.onApplicationSteps().addApplication(appToAdd.get());
        applicationId = addedApplication.getId();
    }

    @Test
    public void checkAddedApplication() {
        assertThat("добавленное приложение эквивалентно ожидаемому", addedApplication,
                equivalentTo(expectedApp));
    }

    @Test
    public void checkApplicationInfo() {
        Application actualApplication = user.onApplicationSteps().getApplication(applicationId);

        assertThat("актуальное приложение эквивалентно ожидаемому", actualApplication,
                equivalentTo(expectedApp));
    }

    @Test
    public void applicationShouldBeInApplicationsList() {
        final List<Application> applications = user.onApplicationSteps().getApplications();

        assertThat("список приложений содержит приложение, эквивалентное ожидаемому", applications,
                hasItem(equivalentTo(expectedApp)));
    }

    @Test
    public void applicationInListShouldHaveValidPermissionDate() {
        final Application actual = user.onApplicationSteps().getApplicationFromList(addedApplication.getId());

        assertThat("дата выдачи прав на собственное приложение соответствует дате создания",
                formatIsoDtf(actual.getPermissionDate()), startsWith(actual.getCreateDate()));
    }

    @After
    public void teardown() {
        user.onApplicationSteps().deleteApplication(applicationId);
    }

    private static Object[] param(ApplicationCreationInfo appToAdd) {
        return toArray(new ApplicationCreationInfoWrapper(appToAdd), getExpectedApplication(OWNER, appToAdd));
    }
}
