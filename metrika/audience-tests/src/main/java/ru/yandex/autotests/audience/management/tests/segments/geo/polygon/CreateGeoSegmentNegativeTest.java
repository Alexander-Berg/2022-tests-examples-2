package ru.yandex.autotests.audience.management.tests.segments.geo.polygon;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.geo.GeoPoint;
import ru.yandex.audience.geo.GeoPolygon;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.SegmentRequestGeoPolygon;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;

import static ru.yandex.audience.geo.GeoSegmentType.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.audience.errors.ManagementError.*;
import static ru.yandex.autotests.audience.management.tests.TestData.*;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.SEGMENTS,
        Requirements.Story.Management.Segment.GEO
})
@Title("Геосегменты: создание сегмента с типом «геолокация - полигоны» (негативные тесты)")
@RunWith(Parameterized.class)
public class CreateGeoSegmentNegativeTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER_2);

    @Parameter
    public String description;

    @Parameter(1)
    public SegmentRequestGeoPolygon segmentRequest;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                createGeoNegativeParam("отсутствует параметр name", getGeoPolygonSegment(LAST).withName(null),
                        NOT_NULL),
                createGeoNegativeParam("пустое имя сегмента", getGeoPolygonSegment(REGULAR)
                        .withName(StringUtils.EMPTY), INCORRECT_SEGMENT_NAME_LENGTH),
                createGeoNegativeParam("слишком длинное имя сегмента", getGeoPolygonSegment(CONDITION)
                        .withName(TOO_LONG_SEGMENT_NAME_LENGTH), INCORRECT_SEGMENT_NAME_LENGTH),
                createGeoNegativeParam("пустой список полигонов",
                        getGeoPolygonSegment(REGULAR).withPolygons(Collections.emptyList()), INCORRECT_NUMBER_OF_POLYGONS),
                createGeoNegativeParam("отсутствует поле polygons",
                        getGeoPolygonSegment(REGULAR).withPolygons(null), POLYGONS_ARE_ABSENT),
                createGeoNegativeParam("геополигон по актуальным координатам",
                        getGeoPolygonSegment(LAST).withPolygons(Collections.singletonList(new GeoPolygon()
                                .withPoints(Arrays.asList(
                                        new GeoPoint().withLatitude(-17.8375).withLongitude(179.4397),
                                        new GeoPoint().withLatitude(-17.8385).withLongitude(179.4397),
                                        new GeoPoint().withLatitude(-17.8385).withLongitude(179.4387),
                                        new GeoPoint().withLatitude(-17.8375).withLongitude(179.4397)
                                )))),
                        POLYGON_WITH_LAST_COORDINATES),
                createGeoNegativeParam("отсутствует поле points у полигона",
                        getGeoPolygonSegment(REGULAR).withPolygons(Collections.singletonList(new GeoPolygon().withPoints(null))), POLYGON_POINTS_ARE_ABSENT),
                createGeoNegativeParam("пустой массив точек у полигона",
                        getGeoPolygonSegment(REGULAR)
                                .withPolygons(Collections.singletonList(new GeoPolygon()
                                        .withPoints(Collections.emptyList()))),
                        POLYGON_POINTS_EMPTY),
                createGeoNegativeParam("широта меньше минимальной",
                        getGeoPolygonSegment(REGULAR).withPolygons(Collections.singletonList(new GeoPolygon()
                                .withPoints(Arrays.asList(
                                        new GeoPoint().withLatitude(-GEO_LATITUDE_LIMIT).withLongitude(0d),
                                        new GeoPoint().withLatitude(-GEO_LATITUDE_LIMIT).withLongitude(0.001),
                                        new GeoPoint().withLatitude(-GEO_LATITUDE_LIMIT - 0.000001d).withLongitude(0.001),
                                        new GeoPoint().withLatitude(-GEO_LATITUDE_LIMIT).withLongitude(0d)
                                )))),
                        INCORRECT_POINT),
                createGeoNegativeParam("широта больше максимальной",
                        getGeoPolygonSegment(REGULAR).withPolygons(Collections.singletonList(new GeoPolygon()
                                .withPoints(Arrays.asList(
                                        new GeoPoint().withLatitude(GEO_LATITUDE_LIMIT).withLongitude(0d),
                                        new GeoPoint().withLatitude(GEO_LATITUDE_LIMIT).withLongitude(0.001),
                                        new GeoPoint().withLatitude(GEO_LATITUDE_LIMIT + 0.000001d).withLongitude(0.001),
                                        new GeoPoint().withLatitude(GEO_LATITUDE_LIMIT).withLongitude(0d)
                                )))),
                        INCORRECT_POINT),
                createGeoNegativeParam("долгота меньше минимальной",
                        getGeoPolygonSegment(REGULAR).withPolygons(Collections.singletonList(new GeoPolygon()
                                .withPoints(Arrays.asList(
                                        new GeoPoint().withLatitude(0d).withLongitude(-180d),
                                        new GeoPoint().withLatitude(0d).withLongitude(-180.000001d),
                                        new GeoPoint().withLatitude(0.001).withLongitude(-180.000001d),
                                        new GeoPoint().withLatitude(0d).withLongitude(-180d)
                                )))),
                        INCORRECT_POINT),
                createGeoNegativeParam("долгота больше максимальной",
                        getGeoPolygonSegment(REGULAR).withPolygons(Collections.singletonList(new GeoPolygon()
                                .withPoints(Arrays.asList(
                                        new GeoPoint().withLatitude(0d).withLongitude(180d),
                                        new GeoPoint().withLatitude(0d).withLongitude(180.000001d),
                                        new GeoPoint().withLatitude(0.001).withLongitude(180.000001d),
                                        new GeoPoint().withLatitude(0d).withLongitude(180d)
                                )))),
                        INCORRECT_POINT),
                createGeoNegativeParam("11 полигонов в сегменте", getGeoPolygonSegment(REGULAR)
                        .withPolygons(getGeoPolygons(GEO_MAX_POLYGONS + 1)), INCORRECT_NUMBER_OF_POLYGONS),
                createGeoNegativeParam("полигон с самопересечениями", getGeoPolygonSegment(REGULAR)
                        .withPolygons(Collections.singletonList(getInvalidGeoPolygon())), POLYGON_WITH_INTERSECTIONS),
                createGeoNegativeParam("отсутствует параметр period_length", getGeoPolygonSegment(CONDITION)
                        .withPeriodLength(null), PERIOD_LENGTH_IS_ABSENT),
                createGeoNegativeParam("невалидный период", getGeoPolygonSegment(CONDITION).withPeriodLength(0L),
                        INCORRECT_PERIOD_LENGTH),
                createGeoNegativeParam("период больше максимального", getGeoPolygonSegment(CONDITION)
                        .withPeriodLength(GEO_MAX_PERIOD_LENGTH + 1), TOO_BIG_PERIOD_LENGTH),
                createGeoNegativeParam("отсутствует параметр times_quantity", getGeoPolygonSegment(CONDITION)
                        .withTimesQuantity(null), TIME_QUANTITY_IS_ABSENT),
                createGeoNegativeParam("quantity больше period_length", getGeoPolygonSegment(CONDITION)
                        .withTimesQuantity(8L).withPeriodLength(7L), QUANTITY_GREATER_PERIOD),
                createGeoNegativeParam("отсутствует параметр geo_segment_type", getGeoPolygonSegment(null),
                        GEO_TYPE_IS_ABSENT)
        );
    }

    @Test
    public void checkTryCreateGeo() {
        user.onSegmentsSteps().createGeoAndExpectError(error,segmentRequest);
    }
}
