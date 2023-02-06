package ru.yandex.autotests.metrika.tests.ft.management.segments.type;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.api.management.client.segments.SegmentSource;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.matchers.SegmentMatchers.segmentSourceEqualTo;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sonick on 14.09.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Тесты на проверку segment_source сегмента")
public class CheckSegmentSourceTest {
    private static UserSteps user;

    private String expression = dimension("ym:s:regionCityName").equalTo("Москва").build();

    private static Segment apiSegment;
    private static Segment uiSegment;
    private static Segment addedUiSegment;
    private static Segment addedApiSegment;
    private static Long counterId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();

        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Before
    public void setup() {
        apiSegment = getDefaultSegment();
        uiSegment = getDefaultSegment();

        addedApiSegment = user.onManagementSteps().onApiSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, apiSegment);
        addedUiSegment = user.onManagementSteps().onInterfaceSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, uiSegment);
    }

    @Test
    public void checkSegmentSourceInterfaceTest() {
        assertThat("тип созданного сегмента UI соответствует segment_source 'interface'", addedUiSegment,
                segmentSourceEqualTo(SegmentSource.INTERFACE));
    }

    @Test
    public void checkSegmentSourceApiTest() {
        assertThat("тип созданного сегмента API соответствует segment_source 'api'", addedApiSegment,
                segmentSourceEqualTo(SegmentSource.API));
    }

    @Test
    public void checkViewInterfaceSegmentSourceApiTest() {
        Segment segment = user.onManagementSteps().onApiSegmentsSteps()
                .getSegmentAndExpectSuccess(counterId, addedUiSegment.getSegmentId());

        assertThat("тип сегмента UI при просмотре ручкой API соответствует segment_source 'api'", segment,
                segmentSourceEqualTo(SegmentSource.INTERFACE));
    }

    @Test
    public void checkChangedSegmentSourceApiTest() {
        addedUiSegment.setExpression(expression);
        Segment modifiedSegment = user.onManagementSteps().onApiSegmentsSteps()
                .editSegmentAndExpectSuccess(counterId, addedUiSegment.getSegmentId(), addedUiSegment);

        assertThat("тип измененного сегмента UI изменился с 'interface' на 'api'", modifiedSegment,
                segmentSourceEqualTo(SegmentSource.API));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
