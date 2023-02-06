package ru.yandex.autotests.audience.management.tests.segments.client.yuid;

import java.io.InputStream;
import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.AfterClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;

import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.parameters.ModificationType;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.audience.SegmentContentType.EMAIL;
import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_INTERNAL_DMP;
import static ru.yandex.autotests.audience.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.audience.errors.ManagementError.CLIENT_INVALID_SEGMENT;
import static ru.yandex.autotests.audience.errors.ManagementError.MODIFICATION_TYPE_IS_ABSENT;
import static ru.yandex.autotests.audience.errors.ManagementError.MODIFY_PROCESSING_SEGMENT;
import static ru.yandex.autotests.audience.errors.ManagementError.NO_NEW_DATA_MODIFICATION;
import static ru.yandex.autotests.audience.errors.ManagementError.UPLOADING_LESS_UNIQUE_ELEMENTS;
import static ru.yandex.autotests.audience.errors.ManagementError.WRONG_CONTENT_TYPE;
import static ru.yandex.autotests.audience.management.tests.TestData.YUID_SEGMENT_BY_UPLOADER_2;
import static ru.yandex.autotests.audience.management.tests.TestData.YUID_SEGMENT_FOR_MODIFY_DATA;
import static ru.yandex.autotests.audience.management.tests.TestData.getContent;
import static ru.yandex.autotests.audience.management.tests.TestData.getContentForAddition;
import static ru.yandex.autotests.audience.management.tests.TestData.getContentForSubtraction;
import static ru.yandex.autotests.audience.management.tests.TestData.getYuidContent;
import static ru.yandex.autotests.audience.management.tests.TestData.getYuidUploadingSegment;
import static ru.yandex.autotests.audience.management.tests.TestData.modifyDataInYuidSegmentParams;
import static ru.yandex.autotests.audience.parameters.ModificationType.ADDITION;
import static ru.yandex.autotests.audience.parameters.ModificationType.REPLACE;
import static ru.yandex.autotests.audience.parameters.ModificationType.SUBTRACTION;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters.makeParameters;

/**
 * Created by ava1on on 19.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.INTERNAL_DMP
})
@Title("Internal dmp: изменение данных в сегменте с типом «yuid» (негативные тесты)")
@RunWith(Parameterized.class)
public class ModifyDataInYuidSegmentNegativeTest {
    private static final User UPLOADER = INTERNAL_DMP_UPLOADER;
    private static final UserSteps user = UserSteps.withUser(UPLOADER);
    private static final User TARGET_USER = USER_FOR_INTERNAL_DMP;

    private static Long processingSegmentId;

    @Parameter
    public String description;

    @Parameter(1)
    public Long segmentId;

    @Parameter(2)
    public InputStream content;

    @Parameter(3)
    public ModificationType modificationType;

    @Parameter(4)
    public UserSteps userParam;

    @Parameter(5)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        processingSegmentId = user.onSegmentsSteps().uploadFileForInternal(getYuidContent(),ulogin(TARGET_USER)).getId();
        user.onSegmentsSteps().confirmClientSegment(processingSegmentId, getYuidUploadingSegment());

        return ImmutableList.of(
                modifyDataInYuidSegmentParams("сегмент не в статусе готов", processingSegmentId,
                        getContentForAddition(), ADDITION, UPLOADER, MODIFY_PROCESSING_SEGMENT),
                modifyDataInYuidSegmentParams("отсутствует modification_type", YUID_SEGMENT_FOR_MODIFY_DATA,
                        getContentForAddition(), null, UPLOADER, MODIFICATION_TYPE_IS_ABSENT),
                modifyDataInYuidSegmentParams("нет прав \"заливателя\"", YUID_SEGMENT_FOR_MODIFY_DATA,
                        getContentForAddition(), ADDITION, SIMPLE_USER, ACCESS_DENIED),
                modifyDataInYuidSegmentParams("загружал другой заливатель", YUID_SEGMENT_BY_UPLOADER_2,
                        getContentForSubtraction(), SUBTRACTION, UPLOADER, CLIENT_INVALID_SEGMENT),
                modifyDataInYuidSegmentParams("нет новых записей для сегмента", YUID_SEGMENT_FOR_MODIFY_DATA,
                        getYuidContent(), REPLACE, UPLOADER, NO_NEW_DATA_MODIFICATION),
                modifyDataInYuidSegmentParams("удаление всех записей", YUID_SEGMENT_FOR_MODIFY_DATA,
                        getYuidContent(), SUBTRACTION, UPLOADER, UPLOADING_LESS_UNIQUE_ELEMENTS),
                modifyDataInYuidSegmentParams("другой тип контента", YUID_SEGMENT_FOR_MODIFY_DATA,
                        getContent(EMAIL, false, "\n"), ADDITION, UPLOADER, WRONG_CONTENT_TYPE)
        );
    }

    @Test
    public void checkTryModifyDataInYuidSegment() {
        userParam.onSegmentsSteps().modifyClientSegmentAndExpectError(error, segmentId, content,
                makeParameters().append(modificationType));
    }

    @AfterClass
    public static void cleanUp() {
        user.onSegmentsSteps().deleteClientSegment(processingSegmentId);
    }
}
