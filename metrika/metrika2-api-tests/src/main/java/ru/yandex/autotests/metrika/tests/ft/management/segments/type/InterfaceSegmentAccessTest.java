package ru.yandex.autotests.metrika.tests.ft.management.segments.type;

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

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.matchers.CompositeMatcher.matchEvery;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sonick on 12.09.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Тесты на доступ к сегментам UI через ручки API")
public class InterfaceSegmentAccessTest {
    private static UserSteps user;

    private static final String CHANGED_NAME = "Changed name";

    private static Segment apiSegment;
    private static Segment uiSegment;
    private static Segment addedUiSegment;
    private static Segment addedApiSegment;
    private static Segment changedSegment;
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

        changedSegment = new Segment()
                .withName(CHANGED_NAME);
    }

    @Test
    public void getSegmentsListTest() {
        List<Segment> segments = user.onManagementSteps().onApiSegmentsSteps()
                .getSegmentsAndExpectSuccess(counterId);

        assertThat("созданный сегмент API присутствует и сегмент UI отсутствует в списке API сегментов счетчика",
                segments, matchEvery(hasItem(beanEquivalent(addedApiSegment)), (not(hasItem(beanEquivalent(addedUiSegment))))));
    }

    @Test
    public void getUiSegmentAccessTest() {
        user.onManagementSteps().onApiSegmentsSteps()
                .getSegmentAndExpectSuccess(counterId, addedUiSegment.getSegmentId());

        assertThat("созданный сегмент UI присутствует в списке сегментов счетчика", addedUiSegment,
                beanEquivalent(uiSegment));
    }

    @Test
    public void editUiSegmentAccessTest() {
        Segment segmentModified = user.onManagementSteps().onApiSegmentsSteps()
                .editSegmentAndExpectSuccess(counterId, addedUiSegment.getSegmentId(), changedSegment);

        assertThat("имя сегмента изменено", segmentModified,
                having(on(Segment.class).getName(), equalTo(CHANGED_NAME)));
    }

    @Test
    public void deleteUiSegmentAccessTest() {
        user.onManagementSteps().onApiSegmentsSteps()
                .deleteSegmentAndExpectSuccess(counterId, addedUiSegment.getSegmentId());
        List<Segment> segments = user.onManagementSteps().onApiSegmentsSteps()
                .getSegmentsAndExpectSuccess(counterId);

        assertThat("созданный сегмент UI отсутствует в списке сегментов счетчика", segments,
                not(hasItem(beanEquivalent(addedUiSegment))));
    }

    @Test
    public void getUiSegmentByIdsTest() {
        List<Segment> segments = user.onManagementSteps().onApiSegmentsSteps()
                .getSegmentsAndExpectSuccess(counterId, asList(addedUiSegment.getSegmentId()));

        assertThat("сегмент UI присутствует в списке", segments,
                hasItem(beanEquivalent(uiSegment)));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }

}
