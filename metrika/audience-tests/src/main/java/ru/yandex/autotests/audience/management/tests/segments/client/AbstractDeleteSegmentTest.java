package ru.yandex.autotests.audience.management.tests.segments.client;

import java.io.InputStream;
import java.util.List;
import java.util.function.Supplier;
import java.util.stream.Collectors;

import ru.yandex.audience.BaseSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_INTERNAL_DMP;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

abstract public class AbstractDeleteSegmentTest {
    protected static final UserSteps userUploader = UserSteps.withUser(INTERNAL_DMP_UPLOADER);
    protected static final User TARGET_USER = USER_FOR_INTERNAL_DMP;
    protected static final UserSteps userOwner = UserSteps.withUser(TARGET_USER);

    protected static Long init(Supplier<InputStream> content,
                             Supplier<SegmentRequestUploading> uploadingSegment) {
        Long segmentId = userUploader.onSegmentsSteps().uploadFileForInternal(content.get(),
                ulogin(TARGET_USER)).getId();
        userUploader.onSegmentsSteps().confirmClientSegment(segmentId, uploadingSegment.get());

        userUploader.onSegmentsSteps().deleteClientSegment(segmentId);
        return segmentId;
    }

    protected static void checkSegmentIsNotInListUploader(Long segmentId) {
        List<Long> segmentIds = userUploader.onSegmentsSteps().getInternalSegments(ulogin(TARGET_USER)).stream()
                .map(BaseSegment::getId).collect(Collectors.toList());

        assertThat("сегмент отсутствует в списке \"заливателя\"", segmentIds, not(hasItem(segmentId)));
    }

    protected static void checkSegmentIsNotInListOwner(Long segmentId) {
        List<Long> segments = userOwner.onSegmentsSteps().getSegments().stream().map(BaseSegment::getId)
                .collect(Collectors.toList());

        assertThat("сегмент отсутствует в списке владельца", segments, not(hasItem(segmentId)));
    }

}
