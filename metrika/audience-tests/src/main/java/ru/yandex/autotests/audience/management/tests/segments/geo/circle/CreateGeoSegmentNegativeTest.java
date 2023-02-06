package ru.yandex.autotests.audience.management.tests.segments.geo.circle;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Lists;
import org.apache.commons.lang3.StringUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.SegmentRequestGeoCircle;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;

import static ru.yandex.audience.geo.GeoSegmentType.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

/**
 * Created by ava1on on 28.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.GEO
})
@Title("Геосегменты: создание сегмента с типом «геолокация» (негативные тесты)")
@RunWith(Parameterized.class)
public class CreateGeoSegmentNegativeTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    @Parameter
    public String description;

    @Parameter(1)
    public SegmentRequestGeoCircle segmentRequest;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                createGeoNegativeParam("отсутствует параметр name", getGeoCircleSegment(LAST).withName(null),
                        NOT_NULL),
                createGeoNegativeParam("пустое имя сегмента", getGeoCircleSegment(REGULAR)
                        .withName(StringUtils.EMPTY), INCORRECT_SEGMENT_NAME_LENGTH),
                createGeoNegativeParam("слишком длинное имя сегмента", getGeoCircleSegment(CONDITION)
                        .withName(TOO_LONG_SEGMENT_NAME_LENGTH), INCORRECT_SEGMENT_NAME_LENGTH),
                createGeoNegativeParam("отсутствует параметр radius", getGeoCircleSegment(REGULAR).withRadius(null),
                        RADIUS_IS_ABSENT),
                createGeoNegativeParam("радиус меньше минимального", getGeoCircleSegment(CONDITION)
                        .withRadius(GEO_MIN_RADIUS - 1), TOO_SMALL_RADIUS),
                createGeoNegativeParam("радиус больше максимального", getGeoCircleSegment(LAST)
                        .withRadius(GEO_MAX_RADIUS + 1), TOO_BIG_RADIUS),
                createGeoNegativeParam("отсутствует параметр period_length", getGeoCircleSegment(CONDITION)
                        .withPeriodLength(null), PERIOD_LENGTH_IS_ABSENT),
                createGeoNegativeParam("невалидный период", getGeoCircleSegment(CONDITION).withPeriodLength(0L),
                        INCORRECT_PERIOD_LENGTH),
                createGeoNegativeParam("период больше максимального", getGeoCircleSegment(CONDITION)
                        .withPeriodLength(GEO_MAX_PERIOD_LENGTH + 1), TOO_BIG_PERIOD_LENGTH),
                createGeoNegativeParam("отсутствует параметр times_quantity", getGeoCircleSegment(CONDITION)
                        .withTimesQuantity(null), TIME_QUANTITY_IS_ABSENT),
                createGeoNegativeParam("quantity больше period_length", getGeoCircleSegment(CONDITION)
                        .withTimesQuantity(8L).withPeriodLength(7L), QUANTITY_GREATER_PERIOD),
                createGeoNegativeParam("отсутствует параметр points", getGeoCircleSegment(LAST).withPoints(null),
                        POINTS_ARE_ABSENT),
                createGeoNegativeParam("пустой массив точек", getGeoCircleSegment(REGULAR)
                        .withPoints(new ArrayList<>()), POINTS_ARE_ABSENT),
                createGeoNegativeParam("широта меньше минимальной", getGeoCircleSegment(CONDITION)
                        .withPoints(getGeoPointsLat(-GEO_LATITUDE_LIMIT - 0.000001d)), INCORRECT_POINT),
                createGeoNegativeParam("широта больше максимальной", getGeoCircleSegment(LAST)
                        .withPoints(getGeoPointsLat(GEO_LATITUDE_LIMIT +0.000001d)), INCORRECT_POINT),
                createGeoNegativeParam("долгота меньше минимальной", getGeoCircleSegment(REGULAR)
                        .withPoints(getGeoPointsLon(-180.000001d)), INCORRECT_POINT),
                createGeoNegativeParam("долгота больше максимальной", getGeoCircleSegment(CONDITION)
                        .withPoints(getGeoPointsLon(180.000001d)), INCORRECT_POINT),
                createGeoNegativeParam("отсутствует параметр geo_segment_type", getGeoCircleSegment(null),
                        GEO_TYPE_IS_ABSENT),
                createGeoNegativeParam("101 точка в condition сегменте", getGeoCircleSegment(CONDITION)
                        .withPoints(getGeoPoints(GEO_CONDITION_MAX_POINTS + 1)), TOO_MUCH_POINTS_CONDITION),
                createGeoNegativeParam("1001 точка в сегменте", getGeoCircleSegment(REGULAR)
                        .withPoints(getGeoPoints(GEO_OTHER_MAX_POINTS + 1)), TOO_MUCH_POINTS),
                createGeoNegativeParam("В точке отсутствует широта", getGeoCircleSegment(HOME)
                        .withPoints(Lists.newArrayList(getGeoPointLon(0.0).withLatitude(null))), INCORRECT_LATITUDE),
                createGeoNegativeParam("В точке отсутсвтует долгота", getGeoCircleSegment(HOME)
                        .withPoints(Lists.newArrayList(getGeoPointLat(0.0).withLongitude(null))), INCORRECT_LONGITUDE)
        );
    }

    @Test
    public void checkTryCreateGeo() {
        user.onSegmentsSteps().createGeoAndExpectError(error,segmentRequest);
    }
}
