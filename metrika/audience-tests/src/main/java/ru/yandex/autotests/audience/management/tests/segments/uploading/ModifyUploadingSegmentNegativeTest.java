package ru.yandex.autotests.audience.management.tests.segments.uploading;

import org.junit.Test;

import ru.yandex.audience.SegmentContentType;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.parameters.ModificationType;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_UPLOADING_MODIFY;
import static ru.yandex.autotests.audience.errors.ManagementError.SEGMENT_IS_DELETED;
import static ru.yandex.autotests.audience.management.tests.TestData.UPLOADING_SEGMENT_DELETED;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.UPLOADING
})
@Title("Cегменты: изменение данных сегмента из файла (негативные тесты)")
public class ModifyUploadingSegmentNegativeTest {

    private final UserSteps user = UserSteps.withUser(USER_FOR_UPLOADING_MODIFY);

    @Test
    public void modifyDeletedSegment() {
        user.onSegmentsSteps().modifyUploadedFileAndExpectError(SEGMENT_IS_DELETED, UPLOADING_SEGMENT_DELETED, TestData.getContent(
                SegmentContentType.IDFA_GAID, false), ModificationType.ADDITION);
    }
}
