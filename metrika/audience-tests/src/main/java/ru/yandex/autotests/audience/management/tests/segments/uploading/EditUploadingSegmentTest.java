package ru.yandex.autotests.audience.management.tests.segments.uploading;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.SegmentContentType;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ru.yandex.autotests.audience.data.wrappers.WrapperBase.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.UPLOADING_SEGMENT_NAME_PREFIX;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by konkov on 31.03.2017.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.UPLOADING
})
@Title("Cегменты: изменение сегмента из файла")
public class EditUploadingSegmentTest {
    private static final User OWNER = Users.SIMPLE_USER_2;

    private final UserSteps user = UserSteps.withUser(OWNER);

    private Long segmentId;
    private UploadingSegment changedSegment;
    private UploadingSegment expectedSegment;

    @Before
    public void setup() {
        UploadingSegment notConfirmedSegment = user.onSegmentsSteps().uploadFile(TestData.getContent(
                SegmentContentType.CRM, false, ","));

        segmentId = notConfirmedSegment.getId();

        UploadingSegment createdSegment = user.onSegmentsSteps().confirmSegment(segmentId, TestData.getUploadingSegment(
                SegmentContentType.CRM, false));

        UploadingSegment segmentToChange = TestData.getSegmentToChange(createdSegment,
                TestData.getName(UPLOADING_SEGMENT_NAME_PREFIX),
                SegmentContentType.MAC, true);

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
                hasBeanEquivalent(UploadingSegment.class, expectedSegment));
    }

    @After
    public void teardown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
