package ru.yandex.autotests.audience.management.tests.audience_crypta_sender;

import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.audience.data.users.Users.AUDIENCE_CRYPTA_SENDER_CREATOR;
import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER;
import static ru.yandex.autotests.audience.management.tests.TestData.getCryptaIdContent;
import static ru.yandex.autotests.audience.management.tests.TestData.getCryptaIdUploadingSegment;
import static ru.yandex.autotests.audience.management.tests.TestData.getExpectedSegment;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;

@Features(Requirements.Feature.AudienceCryptaSender)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.INTERNAL_DMP
})
@Title("Internal dmp: создание сегмента с типом «crypta_id»")
public class CreateCryptaIdSegmentCryptaSenderTest {
    private static final User TARGET_USER = AUDIENCE_CRYPTA_SENDER_CREATOR;
    private static final UserSteps userUploader = UserSteps.withUser(INTERNAL_DMP_UPLOADER);

    private static SegmentRequestUploading segmentRequest;
    private static UploadingSegment segment;

    @BeforeClass
    public static void init() {
        Long segmentId = userUploader.onSegmentsSteps().uploadFileForInternal(getCryptaIdContent(),
                ulogin(TARGET_USER)).getId();
        segmentRequest = getCryptaIdUploadingSegment();
        segment = userUploader.onSegmentsSteps().confirmClientSegment(segmentId, segmentRequest);
    }

    @Test
    public void checkCreatedSegment() {
        assertThat("созданный сегмент эквивалентен создаваемому", segment,
                equivalentTo(getExpectedSegment(segmentRequest)));
    }
}
