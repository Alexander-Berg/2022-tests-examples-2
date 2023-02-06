package ru.yandex.autotests.audience.management.tests.segments.client.puid;

import java.util.Collection;

import org.junit.AfterClass;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.management.tests.segments.client.AbstractConfirmClientSegmentNegativeTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.INTERNAL_DMP
})
@Title("Internal dmp: подтверждение сегмента с типом «puid» (негативные тесты)")
@RunWith(Parameterized.class)
public class ConfirmPuidSegmentNegativeTest extends AbstractConfirmClientSegmentNegativeTest{

    private static Long createdSegmentId;
    private static Long emptyFileSegmentId;

    @Parameterized.Parameters(name = "{0}: {4}")
    public static Collection<Object[]> createParameters() {
        emptyFileSegmentId = getEmptyFileSegmentId();
        createdSegmentId = getCreateSegmentId(TestData::getPuidContent);
        return AbstractConfirmClientSegmentNegativeTest.initAndGetParamsList("puid",
                createdSegmentId, emptyFileSegmentId, TestData::getPuidUploadingSegment);
    }

    @AfterClass
    public static void cleanUp() {
        AbstractConfirmClientSegmentNegativeTest.cleanUp(createdSegmentId, emptyFileSegmentId);
    }
}
