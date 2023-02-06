package ru.yandex.autotests.audience.management.tests.segments.uploading;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.SegmentContentType;
import ru.yandex.autotests.audience.data.wrappers.SegmentRequestUploadingWrapper;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.data.wrappers.SegmentRequestUploadingWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.getContent;
import static ru.yandex.autotests.audience.management.tests.TestData.getUploadingSegment;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 25.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.UPLOADING
})
@Title("Uploading: удаление сегмента созданного из файла")
public class DeleteUploadingSegmentTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    private Long segmentId;

    @Before
    public void setup() {
        SegmentRequestUploadingWrapper request= wrap(getUploadingSegment(SegmentContentType.CRM, false));
        Long notConfirmedSegmentId = user.onSegmentsSteps().uploadFile(getContent(request)).getId();
        segmentId = user.onSegmentsSteps().confirmSegment(notConfirmedSegmentId, request.get()).getId();

        user.onSegmentsSteps().deleteSegment(segmentId);
    }

    @Test
    public void checkSegmentDeleted() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("сегмент отсутствует в списке", segments,
                not(hasItem(having(on(BaseSegment.class).getId(), equalTo(segmentId)))));
    }
}
