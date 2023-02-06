package ru.yandex.autotests.advapi.api.tests.ft.management.placements;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.Errors.LAST_PLACEMENT_REMOVAL;
import static ru.yandex.autotests.advapi.Errors.NOT_FOUND;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;

@Features(MANAGEMENT)
@Title("Удаление размещений (негативные)")
@RunWith(Parameterized.class)
public class DeletePlacementNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final long ADVERTISER_ID = 196;
    private static final long CAMPAIGN_ID = 256;
    private static final long NOT_EXISTING_PLACEMENT = 0L;
    private static final long ONLY_PLACEMENT = 268L;


    @Parameterized.Parameter()
    public Long pid;

    @Parameterized.Parameter(1)
    public IExpectedError error;

    @Parameterized.Parameter(2)
    public String message;

    @Parameterized.Parameters(name = "{2}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        NOT_EXISTING_PLACEMENT,
                        NOT_FOUND,
                        "нельзя удалить несуществующее размещение"
                },
                {
                        ONLY_PLACEMENT,
                        LAST_PLACEMENT_REMOVAL,
                        "нельзя удалить единственное размещение для кампании"
                }
        });
    }

    @Test
    public void failToDeletePlacement() {
        UserSteps.withUser(OWNER).onPlacementsSteps().deletePlacementAndExpectError(ADVERTISER_ID, CAMPAIGN_ID, pid, error);
    }
}
