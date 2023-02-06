package ru.yandex.autotests.audience.management.tests.segments.lookalike;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.LookalikeSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.metrika.audience.pubapi.SegmentRequestLookalike;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.lang.Boolean.FALSE;
import static java.lang.Boolean.TRUE;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.management.tests.TestData.getExpectedSegment;
import static ru.yandex.autotests.audience.management.tests.TestData.getLookalikeSegment;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 21.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.LAL
})
@Title("Lookalike: проверка установки флагов Distribution")
@RunWith(Parameterized.class)
public class DistributionFlagTest {
    private final UserSteps user = UserSteps.withUser(USER_FOR_LOOKALIKE);

    private SegmentRequestLookalike segmentRequest;
    private LookalikeSegment createdSegment;
    private Long segmentId;

    @Parameter
    public Boolean geoDistribution;

    @Parameter(1)
    public Boolean deviceDistribution;

    @Parameterized.Parameters(name = "Опции lookalike - гео: {0}, device: {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(TRUE, FALSE, null)
                .values(TRUE, FALSE, null)
                .build();
    }

    @Before
    public void setup() {
        segmentRequest = getLookalikeSegment(geoDistribution, deviceDistribution);
        createdSegment = user.onSegmentsSteps().createLookalike(segmentRequest);
        segmentId = createdSegment.getId();
    }

    @Test
    public void createdSegmentTest() {
        assertThat("созданный сегмент эквивалентен создаваемому", createdSegment,
                equivalentTo(getExpectedSegment(segmentRequest)));
    }

    @After
    public void tearDown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
