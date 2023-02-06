package ru.yandex.autotests.audience.management.tests.segments.client.yuid;

import java.io.InputStream;
import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;

import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.parameters.ModificationType;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.Users.INTERNAL_DMP_UPLOADER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_INTERNAL_DMP;
import static ru.yandex.autotests.audience.management.tests.TestData.YUID_SEGMENTS_FOR_MODIFICATION;
import static ru.yandex.autotests.audience.management.tests.TestData.getContentForAddition;
import static ru.yandex.autotests.audience.management.tests.TestData.getContentForReplace;
import static ru.yandex.autotests.audience.management.tests.TestData.getContentForSubtraction;
import static ru.yandex.autotests.audience.parameters.ModificationType.ADDITION;
import static ru.yandex.autotests.audience.parameters.ModificationType.REPLACE;
import static ru.yandex.autotests.audience.parameters.ModificationType.SUBTRACTION;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;

/**
 * Created by ava1on on 09.06.17.
 */
@Features({Requirements.Feature.MANAGEMENT, "METRIQA-1409"})
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.INTERNAL_DMP
})
@Title("Internal dmp: изменение данных в сегменте с типом «yuid»")
@RunWith(Parameterized.class)
public class ExcludeModifyDataInYuidSegmentTest {
    private final UserSteps userUploader = UserSteps.withUser(INTERNAL_DMP_UPLOADER);
    private final User targetUser = USER_FOR_INTERNAL_DMP;

    private UploadingSegment modifiedSegment;

    @Parameter
    public ModificationType modificationType;

    @Parameter(1)
    public Long segmentToModify;

    @Parameter(2)
    public InputStream content;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                toArray(ADDITION, YUID_SEGMENTS_FOR_MODIFICATION.get(0), getContentForAddition()),
                toArray(SUBTRACTION, YUID_SEGMENTS_FOR_MODIFICATION.get(1), getContentForSubtraction()),
                toArray(REPLACE, YUID_SEGMENTS_FOR_MODIFICATION.get(2), getContentForReplace())
        );
    }

    @Before
    public void setup() {
        modifiedSegment = userUploader.onSegmentsSteps().modifyClientSegment(segmentToModify,
               content, modificationType);
    }

    @Test
    public void checkModifyYuidSegmentData() {
        List<BaseSegment> segments = userUploader.onSegmentsSteps().getInternalSegments(ulogin(targetUser));

        assertThat("сегмент с измененными данными присутсвует в списке", segments,
                hasBeanEquivalent(UploadingSegment.class, modifiedSegment));
    }
}
