package ru.yandex.autotests.audience.management.tests.segments.lookalike;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.AfterClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.SegmentRequestLookalike;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.User.AUDIENCE_APPMETRICA_SEGMENT_ID;
import static ru.yandex.autotests.audience.data.users.User.AUDIENCE_METRIKA_SEGMENT_ID;
import static ru.yandex.autotests.audience.data.users.Users.USER_LOOKALIKE_NEGATIVE;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 22.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.LAL
})
@Title("Lookalike: создание сегмента с типом «lookalike» (негативные тесты)")
@RunWith(Parameterized.class)
public class CreateLookalikeSegmentNegativeTest {
    private static final User OWNER = USER_LOOKALIKE_NEGATIVE;
    private static final UserSteps user = UserSteps.withUser(OWNER);

    private static Long processingSegmentId = user.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.LAST)).getId();

    @Parameter()
    public SegmentRequestLookalike segmentRequest;

    @Parameter(1)
    public IExpectedError error;

    @Parameter(2)
    public String description;

    @Parameterized.Parameters(name = "{2}: {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                createLookalikeNegativeParam("исходный сегмент гео актуальный", createLookalikeForGeoLast(),
                        LOOKALIKE_FOR_GEO_LAST),
                createLookalikeNegativeParam("исходный сегмент dmp", createLookalikeForDmp(),
                        LOOKALIKE_FOR_DMP),
                createLookalikeNegativeParam("исходный сегмент в статусе «Мало данных»",
                        createLookalikeForFewData(), LOOKALIKE_NOT_PROCESSED_SOURCE),
                createLookalikeNegativeParam("нет доступа к исходному сегменту",
                        createLookalikeForNoAccess(), LOOKALIKE_NOT_OWNER_FOR_SOURCE),
                createLookalikeNegativeParam("исходный сегмент в статусе «Неактивен»",
                        createLookalikeForInactive(), LOOKALIKE_NOT_PROCESSED_SOURCE),
                createLookalikeNegativeParam("пустое имя сегмента",
                        getLookalikeSegment(StringUtils.EMPTY), INCORRECT_SEGMENT_NAME_LENGTH),
                createLookalikeNegativeParam("слишком длинное имя сегмента",
                        getLookalikeSegment(TOO_LONG_SEGMENT_NAME_LENGTH), INCORRECT_SEGMENT_NAME_LENGTH),
                createLookalikeNegativeParam("отсутствует параметр name",
                        getLookalikeSegment().withName(null), NOT_NULL),
                createLookalikeNegativeParam("исходный сегмент в статусе «Обрабатывается»",
                        getLookalikeSegment(processingSegmentId), LOOKALIKE_NOT_PROCESSED_SOURCE),
                createLookalikeNegativeParam("отсутствует параметр lookalike_link",
                        getLookalikeSegment().withLookalikeLink(null), NOT_NULL),
                createLookalikeNegativeParam("слишком большой lookalike_value",
                        getLookalikeSegment().withLookalikeValue(LOOKALIKE_PRECISION_MAX_VALUE + 1),
                        TOO_BIG_LOOKALIKE_VALUE),
                createLookalikeNegativeParam("слишком маленький lookalike_value",
                        getLookalikeSegment().withLookalikeValue(LOOKALIKE_PRECISION_MIN_VALUE - 1),
                        TOO_SMALL_LOOKALIKE_VALUE),
                createLookalikeNegativeParam("отсутствует параметр lookalike_value",
                        getLookalikeSegment().withLookalikeValue(null), NOT_NULL),
                createLookalikeNegativeParam("права только на чтение исходного объекта Метрики",
                        getLookalikeSegment(OWNER.get(AUDIENCE_METRIKA_SEGMENT_ID)), NO_ACCESS_TO_CREATE_LOOKALIKE),
                createLookalikeNegativeParam("права только на чтение исходного объекта АппМетрики",
                        getLookalikeSegment(OWNER.get(AUDIENCE_APPMETRICA_SEGMENT_ID)), NO_ACCESS_TO_CREATE_LOOKALIKE)
        );
    }

    @Test
    public void checkTryCreateLookalike() {
        user.onSegmentsSteps().createLookalikeAndExpectError(error, segmentRequest);
    }

    @AfterClass
    public static void cleanUp() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(processingSegmentId);
    }
}
