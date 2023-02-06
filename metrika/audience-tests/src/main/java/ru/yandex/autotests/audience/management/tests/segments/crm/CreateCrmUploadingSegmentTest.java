package ru.yandex.autotests.audience.management.tests.segments.crm;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.SegmentContentType;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdStatGETSchema;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.data.wrappers.SegmentRequestUploadingWrapper;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.apache.commons.lang3.StringEscapeUtils.escapeJava;
import static org.apache.commons.lang3.StringEscapeUtils.unescapeJava;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.audience.data.wrappers.SegmentRequestUploadingWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.getExpectedSegment;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.CRM_UPLOADING
})
@Title("Uploading: создание CRM сегмента из файла")
@RunWith(Parameterized.class)
public class CreateCrmUploadingSegmentTest {

    private static final User OWNER = Users.SIMPLE_USER_2;

    private final UserSteps user = UserSteps.withUser(OWNER);

    private UploadingSegment createdSegment;
    private Long segmentId;

    @Parameter
    public SegmentRequestUploadingWrapper segmentWrapper;

    @Parameter(1)
    public String delimiter;

    @Parameters(name = "{0}, разделитель: \"{1}\"")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(
                        requestUploading(false),
                        requestUploading(true)
                )
                .values(
                        escapeJava("\n"),
                        escapeJava("\r"),
                        escapeJava("\r\n")
                )
                .build();
    }

    @Before
    public void setup() {
        UploadingSegment notConfirmedSegment = user.onSegmentsSteps().uploadCsvFile(
                TestData.getContent(SegmentContentType.CRM, segmentWrapper.get().getHashed(), unescapeJava(delimiter)));
        segmentId = notConfirmedSegment.getId();
        createdSegment = user.onSegmentsSteps().confirmSegment(segmentId, segmentWrapper.get());
    }

    @Test
    public void createdSegmentTest() {
        assertThat("созданный сегмент эквивалентем создаваемому", createdSegment,
                equivalentTo(getExpectedSegment(segmentWrapper.get())));
    }

    @Test
    public void statSegmentTest() {
        V1ManagementSegmentSegmentIdStatGETSchema stat = user.onSegmentsSteps().getStat(segmentId);

        assertThat("созданный сегмент данных не содержит", stat.getNoData(), equalTo(true));
    }

    @Test
    public void getSegmentsTest() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("созданный сегмент присутствует в списке сегментов", segments,
                hasBeanEquivalent(UploadingSegment.class, getExpectedSegment(segmentWrapper.get())));
    }

    @After
    public void teardown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }

    private static SegmentRequestUploadingWrapper requestUploading(boolean isHashed) {
        return wrap(TestData.getUploadingSegment(SegmentContentType.CRM, isHashed));
    }
}
