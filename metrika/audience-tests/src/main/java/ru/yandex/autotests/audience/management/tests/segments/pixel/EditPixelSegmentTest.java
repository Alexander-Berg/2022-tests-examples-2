package ru.yandex.autotests.audience.management.tests.segments.pixel;

import org.junit.*;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.pixel.PixelSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ru.yandex.autotests.audience.data.wrappers.SegmentRequestPixelWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.PIXEL_NAME_PREFIX;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by konkov on 31.03.2017.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.PIXEL
})
@Title("Cегменты: изменение сегмента с типом «pixel»")
public class EditPixelSegmentTest {
    private static final User OWNER = Users.SIMPLE_USER;

    private static final UserSteps user = UserSteps.withUser(OWNER);
    private static Long pixelId;
    private static Long otherPixelId;

    private Long segmentId;
    private PixelSegment changedSegment;
    private PixelSegment expectedSegment;

    @BeforeClass
    public static void init() {
        pixelId = user.onPixelsSteps().createPixel(TestData.getPixelName()).getId();
        otherPixelId = user.onPixelsSteps().createPixel(TestData.getPixelName()).getId();
    }

    @Before
    public void setup() {
        PixelSegment createdSegment = user.onSegmentsSteps().createPixel(TestData.getPixelSegment(pixelId));
        segmentId = createdSegment.getId();

        PixelSegment segmentToChange = TestData.getSegmentToChange(createdSegment,
                TestData.getName(PIXEL_NAME_PREFIX), otherPixelId);

        changedSegment = user.onSegmentsSteps().editSegment(segmentId, segmentToChange);

        expectedSegment = wrap(createdSegment).getClone().withName(segmentToChange.getName());
    }

    @Test
    public void checkChangedSegment() {
        assertThat("измененный сегмент совпадает с ожидаемым", changedSegment,
                equivalentTo(expectedSegment));
    }

    @Test
    public void checkChangedSegmentInList() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("измененный сегмент присутствует в списке сегментов", segments,
                hasBeanEquivalent(PixelSegment.class, expectedSegment));
    }

    @After
    public void teardown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }

    @AfterClass
    public static void cleanup() {
        user.onPixelsSteps().deletePixelAndIgnoreStatus(pixelId);
        user.onPixelsSteps().deletePixelAndIgnoreStatus(otherPixelId);
    }

}
