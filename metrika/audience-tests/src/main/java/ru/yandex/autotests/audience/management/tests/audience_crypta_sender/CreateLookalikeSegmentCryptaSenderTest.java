package ru.yandex.autotests.audience.management.tests.audience_crypta_sender;

import com.google.common.collect.ImmutableList;
import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.LookalikeSegment;
import ru.yandex.audience.SegmentType;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdStatGETSchema;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.Delegate;
import ru.yandex.metrika.audience.pubapi.SegmentRequestLookalike;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.audience.data.wrappers.DelegateWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.metrika.audience.pubapi.DelegateType.EDIT;

@Features(Requirements.Feature.AudienceCryptaSender)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.LAL
})
@Title("Lookalike: создание сегмента с типом «lookalike»")
@RunWith(Parameterized.class)
public class CreateLookalikeSegmentCryptaSenderTest {
    private static final UserSteps superUser = UserSteps.withUser(SUPER_USER);
    private static final UserSteps userLAL = UserSteps.withUser(AUDIENCE_CRYPTA_SENDER_CREATOR);

    private static Delegate delegate;

    private LookalikeSegment createdSegment;
    private Long segmentId;

    @Parameter
    public SegmentType type;

    @Parameter(1)
    public SegmentRequestLookalike segmentRequest;

    @Parameter(2)
    public UserSteps user;

    @Parameter(3)
    public String uLogin;

    @Parameter(4)
    public String notes;

    @Parameterized.Parameters(name = "тип исходного сегмента: {0}. notes: {4}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                createLookalikeParam(SegmentType.LOOKALIKE, getLookalikeSegment(SEGMENTS_CRYPTA_SENDER.get(SegmentType.LOOKALIKE)),
                        userLAL, null)
        );
    }

    @BeforeClass
    public static void init() {
        delegate = getDelegate(USER_FOR_LOOKALIKE, EDIT);
        superUser.onDelegatesSteps().createDelegate(wrap(delegate), ulogin(PIXEL_SEGMENT_OWNER));
    }

    @Before
    public void setup() {
        createdSegment = user.onSegmentsSteps().createLookalike(segmentRequest, ulogin(uLogin));
        segmentId = createdSegment.getId();
    }

    @Test
    public void createdSegmentTest() {
        assertThat("созданный сегмент эквивалентен создаваемому", createdSegment,
                equivalentTo(getExpectedSegment(segmentRequest)));
    }
}
