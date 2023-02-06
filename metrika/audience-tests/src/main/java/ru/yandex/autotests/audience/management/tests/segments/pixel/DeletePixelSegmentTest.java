package ru.yandex.autotests.audience.management.tests.segments.pixel;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.management.tests.TestData.getPixelName;
import static ru.yandex.autotests.audience.management.tests.TestData.getPixelSegment;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 25.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.PIXEL
})
@Title("Пиксель: удаление сегмента с типом «pixel»")
public class DeletePixelSegmentTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER);

    private Long segmentId;
    private Long pixelId;

    @Before
    public void setup() {
        pixelId = user.onPixelsSteps().createPixel(getPixelName()).getId();
        segmentId = user.onSegmentsSteps().createPixel(getPixelSegment(pixelId)).getId();

        user.onSegmentsSteps().deleteSegment(segmentId);
    }

    @Test
    public void checkSegmentDeleted() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("сегмент отсутствует в списке", segments,
                not(hasItem(having(on(BaseSegment.class).getId(), equalTo(segmentId)))));
    }

    @After
    public void tearDown() {
        user.onPixelsSteps().deletePixelAndIgnoreStatus(pixelId);
    }
}
