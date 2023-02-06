package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.ADD
})
@Title("Проверка активности приложения")
@RunWith(Parameterized.class)
public class GetAppActivityStatusTest {

    private final UserSteps manager = UserSteps.onTesting(SUPER_LIMITED);

    @Parameterized.Parameter
    public Long appId;

    @Parameterized.Parameter(1)
    public String expected;

    @Parameterized.Parameters(name = "app {0}, expected activity status: {1}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(
                new Object[]{Applications.PUSH_SAMPLE.get(ID), "true"},
                new Object[]{Applications.YANDEX_SEARCH_FOR_WP_TESTING.get(ID), "false"}
        );
    }

    @Test
    public void testCheckActiveApp() {
        String isActive = manager.onTrackerSteps().isAppActive(appId);
        assertThat("Статус активности приложения совпадает с ожидаемым", isActive, equalTo(expected));
    }
}
