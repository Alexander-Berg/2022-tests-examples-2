package ru.yandex.autotests.audience.management.tests.segments.client.crypta_id;

import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.management.tests.segments.client.AbstractDeleteSegmentTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.INTERNAL_DMP
})
@Title("Internal dmp: удаление сегмента с типом «crypta_id»")
public class DeleteCryptaIdSegmentTest extends AbstractDeleteSegmentTest {

    private static Long segmentId;

    @BeforeClass
    public static void setup() {
        segmentId = init(TestData::getCryptaIdContent, TestData::getCryptaIdUploadingSegment);
    }

    @Test
    public void checkSegmentIsNotInListUploader() {
        checkSegmentIsNotInListUploader(segmentId);
    }

    @Test
    public void checkSegmentIsNotInListOwner() {
        checkSegmentIsNotInListOwner(segmentId);
    }
}
