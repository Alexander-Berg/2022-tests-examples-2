package ru.yandex.autotests.audience.management.tests.segments.clientid;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.AfterClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.ClientIdSegmentRequestUploading;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER_2;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.audience.steps.UserSteps.withUser;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.CLIENTID_UPLOADING
})
@Title("Uploading: подтверждение сегмента по ClientId Метрики из файла (негативные тесты)")
@RunWith(Parameterized.class)
public class ConfirmClientIdUploadingSegmentNegativeTest {
    private static final User UPLOADER = SIMPLE_USER_2;
    private static final User ANOTHER_UPLOADER = INTERNAL_DMP_UPLOADER_2;
    private static final UserSteps user = withUser(UPLOADER);

    private static Long newValidSegmentId;
    private static Long newEmptySegmentId;

    @Parameter
    public String description;

    @Parameter(1)
    public Long segmentId;

    @Parameter(2)
    public ClientIdSegmentRequestUploading segmentRequest;

    @Parameter(3)
    public User userParam;

    @Parameter(4)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {4}")
    public static Collection<Object[]> createParameters() {
        newValidSegmentId = user.onSegmentsSteps().uploadFile(getClientIdContent()).getId();
        newEmptySegmentId = user.onSegmentsSteps().uploadFile(getEmptyContent()).getId();

        return ImmutableList.of(
                toArray("пустой name", newValidSegmentId,
                        getClientIdSegmentRequestUploading().withName(StringUtils.EMPTY),
                        UPLOADER, INCORRECT_SEGMENT_NAME_LENGTH),
                toArray("отсутствует name", newValidSegmentId,
                        getClientIdSegmentRequestUploading().withName(null),
                        UPLOADER, NOT_NULL),
                toArray("слишком длинный name", newValidSegmentId,
                        getClientIdSegmentRequestUploading().withName(TOO_LONG_SEGMENT_NAME_LENGTH),
                        UPLOADER, INCORRECT_SEGMENT_NAME_LENGTH),
                toArray("отсутствует counter_id", newValidSegmentId,
                        getClientIdSegmentRequestUploading().withCounterId(null),
                        UPLOADER, NOT_NULL),
                toArray("нет доступа", newValidSegmentId,
                        getClientIdSegmentRequestUploading(),
                        ANOTHER_UPLOADER, ACCESS_DENIED),
                toArray("залит пустой файл", newEmptySegmentId,
                        getClientIdSegmentRequestUploading(),
                        UPLOADER, UPLOADING_LESS_UNIQUE_ELEMENTS),
                toArray("нет доступа к счетчику", newValidSegmentId,
                        getClientIdSegmentRequestUploading().withCounterId(101024L),
                        UPLOADER, ACCESS_DENIED_FOR_COUNTER),
                toArray("нет доступа к счетчику 0", newValidSegmentId,
                        getClientIdSegmentRequestUploading().withCounterId(0L),
                        UPLOADER, ACCESS_DENIED_FOR_COUNTER),
                toArray("нет доступа к несуществующему счетчику", newValidSegmentId,
                        getClientIdSegmentRequestUploading().withCounterId(12345L),
                        UPLOADER, ACCESS_DENIED_FOR_COUNTER)
        );
    }

    @Test
    public void checkTryConfirmClientIdSegment() {
        withUser(userParam).onSegmentsSteps().confirmClientIdSegmentAndExpectError(error, segmentId, segmentRequest);
    }

    @AfterClass
    public static void cleanUp() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(newValidSegmentId);
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(newEmptySegmentId);
    }
}
