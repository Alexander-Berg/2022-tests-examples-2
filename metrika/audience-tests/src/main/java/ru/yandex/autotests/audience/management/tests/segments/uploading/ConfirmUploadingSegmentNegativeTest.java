package ru.yandex.autotests.audience.management.tests.segments.uploading;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.io.InputStream;
import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.audience.SegmentContentType.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 25.10.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.UPLOADING
})
@Title("Uploading: подтверждение сегмента (негативные тесты)")
@RunWith(Parameterized.class)
public class ConfirmUploadingSegmentNegativeTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    private Long segmentId;

    @Parameter
    public String description;

    @Parameter(1)
    public InputStream content;

    @Parameter(2)
    public SegmentRequestUploading segmentRequest;

    @Parameter(3)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                toArray("пустой name", getContent(CRM, false),
                        getUploadingSegment(CRM, false).withName(StringUtils.EMPTY), INCORRECT_SEGMENT_NAME_LENGTH),
                toArray("отсутствует name", getContent(IDFA_GAID, false),
                        getUploadingSegment(IDFA_GAID, false).withName(null), NOT_NULL),
                toArray("слишком длинный name", getContent(CRM, true),
                        getUploadingSegment(CRM, true).withName(TOO_LONG_SEGMENT_NAME_LENGTH),
                        INCORRECT_SEGMENT_NAME_LENGTH),
                toArray("отсутствует content_type", getContent(CRM, true),
                        getUploadingSegment(CRM, true).withContentType(null), NOT_NULL),
                toArray("запрос без body", getContent(CRM, true), null, NOT_NULL),
                toArray("пустой файл", getEmptyContent(), getUploadingSegment(CRM, true),
                        UPLOADING_LESS_UNIQUE_ELEMENTS),
                toArray("не совпадают тип и контент", getContent(CRM, false), getUploadingSegment(MAC, false),
                        UPLOADING_LESS_UNIQUE_ELEMENTS)
        );
    }

    @Before
    public void setup() {
        segmentId = user.onSegmentsSteps().uploadFile(content).getId();
    }

    @Test
    public void checkTryConfirmUploadingSegmentTest() {
        user.onSegmentsSteps().confirmSegmentAndExpectError(error, segmentId, segmentRequest);
    }

    @After
    public void cleanUp() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
