package ru.yandex.autotests.audience.management.tests.segments.crm;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
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
import static ru.yandex.audience.SegmentContentType.CRM;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.errors.ManagementError.CRM_HEADER_VALIDATION_ERROR;
import static ru.yandex.autotests.audience.errors.ManagementError.INVALID_DATA_FORMAT;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.CRM_UPLOADING
})
@Title("Uploading: подтверждение CRM сегмента из файла (негативные тесты)")
@RunWith(Parameterized.class)
public class ConfirmCrmUploadingSegmentNegativeTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    @Parameter
    public String description;

    @Parameter(1)
    public InputStream content;

    @Parameter(2)
    public IExpectedError error;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
//                commented due to https://st.yandex-team.ru/AUDIENCE-535
//                toArray("отсутствует колонка email", getCrmContentWithoutEmail(), CRM_HEADER_VALIDATION_ERROR),
//                toArray("отсутствует колонка phone", getCrmContentWithoutPhone(), CRM_HEADER_VALIDATION_ERROR),
                toArray("не правильный формат в строке", getCrmContentNoParse(), INVALID_DATA_FORMAT)
        );
    }

    @Test
    public void checkTryConfirmUploadingSegmentTest() {
        user.onSegmentsSteps().uploadCsvFileAndExpectError(error, content);
    }
}
