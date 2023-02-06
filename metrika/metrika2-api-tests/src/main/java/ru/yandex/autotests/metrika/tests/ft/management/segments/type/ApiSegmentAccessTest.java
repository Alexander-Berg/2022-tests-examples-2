package ru.yandex.autotests.metrika.tests.ft.management.segments.type;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.api.management.client.segments.SegmentsServiceInnerSegmentUsers;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.matchers.CompositeMatcher.matchEvery;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sonick on 12.09.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Тесты на доступ к сегментам API через ручки UI")
public class ApiSegmentAccessTest {

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
    public void getSegmentsListTest() {
        List<Segment> segments = user.onManagementSteps().onInterfaceSegmentsSteps()
                .getSegmentsAndExpectSuccess(counterId);

        assertThat("созданный сегмент UI присутствует и сегмент API отсутствует в списке UI сегментов счетчика",
                segments, matchEvery(hasItem(beanEquivalent(addedUiSegment)), (not(hasItem(beanEquivalent(addedApiSegment))))));
    }

    @Test
    public void getApiSegmentAccessTest() {
        user.onManagementSteps().onInterfaceSegmentsSteps()
                .getSegmentAndExpectError(ManagementError.NOT_FOUND, counterId, addedApiSegment.getSegmentId());
    }

    @Test
    public void editApiSegmentAccessTest() {
        addedApiSegment.setExpression(expression);
        user.onManagementSteps().onInterfaceSegmentsSteps()
                .editSegmentAndExpectError(ManagementError
                        .ACCESS_DENIED_TO_ANOTHER_SEGMENT_TYPE, counterId, addedApiSegment.getSegmentId(), addedApiSegment);
    }

    @Test
    public void deleteApiSegmentAccessTest() {
        user.onManagementSteps().onInterfaceSegmentsSteps()
                .deleteSegmentAndExpectError(ManagementError
                        .ACCESS_DENIED_TO_ANOTHER_SEGMENT_TYPE, counterId, addedApiSegment.getSegmentId());
    }

    @Test
    public void getApiSegmentByIdsTest() {
        List<Segment> segments = user.onManagementSteps().onInterfaceSegmentsSteps()
                .getSegmentsAndExpectSuccess(counterId, asList(addedApiSegment.getSegmentId()));

        assertThat("список сегментов пуст", segments, empty());
    }

    @Test
    public void getApiSegmentStatTest() {
        List<SegmentsServiceInnerSegmentUsers> segments = user.onManagementSteps().onInterfaceSegmentsSteps()
                .getSegmentsStatAndExpectSuccess(counterId);

        assertThat("сегмент API отсутствует в списке", segments,
                matchEvery(hasItem(having(on(SegmentsServiceInnerSegmentUsers.class).getSegmentId(),
                        equalTo(addedUiSegment.getSegmentId()))),
                        not(hasItem(having(on(SegmentsServiceInnerSegmentUsers.class).getSegmentId(),
                                equalTo(addedApiSegment.getSegmentId()))))));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }

}
