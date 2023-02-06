package ru.yandex.autotests.metrika.tests.ft.management.segments.lifecycle;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 10.11.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Удаление сегмента")
public class DeleteSegmentTest {

    private static UserSteps user;

    private static Segment segment;
    private static Long counterId;
    private static Long segmentId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();

        segment = getDefaultSegment();

        segmentId = user.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, segment).getSegmentId();

        user.onManagementSteps().onSegmentsSteps()
                .deleteSegmentAndExpectSuccess(counterId, segmentId);
    }

    @Test
    public void segmentsLifecycleDeleteCheckSegmentInCounterListTest() {
        List<Segment> segments =
                user.onManagementSteps().onSegmentsSteps().getSegmentsAndExpectSuccess(counterId);

        assertThat("созданный сегмент отсутствует в списке сегментов счетчика", segments,
                not(hasItem(beanEquivalent(segment))));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
