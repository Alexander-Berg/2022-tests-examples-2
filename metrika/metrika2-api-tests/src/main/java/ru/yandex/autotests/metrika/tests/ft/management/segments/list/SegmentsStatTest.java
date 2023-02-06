package ru.yandex.autotests.metrika.tests.ft.management.segments.list;

import org.hamcrest.Matcher;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.management.v1.segments.enums.SegmentsSortEnum;
import ru.yandex.autotests.metrika.data.parameters.management.v1.SegmentsStatParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.segments.SegmentsServiceInnerSegmentUsers;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getSegments;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 02.11.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Получение списка сегментов и статистики")
@RunWith(Parameterized.class)
public class SegmentsStatTest {

    private static final UserSteps user = new UserSteps();

    private static final Integer NUMBER_OF_SEGMENTS = 3;

    private static Long counterId;

    @Parameterized.Parameter(0)
    public SegmentsSortEnum sort;

    @Parameterized.Parameter(1)
    public Boolean reverse;

    @Parameterized.Parameter(2)
    public Integer offset;

    @Parameterized.Parameter(3)
    public Integer perPage;

    @Parameterized.Parameters(name = "sort: {0}; reverse: {1}; offset: {2}; per_page: {3}")
    public static Collection<Object[]> createParameters() {
        return asList(
                toArray(null, null, null, null),
                toArray(SegmentsSortEnum.CREATE_DATE, Boolean.FALSE, 1, 0),
                toArray(SegmentsSortEnum.MONTH_USERS, Boolean.TRUE, 2, 1),
                toArray(SegmentsSortEnum.NAME, null, null, null),
                toArray(SegmentsSortEnum.RETARGETING, null, null, null),
                toArray(SegmentsSortEnum.WEEK_USERS, null, null, null));
    }

    @BeforeClass
    public static void init() {
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();

        user.onManagementSteps().onSegmentsSteps().createSegments(counterId, getSegments(NUMBER_OF_SEGMENTS));
    }

    @Test
    public void segmentStatTest() {
        List<SegmentsServiceInnerSegmentUsers> segments = user.onManagementSteps().onSegmentsSteps()
                .getSegmentsStatAndExpectSuccess(
                        counterId,
                        new SegmentsStatParameters()
                                .withSort(sort)
                                .withReverse(reverse)
                                .withPerPage(perPage)
                                .withOffset(offset));

        assertThat("Количество сегментов в списке совпадает с ожидаемым", segments,
                iterableWithSize(getSizeMatcher()));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }

    private Matcher<Integer> getSizeMatcher() {
        return perPage != null
                ? equalTo(perPage)
                : equalTo(NUMBER_OF_SEGMENTS - Optional.ofNullable(offset).orElse(1) + 1);
    }
}
