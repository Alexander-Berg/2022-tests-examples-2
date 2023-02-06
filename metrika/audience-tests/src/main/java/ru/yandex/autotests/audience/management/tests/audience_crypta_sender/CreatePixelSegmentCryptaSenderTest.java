package ru.yandex.autotests.audience.management.tests.audience_crypta_sender;

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
import static ru.yandex.autotests.audience.management.tests.TestData.PIXEL_ID_CRYPTA_SENDER;
import static ru.yandex.autotests.audience.management.tests.TestData.getExpectedSegment;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(Requirements.Feature.AudienceCryptaSender)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.PIXEL
})
@Title("Cегменты: создание сегмента с типом «pixel»")
public class CreatePixelSegmentCryptaSenderTest {
    private static final User OWNER = Users.AUDIENCE_CRYPTA_SENDER_CREATOR;

    private static final UserSteps user = UserSteps.withUser(OWNER);
    private static Long pixelId;

    private SegmentRequestPixel segmentRequest;
    private PixelSegment createdSegment;
    private Long segmentId;

    @Before
    public void setup() {
        pixelId = PIXEL_ID_CRYPTA_SENDER;
        segmentRequest = TestData.getPixelSegmentCryptaSender(pixelId);
        createdSegment = user.onSegmentsSteps().createPixel(segmentRequest);
        segmentId = createdSegment.getId();
    }

    @Test
    public void createdSegmentTest() {
        assertThat("созданный сегмент эквивалентен создаваемому", createdSegment, equivalentTo(getExpectedSegment(segmentRequest)));
    }
}
