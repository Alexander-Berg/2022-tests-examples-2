package ru.yandex.autotests.audience.management.tests.segments.client.puid;

import java.util.Collection;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.management.tests.segments.client.AbstractUploadSegmentNegativeTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.INTERNAL_DMP
})
@Title("Internal dmp: загрузка файла для сегмента с типом «puid» (негативные тесты)")
@RunWith(Parameterized.class)
public class UploadPuidSegmentNegativeTest extends AbstractUploadSegmentNegativeTest {

    @Parameterized.Parameters(name = "{0}: {4}")
    public static Collection<Object[]> createParameters() {
        return getParams(TestData::getPuidContent);
    }

    @Test
    public void checkTryUploadFileForPuidSegment() {
        userParamUploader.onSegmentsSteps().uploadFileForInternalAndExpectError(error, content, ulogin(userParam));
    }
}
