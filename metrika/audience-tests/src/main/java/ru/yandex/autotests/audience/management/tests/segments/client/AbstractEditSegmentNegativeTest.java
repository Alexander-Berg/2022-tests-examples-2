package ru.yandex.autotests.audience.management.tests.segments.client;

import java.io.InputStream;
import java.util.List;
import java.util.function.Supplier;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.runners.Parameterized;

import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;

import static ru.yandex.autotests.audience.data.users.User.GEO_SEGMENT_ID;
import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_INTERNAL_DMP;
import static ru.yandex.autotests.audience.errors.ManagementError.CLIENT_INVALID_SEGMENT;
import static ru.yandex.autotests.audience.errors.ManagementError.INCORRECT_SEGMENT_NAME_LENGTH;
import static ru.yandex.autotests.audience.errors.ManagementError.NOT_NULL;
import static ru.yandex.autotests.audience.management.tests.TestData.TOO_LONG_SEGMENT_NAME_LENGTH;
import static ru.yandex.autotests.audience.management.tests.TestData.UPLOADING_SEGMENT_NAME_PREFIX;
import static ru.yandex.autotests.audience.management.tests.TestData.YUID_SEGMENT_BY_UPLOADER_2;
import static ru.yandex.autotests.audience.management.tests.TestData.editClientNegativeParams;
import static ru.yandex.autotests.audience.management.tests.TestData.getName;
import static ru.yandex.autotests.audience.management.tests.TestData.getSegmentToChange;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;

abstract public class AbstractEditSegmentNegativeTest {
    protected static final UserSteps user = UserSteps.withUser(INTERNAL_DMP_UPLOADER);
    protected static final User TARGET_USER = USER_FOR_INTERNAL_DMP;

    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public Long segmentId;

    @Parameterized.Parameter(2)
    public UploadingSegment segmentToChange;

    @Parameterized.Parameter(3)
    public IExpectedError error;

    protected static Long uploadSegment(Supplier<InputStream> content) {
        return user.onSegmentsSteps().uploadFileForInternal(content.get(), ulogin(TARGET_USER)).getId();
    }

    protected static UploadingSegment confirmSegment(Long segmentId,
                                                     Supplier<SegmentRequestUploading> uploadingSegment) {
        return user.onSegmentsSteps().confirmClientSegment(segmentId, uploadingSegment.get());
    }

    protected static List<Object[]> getParams(UploadingSegment segment) {
        return ImmutableList.of(
                editClientNegativeParams("пустой name", segment.getId(),
                        getSegmentToChange(segment, StringUtils.EMPTY), INCORRECT_SEGMENT_NAME_LENGTH),
                editClientNegativeParams("слишком длинный name", segment.getId(),
                        getSegmentToChange(segment, TOO_LONG_SEGMENT_NAME_LENGTH), INCORRECT_SEGMENT_NAME_LENGTH),
                editClientNegativeParams("отсутствует поле name", segment.getId(),
                        getSegmentToChange(segment, null), NOT_NULL),
                editClientNegativeParams("сегмент не того типа ", USER_FOR_INTERNAL_DMP.get(GEO_SEGMENT_ID),
                        getSegmentToChange(segment, getName(UPLOADING_SEGMENT_NAME_PREFIX)), CLIENT_INVALID_SEGMENT),
                editClientNegativeParams("другой заливатель", YUID_SEGMENT_BY_UPLOADER_2,
                        getSegmentToChange(segment, getName(UPLOADING_SEGMENT_NAME_PREFIX)), CLIENT_INVALID_SEGMENT)
        );
    }

    protected static void cleanUp(Long targetSegmentId) {
        user.onSegmentsSteps().deleteClientSegmentAndIgnoreStatus(targetSegmentId);
    }

}
