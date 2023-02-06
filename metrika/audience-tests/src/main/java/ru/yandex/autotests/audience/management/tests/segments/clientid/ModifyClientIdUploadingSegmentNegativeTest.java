package ru.yandex.autotests.audience.management.tests.segments.clientid;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.parameters.ModificationType;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.io.InputStream;
import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.getClientIdContentForAddition;
import static ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.audience.parameters.ModificationType.ADDITION;
import static ru.yandex.autotests.audience.steps.UserSteps.withUser;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.CLIENTID_UPLOADING
})
@Title("Uploading: изменение данных в сегменте по ClientId Метрики, созданного из файла (негативные тесты)")
@RunWith(Parameterized.class)
public class ModifyClientIdUploadingSegmentNegativeTest {

    private static final User UPLOADER = SIMPLE_USER_2;
    private static final User BAD_USER = SIMPLE_USER;
    private static final UserSteps owner = withUser(UPLOADER);

    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public Long segmentId;

    @Parameterized.Parameter(2)
    public InputStream content;

    @Parameterized.Parameter(3)
    public ModificationType modificationType;

    @Parameterized.Parameter(4)
    public User user;

    @Parameterized.Parameter(5)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        UploadingSegment notConfirmedSegment = owner.onSegmentsSteps().uploadFile(TestData.getClientIdContent());
        Long processingSegmentId = notConfirmedSegment.getId();

        owner.onSegmentsSteps().confirmClientIdSegment(processingSegmentId,
                TestData.getClientIdSegmentRequestUploading());

        return ImmutableList.of(
                toArray("сегмент не в статусе готов", processingSegmentId,
                        getClientIdContentForAddition(), ADDITION, UPLOADER, MODIFY_PROCESSING_SEGMENT),
                toArray("отсутствует modification_type", processingSegmentId,
                        getClientIdContentForAddition(), null, UPLOADER, MODIFICATION_TYPE_IS_ABSENT),
                toArray("нет прав \"заливателя\"", processingSegmentId,
                        getClientIdContentForAddition(), ADDITION, BAD_USER, ACCESS_DENIED)
        );
    }

    @Test
    public void checkTryModifyDataInClientIdSegment() {
        withUser(user).onSegmentsSteps().modifyUploadedFileAndExpectError(error, segmentId, content,
                makeParameters().append(modificationType));
    }

    @After
    public void teardown() {
        owner.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }

}
