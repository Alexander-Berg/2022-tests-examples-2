package ru.yandex.autotests.audience.management.tests.stat;

import org.junit.Test;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.SegmentStatDataInnerGoalStatData;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.management.tests.TestData.SEGMENT_WITH_EXTENDED_STAT;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 23.10.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.SEGMENTS})
@Title("Статистика: расширенная статистика с двумя одинаковыми целями")
public class GetExtendedStatTest {
    private final UserSteps user = UserSteps.withUser(USER_FOR_LOOKALIKE);

    @Test
    public void getExtendedStat() {
        List<SegmentStatDataInnerGoalStatData> goals = user.onSegmentsSteps().getStat(SEGMENT_WITH_EXTENDED_STAT)
                .getGoals();

        assertThat("список целей не пустой", goals, iterableWithSize(greaterThan(0)));
    }
}
