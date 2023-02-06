package ru.yandex.autotests.audience.management.tests.audience_crypta_sender;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdStatGETSchema;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.ClientIdSegmentRequestUploading;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.apache.commons.lang3.StringEscapeUtils.unescapeJava;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.audience.management.tests.TestData.DEFAULT_DELIMITER;
import static ru.yandex.autotests.audience.management.tests.TestData.getExpectedSegment;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(Requirements.Feature.AudienceCryptaSender)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.CLIENTID_UPLOADING
})
@Title("Uploading: создание сегмента по ClientId Метрики из файла")
public class CreateClientIdUploadingSegmentCryptaSenderTest {

    private static final User OWNER = Users.AUDIENCE_CRYPTA_SENDER_CREATOR;

    private final UserSteps user = UserSteps.withUser(OWNER);

    private UploadingSegment createdSegment;
    private Long segmentId;
    private ClientIdSegmentRequestUploading segment;
    private String delimiter=DEFAULT_DELIMITER;

    @Before
    public void setup() {
        UploadingSegment notConfirmedSegment = user.onSegmentsSteps().uploadFile(
                TestData.getClientIdContentCryptaSender(unescapeJava(delimiter)));
        segmentId = notConfirmedSegment.getId();
        segment = TestData.getClientIdSegmentRequestUploadingCryptaSender();
        createdSegment = user.onSegmentsSteps().confirmClientIdSegment(segmentId, segment);
    }

    @Test
    public void createdSegmentTest() {
        assertThat("созданный сегмент эквивалентем создаваемому", createdSegment,
                equivalentTo(getExpectedSegment(segment)));
    }
}
