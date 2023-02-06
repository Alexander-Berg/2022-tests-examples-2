package ru.yandex.autotests.audience.management.tests.segments.client.crypta_id;

import java.util.Collection;

import org.junit.AfterClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.management.tests.segments.client.AbstractEditSegmentNegativeTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.INTERNAL_DMP
})
@Title("Internal dmp: редактирование сегмента с типом «crypta_id» (негативные тесты)")
@RunWith(Parameterized.class)
public class EditCryptaIdSegmentNegativeTest extends AbstractEditSegmentNegativeTest {

    private static Long targetSegmentId;

    @Parameterized.Parameters(name = "{0}: {3}")
    public static Collection<Object[]> createParameters() {
        targetSegmentId = uploadSegment(TestData::getCryptaIdContent);
        UploadingSegment segment = confirmSegment(targetSegmentId, TestData::getCryptaIdUploadingSegment);
        return getParams(segment);
    }

    @Test
    public void test() {
        user.onSegmentsSteps().editClientSegmentAndExpectError(error, segmentId, segmentToChange);
    }

    @AfterClass
    public static void cleanUp() {
        cleanUp(targetSegmentId);
    }

}
