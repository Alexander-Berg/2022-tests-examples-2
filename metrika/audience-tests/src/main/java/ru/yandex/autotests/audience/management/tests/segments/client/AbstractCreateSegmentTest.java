package ru.yandex.autotests.audience.management.tests.segments.client;

import java.util.List;

import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;

import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_INTERNAL_DMP;
import static ru.yandex.autotests.audience.management.tests.TestData.getExpectedSegment;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;

abstract public class AbstractCreateSegmentTest {
    protected static final User TARGET_USER = USER_FOR_INTERNAL_DMP;
    protected static final UserSteps userUploader = UserSteps.withUser(INTERNAL_DMP_UPLOADER);
    protected static final UserSteps userOwner = UserSteps.withUser(TARGET_USER);

    protected void checkCreatedSegment(UploadingSegment segment, SegmentRequestUploading segmentRequest) {
        assertThat("созданный сегмент эквивалентен создаваемому", segment,
                equivalentTo(getExpectedSegment(segmentRequest)));
    }

    protected void checkSegmentInTargetUserList(SegmentRequestUploading segmentRequest) {
        List<BaseSegment> segments = userOwner.onSegmentsSteps().getSegments();

        assertThat("сегмент присутствует в списке владельца", segments,
                hasBeanEquivalent(UploadingSegment.class, getExpectedSegment(segmentRequest)));
    }

    protected void checkSegmentInUploaderList(SegmentRequestUploading segmentRequest) {
        List<BaseSegment> segments = userUploader.onSegmentsSteps().getInternalSegments(ulogin(TARGET_USER));

        assertThat("сегмент присутствует в списке \"заливателя\"", segments,
                hasBeanEquivalent(UploadingSegment.class, getExpectedSegment(segmentRequest)));
    }

    protected static void cleanUp(Long segmentId) {
        userOwner.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
