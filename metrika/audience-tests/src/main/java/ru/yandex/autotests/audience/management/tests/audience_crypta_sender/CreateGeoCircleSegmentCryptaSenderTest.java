package ru.yandex.autotests.audience.management.tests.audience_crypta_sender;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.geo.CircleGeoSegment;
import ru.yandex.audience.geo.GeoSegment;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdStatGETSchema;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.data.wrappers.SegmentRequestGeoCircleWrapper;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.management.tests.TestData;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.audience.data.wrappers.SegmentRequestGeoCircleWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.getExpectedSegment;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(Requirements.Feature.AudienceCryptaSender)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.GEO
})
@Title("Cегменты: создание сегмента с типом «геолокация»")
@RunWith(Parameterized.class)
public class CreateGeoCircleSegmentCryptaSenderTest {

    private static final User OWNER = Users.AUDIENCE_CRYPTA_SENDER_CREATOR;

    private final UserSteps user = UserSteps.withUser(OWNER);

    private GeoSegment createdSegment;
    private Long segmentId;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return Stream.of(GeoSegmentType.values())
                .map(t -> param(t))
                .collect(toList());
    }

    @Parameter
    public SegmentRequestGeoCircleWrapper segmentWrapper;

    @Before
    public void setup() {
        createdSegment = user.onSegmentsSteps().createGeo(segmentWrapper.get());
        segmentId = createdSegment.getId();
    }

    @Test
    public void createdSegmentTest() {
        assertThat("созданный сегмент эквивалентем создаваемому", createdSegment,
                equivalentTo(getExpectedSegment(segmentWrapper.get())));
    }

    private static Object[] param(GeoSegmentType type) {
        return toArray(wrap(TestData.getGeoCircleSegmentCryptaSender(type)));
    }
}
