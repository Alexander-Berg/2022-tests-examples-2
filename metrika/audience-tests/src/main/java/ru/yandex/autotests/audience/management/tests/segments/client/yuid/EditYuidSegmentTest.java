package ru.yandex.autotests.audience.management.tests.segments.client.yuid;

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
@Title("Internal dmp: редактирование сегмента с типом «yuid»")
public class EditYuidSegmentTest extends AbstractEditSegmentTest {

    private Long segmentId;
    private UploadingSegment createdSegment;

    @Before
    public void setup() {
        segmentId = uploadSegment(TestData::getYuidContent);
        createdSegment = confirmSegment(segmentId, TestData::getYuidUploadingSegment);
    }

    @Test
    public void checkEditYuidSegment() {
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
