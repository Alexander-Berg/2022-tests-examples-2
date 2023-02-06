package ru.yandex.autotests.metrika.tests.ft.management.segments.lifecycle;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 10.11.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Создание сегмента (негативные)")
public class CreateSegmentNegativeTest {

    private static UserSteps user;

    private static Long counterId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();

        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void segmentsWithNotAllowedSymbolsInNameTest() {
        user.onManagementSteps().onSegmentsSteps().createSegmentAndExpectError(
                ManagementError.NOT_ALLOWED_SYMBOLS_IN_SEGMENT_NAME,
                counterId,
                getDefaultSegment().withName("\uD83D\uDCC5")
        );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
