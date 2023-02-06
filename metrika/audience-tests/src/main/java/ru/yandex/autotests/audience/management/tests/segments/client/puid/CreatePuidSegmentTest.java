package ru.yandex.autotests.audience.management.tests.segments.client.puid;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.segments.client.AbstractCreateSegmentTest;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.audience.management.tests.TestData.getPuidContent;
import static ru.yandex.autotests.audience.management.tests.TestData.getPuidUploadingSegment;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.INTERNAL_DMP
})
@Title("Internal dmp: создание сегмента с типом «puid»")
public class CreatePuidSegmentTest extends AbstractCreateSegmentTest {

    private static SegmentRequestUploading segmentRequest;
    private static Long segmentId;
    private static UploadingSegment segment;

    @BeforeClass
    public static void init() {
        segmentId = userUploader.onSegmentsSteps().uploadFileForInternal(getPuidContent(),
                ulogin(TARGET_USER)).getId();
        segmentRequest = getPuidUploadingSegment();
        segment = userUploader.onSegmentsSteps().confirmClientSegment(segmentId, segmentRequest);
    }

    @Test
    public void checkCreatedSegment() {
        super.checkCreatedSegment(segment, segmentRequest);
    }

    @Test
    public void checkSegmentInTargetUserList() {
        super.checkSegmentInTargetUserList(segmentRequest);
    }

    @Test
    public void checkSegmentInUploaderList() {
        super.checkSegmentInUploaderList(segmentRequest);
    }

    @AfterClass
    public static void cleanUp() {
        AbstractCreateSegmentTest.cleanUp(segmentId);
    }
}
