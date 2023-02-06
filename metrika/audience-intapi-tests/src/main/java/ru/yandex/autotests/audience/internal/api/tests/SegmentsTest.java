package ru.yandex.autotests.audience.internal.api.tests;

import com.google.common.collect.ImmutableList;
import org.hamcrest.Matcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.audience.internal.api.parameters.GetUsersParameters;
import ru.yandex.autotests.audience.internal.api.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.stream.Collectors;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.internal.api.IntapiFeatures.DIRECT;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by apuzikov on 04.07.17.
 */
@Features(DIRECT)
@Title("Проверка ручки охвата сегмента для директа")
@RunWith(Parameterized.class)
public class SegmentsTest {
    private final UserSteps user = new UserSteps();
    private final Long DAYS_LONG = 30L;

    private static final Matcher<Long> GREATER_THAN_ZERO = greaterThan(0L);
    private static final Matcher<Long> GREATER_THAN_OR_EQUAL_TO_ZERO = greaterThanOrEqualTo(0L);

    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public long segmentId;

    @Parameterized.Parameter(2)
    public Matcher<Long> matcher;

    @Parameterized.Parameter(3)
    public Matcher<Long> matcherSketched;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .addAll(SEGMENTS.entrySet().stream()
                        .map(k -> toArray(
                                "сегмент Аудитории: " + k.getKey().toString(),
                                k.getValue().getLeft(),
                                equalTo(k.getValue().getRight()),
                                // 10% ошибки - приемлемо
                                allOf(
                                        greaterThanOrEqualTo((long) (k.getValue().getRight() * 0.9)),
                                        lessThanOrEqualTo((long) (k.getValue().getRight() * 1.1))
                                )
                        ))
                        .collect(Collectors.toList()))
                .add(toArray("цель Метрики", METRIKA_GOAL_ID, GREATER_THAN_ZERO, GREATER_THAN_ZERO))
                .add(toArray("сегмент Метрики", METRIKA_SEGMENT_ID, GREATER_THAN_ZERO, GREATER_THAN_ZERO))
                .add(toArray("счетчик метрики", METRIKA_COUNTER_ID, GREATER_THAN_ZERO, GREATER_THAN_ZERO))
                .add(toArray("цель ecommerce", ECOMMERCE_GOAL_ID, GREATER_THAN_ZERO, GREATER_THAN_ZERO))
                .add(toArray("сегмент cdp", CDP_SEGMENT_WITH_DATA_GOAL_ID, GREATER_THAN_OR_EQUAL_TO_ZERO, GREATER_THAN_OR_EQUAL_TO_ZERO))
                .build();
    }

    @Test
    public void checkSegmentsSketchedCoverage() {
        Long actual = user.onDirectSteps()
                .getUsersSegmentsSketched(
                        new GetUsersParameters()
                                .withUid(segmentId)
                                .withDays(DAYS_LONG))
                .getResponse();

        assertThat("охват по скетчу примерно совпадает с ожидаемым", actual, matcherSketched);
    }
}
