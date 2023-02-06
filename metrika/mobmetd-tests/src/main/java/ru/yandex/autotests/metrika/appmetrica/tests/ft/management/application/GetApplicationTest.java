package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.application;

import com.google.common.base.Throwables;
import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.ApplicationCreationInfoWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationCreationInfo;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static java.util.Comparator.comparing;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.SortedByMatcher.sortedBy;
import static ru.yandex.autotests.metrika.appmetrica.parameters.AppListSortParameter.SORTED_ASC;
import static ru.yandex.autotests.metrika.appmetrica.parameters.AppListSortParameter.SORTED_DESC;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

/**
 * Created by graev on 16/01/2017.
 */
@Features(Requirements.Feature.Management.APPLICATION)
@Stories({
        Requirements.Story.Application.INFO,
        Requirements.Story.Application.LIST
})
@Title("Получение приложения")
@RunWith(Parameterized.class)
public class GetApplicationTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);

    private Long applicationId1;
    private Long applicationId2;

    @Parameterized.Parameter()
    public ApplicationCreationInfoWrapper appToAdd;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(getDefaultApplication()))
                .build();
    }

    @Before
    public void setup() {
        Application addedApplication1 = user.onApplicationSteps().addApplication(appToAdd.get());
        applicationId1 = addedApplication1.getId();

        // Это нужно сделать, чтобы время создания двух приложений отличалось
        sleep(2);

        Application addedApplication2 = user.onApplicationSteps().addApplication(appToAdd.get());
        applicationId2 = addedApplication2.getId();
    }

    @Test
    public void applicationListCanBeSortedAsc() {
        final List<Application> applications = user.onApplicationSteps().getApplications(SORTED_ASC);

        assertThat("список приложений отсортирован по дате получения доступа по неубыванию",
                applications, sortedBy(comparing(Application::getPermissionDate)));
    }

    @Test
    public void applicationListCanBeSortedDesc() {
        final List<Application> applications = user.onApplicationSteps().getApplications(SORTED_DESC);

        assertThat("список приложений отсортирован по дате получения доступа по невозрастанию",
                applications, sortedBy(comparing(Application::getPermissionDate).reversed()));
    }

    @After
    public void teardown() {
        user.onApplicationSteps().deleteApplication(applicationId1);
        user.onApplicationSteps().deleteApplication(applicationId2);
    }

    private static Object[] param(ApplicationCreationInfo appToAdd) {
        return toArray(new ApplicationCreationInfoWrapper(appToAdd));
    }

    private static void sleep(int timeout) {
        try {
            TimeUnit.SECONDS.sleep(timeout);
        } catch (InterruptedException e) {
            Throwables.propagate(e);
        }
    }
}
