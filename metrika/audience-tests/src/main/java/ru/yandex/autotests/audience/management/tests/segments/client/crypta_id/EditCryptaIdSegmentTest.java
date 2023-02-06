package ru.yandex.autotests.audience.management.tests.segments.client.crypta_id;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.management.tests.segments.client.AbstractEditSegmentTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.INTERNAL_DMP
})
@Title("Internal dmp: редактирование сегмента с типом «crypta_id»")
public class EditCryptaIdSegmentTest extends AbstractEditSegmentTest {

    private Long segmentId;
    private UploadingSegment createdSegment;

    @Before
    public void setup() {
        segmentId = uploadSegment(TestData::getCryptaIdContent);
        createdSegment = confirmSegment(segmentId, TestData::getCryptaIdUploadingSegment);
    }

    @Test
    public void checkEditCryptaIdSegment() {
        checkEditSegment(createdSegment, segmentId);
    }

    @Test
    public void checkBoundaryNameLength() {
        checkBoundaryNameLength(createdSegment, segmentId);
    }

    @After
    public void cleanUp() {
        cleanUp(segmentId);
    }
}
