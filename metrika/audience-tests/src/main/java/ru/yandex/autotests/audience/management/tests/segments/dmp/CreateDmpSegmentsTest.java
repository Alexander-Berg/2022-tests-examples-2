package ru.yandex.autotests.audience.management.tests.segments.dmp;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.SegmentRequestDmp;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;
import java.util.Map;

import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 01.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.DMP
})
@Title("Dmp: создание сегментов с типом «dmp»")
public class CreateDmpSegmentsTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    private static List<SegmentRequestDmp> segmentRequests;
    private static List<BaseSegment> createdSegments;
    private static List<Long> segmentsIds;

    @BeforeClass
    public static void setup() {
        segmentRequests = getDmpSegments(DMP_SEGMENTS_IDS.entrySet().stream()
                .filter(a -> a.getKey().startsWith("CreateDmpSegmentsTest"))
                .map(Map.Entry::getValue)
                .collect(toList()));
        createdSegments = user.onSegmentsSteps().createDmps(segmentRequests);
        segmentsIds = createdSegments.stream().map(BaseSegment::getId).collect(toList());
    }

    @Test
    public void  createdSegmentTest() {
        assertThat("созданные сегменты эквивалентны создаваемым", createdSegments,
                equivalentTo(getExpectedSegments(segmentRequests)));
    }

    @Test
    public void statSegmentsTest() {
        List<Boolean> stats = segmentsIds.stream()
                .map(a -> user.onSegmentsSteps().getStat(a).getNoData()).collect(toList());

        assertThat("созданные сегменты данных не содержат", stats, everyItem(equalTo(true)));
    }

    @Test
    public void getSegmentsTest() {
        List<BaseSegment> segments = user.onSegmentsSteps().getSegments();

        assertThat("созданные сегменты присутствуют в списке сегментов", createdSegments,
                everyItem(isIn(segments)));
    }

    @AfterClass
    public static void cleanUp() {
        segmentsIds.forEach(a -> user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(a));
    }
}
