package ru.yandex.autotests.metrika.tests.ft.management.segments.lifecycle;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getSegmentName;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 10.11.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Изменение сегмента")
public class EditSegmentTest {

    private static final String ORIGINAL_EXPRESSION = "ym:s:regionCityName=='Москва'";
    private static final String MODIFIED_EXPRESSION = "ym:s:regionCityName=='Санкт-Петербург'";

    private static UserSteps user;
    private String ORIGINAL_NAME;
    private String MODIFIED_NAME;

    private Segment segment;
    private static Long counterId;
    private Long segmentId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();

        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Before
    public void setup() {
        ORIGINAL_NAME = getSegmentName();
        MODIFIED_NAME = getSegmentName();

        segment = new Segment()
                .withName(ORIGINAL_NAME)
                .withExpression(ORIGINAL_EXPRESSION);

        segmentId = user.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, segment).getSegmentId();
    }

    @Test
    public void segmentsLifecycleEditNameTest() {

        segment.setName(MODIFIED_NAME);

        user.onManagementSteps().onSegmentsSteps().editSegmentAndExpectSuccess(counterId, segmentId, segment);

        Segment segmentModified = user.onManagementSteps().onSegmentsSteps()
                .getSegmentAndExpectSuccess(counterId, segmentId);

        assertThat("имя сегмента изменено", segmentModified,
                having(on(Segment.class).getName(), equalTo(MODIFIED_NAME)));
    }

    @Test
    public void segmentsLifecycleEditFilterTest() {

        segment.setExpression(MODIFIED_EXPRESSION);

        user.onManagementSteps().onSegmentsSteps().editSegmentAndExpectSuccess(counterId, segmentId, segment);

        Segment segmentModified = user.onManagementSteps().onSegmentsSteps()
                .getSegmentAndExpectSuccess(counterId, segmentId);

        assertThat("выражение фильтра сегмента изменено", segmentModified,
                having(on(Segment.class).getExpression(), equalTo(MODIFIED_EXPRESSION)));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
