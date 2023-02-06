package ru.yandex.autotests.audience.management.tests.segments.client;

import java.io.InputStream;
import java.util.List;
import java.util.function.Supplier;

import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;

import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_INTERNAL_DMP;
import static ru.yandex.autotests.audience.management.tests.TestData.BOUNDARY_LENGTH_SEGMENT_NAME;
import static ru.yandex.autotests.audience.management.tests.TestData.UPLOADING_SEGMENT_NAME_PREFIX;
import static ru.yandex.autotests.audience.management.tests.TestData.getName;
import static ru.yandex.autotests.audience.management.tests.TestData.getSegmentToChange;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;

abstract public class AbstractEditSegmentTest {
    protected final static UserSteps userUploader = UserSteps.withUser(INTERNAL_DMP_UPLOADER);
    protected final static User targetUser = USER_FOR_INTERNAL_DMP;

    protected static Long uploadSegment(Supplier<InputStream> content) {
        return userUploader.onSegmentsSteps().uploadFileForInternal(content.get(),
                ulogin(targetUser)).getId();
    }

    protected static UploadingSegment confirmSegment(Long segmentId,
                                                     Supplier<SegmentRequestUploading> uploadingSegment) {
        return userUploader.onSegmentsSteps().confirmClientSegment(segmentId, uploadingSegment.get());
    }

    protected static void checkEditSegment(UploadingSegment createdSegment, Long segmentId) {
        UploadingSegment segmentToChange = getSegmentToChange(createdSegment, getName(UPLOADING_SEGMENT_NAME_PREFIX));
        UploadingSegment editedSegment = userUploader.onSegmentsSteps().editClientSegment(segmentId, segmentToChange);

        assertThat("изменяемый сегмент эквивалентен измененному", editedSegment,
                equivalentTo(segmentToChange));
    }

    protected static void checkBoundaryNameLength(UploadingSegment createdSegment, Long segmentId) {
        UploadingSegment segmentToChange = getSegmentToChange(createdSegment, BOUNDARY_LENGTH_SEGMENT_NAME);

        userUploader.onSegmentsSteps().editClientSegment(segmentId, segmentToChange);

        List<BaseSegment> segments = userUploader.onSegmentsSteps().getInternalSegments(ulogin(targetUser));

        assertThat("изменненный сегмент присутствует в списке", segments,
                hasBeanEquivalent(UploadingSegment.class, segmentToChange, BeanFieldPath.newPath("guest")));
    }

    protected static void cleanUp(Long segmentId) {
        userUploader.onSegmentsSteps().deleteClientSegment(segmentId);
    }

}
