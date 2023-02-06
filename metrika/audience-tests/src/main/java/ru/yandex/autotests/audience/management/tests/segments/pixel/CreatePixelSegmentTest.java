package ru.yandex.autotests.audience.management.tests.segments.pixel;

import org.junit.*;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.pixel.PixelSegment;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdStatGETSchema;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.SegmentRequestPixel;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.audience.management.tests.TestData.getExpectedSegment;
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
@Title("Cегменты: создание сегмента с типом «pixel»")
public class CreatePixelSegmentTest {
    private static final User OWNER = Users.SIMPLE_USER;

    private static final UserSteps user = UserSteps.withUser(OWNER);
    private static Long pixelId;

    private SegmentRequestPixel segmentRequest;
    private PixelSegment createdSegment;
    private Long segmentId;

    @BeforeClass
    public static void init() {
        pixelId = user.onPixelsSteps().createPixel(TestData.getPixelName()).getId();
    }

    @Before
    public void setup() {
        segmentRequest = TestData.getPixelSegment(pixelId);
        createdSegment = user.onSegmentsSteps().createPixel(segmentRequest);
        segmentId = createdSegment.getId();
    }

    @Test
    public void createdSegmentTest() {
        assertThat("созданный сегмент эквивалентен создаваемому", createdSegment,
                equivalentTo(getExpectedSegment(segmentRequest)));
    }

    @Test
    public void statSegementTest() {
        V1ManagementSegmentSegmentIdStatGETSchema stat = user.onSegmentsSteps().getStat(segmentId);

        assertThat("созданный сегмент данных не содержит", stat.getNoData(), equalTo(true));
    }

    @Test
    public void getSegmentsTest() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("созданный сегмент присутствует в списке сегментов", segments,
                hasBeanEquivalent(PixelSegment.class, getExpectedSegment(segmentRequest)));
    }

    @After
    public void teardown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }

    @AfterClass
    public static void cleanup() {
        user.onPixelsSteps().deletePixelAndIgnoreStatus(pixelId);
    }
}
