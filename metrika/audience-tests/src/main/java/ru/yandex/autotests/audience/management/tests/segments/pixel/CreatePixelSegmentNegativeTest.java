package ru.yandex.autotests.audience.management.tests.segments.pixel;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.AfterClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.SegmentRequestPixel;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_FOR_LOOKALIKE;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 10.05.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.PIXEL
})
@Title("Пиксель: создание сегмента с типом «pixel» (негативные тесты)")
@RunWith(Parameterized.class)
public class CreatePixelSegmentNegativeTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER);
    private static final UserSteps userOwner = UserSteps.withUser(USER_FOR_LOOKALIKE);

    private static Long anotherPixelId;

    @Parameter
    public String description;

    @Parameter(1)
    public SegmentRequestPixel segmentRequest;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        anotherPixelId = userOwner.onPixelsSteps().createPixel(getPixelName()).getId();

        return ImmutableList.of(
                createPixelSegmentNegativeParam("отсутствует параметр pixelId", getPixelSegment(null),
                        NOT_NULL),
                createPixelSegmentNegativeParam("пустое имя сегмента",
                        getPixelSegment().withName(StringUtils.EMPTY), INCORRECT_SEGMENT_NAME_LENGTH),
                createPixelSegmentNegativeParam("слишком длинное имя сегмента",
                        getPixelSegment().withName(TOO_LONG_SEGMENT_NAME_LENGTH), INCORRECT_SEGMENT_NAME_LENGTH),
                createPixelSegmentNegativeParam("отсутствует параметр name", getPixelSegment().withName(null),
                        NOT_NULL),
                createPixelSegmentNegativeParam("слишком большой period_length",
                        getPixelSegment().withPeriodLength(PIXEL_MAX_PERIOD_LENGTH + 1), TOO_BIG_PERIOD_LENGTH_PIXEL),
                createPixelSegmentNegativeParam("слишком маленький period_length",
                        getPixelSegment().withPeriodLength(PIXEL_MIN_PERIOD_LENGTH - 1), TOO_SMALL_PERIOD_LENGTH_PIXEL),
                createPixelSegmentNegativeParam("слишком маленький times_quantity",
                        getPixelSegment().withTimesQuantity(PIXEL_MIN_TIMES_QUANTITY - 1), INCORRECT_TIMES_QUANTITY_PIXEL),
                createPixelSegmentNegativeParam("слишком большой times_quantity",
                        getPixelSegment().withTimesQuantity(PIXEL_MAX_TIMES_QUANTITY + 1), TOO_BIG_TIMES_QUANTITY_PIXEL),
                createPixelSegmentNegativeParam("отсутствует параметр times_quantity",
                        getPixelSegment().withTimesQuantity(null), PIXEL_TIMES_QUANTITY_IS_ABSENT),
                createPixelSegmentNegativeParam("отсутствует параметр times_quantity_operation",
                        getPixelSegment().withTimesQuantityOperation(null), NO_TIMES_QUANTITY_OPERATION),
                createPixelSegmentNegativeParam("нет доступа к пикселю", getPixelSegment(anotherPixelId),
                        NO_ACCESS_TO_PIXEL)
        );
    }

    @Test
    public void checkTryCreatePixelSegment() {
        user.onSegmentsSteps().createPixelAndExpectError(error, segmentRequest);
    }

    @AfterClass
    public static void cleanUp() {
        userOwner.onPixelsSteps().deletePixelAndIgnoreStatus(anotherPixelId);
    }
}
