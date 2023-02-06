package ru.yandex.autotests.audience.management.tests.segments.client;

import java.io.InputStream;
import java.util.List;
import java.util.function.Supplier;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.Test;
import org.junit.runners.Parameterized.Parameter;

import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;

import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER;
import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER_2;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_INTERNAL_DMP;
import static ru.yandex.autotests.audience.errors.ManagementError.CLIENT_INVALID_SEGMENT;
import static ru.yandex.autotests.audience.errors.ManagementError.INCORRECT_SEGMENT_NAME_LENGTH;
import static ru.yandex.autotests.audience.errors.ManagementError.NOT_NULL;
import static ru.yandex.autotests.audience.errors.ManagementError.UPLOADING_LESS_UNIQUE_ELEMENTS;
import static ru.yandex.autotests.audience.management.tests.TestData.TOO_LONG_SEGMENT_NAME_LENGTH;
import static ru.yandex.autotests.audience.management.tests.TestData.confirmClientSegmentNegativeParams;
import static ru.yandex.autotests.audience.management.tests.TestData.getEmptyContent;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;

public abstract class AbstractConfirmClientSegmentNegativeTest {
    protected static final User UPLOADER = INTERNAL_DMP_UPLOADER;
    protected static final User ANOTHER_UPLOADER = INTERNAL_DMP_UPLOADER_2;
    protected static final UserSteps user = UserSteps.withUser(UPLOADER);
    protected static final User TARGET_USER = USER_FOR_INTERNAL_DMP;

    @Parameter
    public String description;

    @Parameter(1)
    public Long segmentId;

    @Parameter(2)
    public SegmentRequestUploading segmentRequest;

    @Parameter(3)
    public UserSteps userParam;

    @Parameter(4)
    public IExpectedError error;

    protected static List<Object[]> initAndGetParamsList(String segmentType,
                                                         Long createdSegmentId,
                                                         Long emptyFileSegmentId,
                                                         Supplier<SegmentRequestUploading> requestSupplier) {

        return ImmutableList.of(
                confirmClientSegmentNegativeParams(segmentType + " пустой name", createdSegmentId,
                        requestSupplier.get().withName(StringUtils.EMPTY),
                        UPLOADER, INCORRECT_SEGMENT_NAME_LENGTH),
                confirmClientSegmentNegativeParams(segmentType + " отсутствует name", createdSegmentId,
                        requestSupplier.get().withName(null), UPLOADER, NOT_NULL),
                confirmClientSegmentNegativeParams(segmentType + " слишком длинный name", createdSegmentId,
                        requestSupplier.get().withName(TOO_LONG_SEGMENT_NAME_LENGTH),
                        UPLOADER, INCORRECT_SEGMENT_NAME_LENGTH),
                confirmClientSegmentNegativeParams(segmentType + " отсутствует content_type", createdSegmentId,
                        requestSupplier.get().withContentType(null), UPLOADER, NOT_NULL),
                confirmClientSegmentNegativeParams(segmentType + " другой заливатель", createdSegmentId,
                        requestSupplier.get(), ANOTHER_UPLOADER, CLIENT_INVALID_SEGMENT),
                confirmClientSegmentNegativeParams(segmentType + " залит пустой файл", emptyFileSegmentId,
                        requestSupplier.get(), UPLOADER, UPLOADING_LESS_UNIQUE_ELEMENTS)
        );
    }

    protected static Long getCreateSegmentId(Supplier<InputStream> contentSupplier) {
        return user.onSegmentsSteps().uploadFileForInternal(contentSupplier.get(),
                ulogin(TARGET_USER)).getId();
    }

    protected static Long getEmptyFileSegmentId() {
        return user.onSegmentsSteps().uploadFileForInternal(getEmptyContent(),
                ulogin(TARGET_USER)).getId();
    }

    @Test
    public void checkTryConfirmSegment() {
        userParam.onSegmentsSteps().confirmClientSegmentAndExpectError(error, segmentId, segmentRequest);
    }

    public static void cleanUp(Long createdSegmentId, Long emptyFileSegmentId) {
        user.onSegmentsSteps().deleteClientSegment(createdSegmentId);
        user.onSegmentsSteps().deleteClientSegment(emptyFileSegmentId);
    }

}
