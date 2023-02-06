package ru.yandex.metrika.api.management.client.segments;

import javax.annotation.Nonnull;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.segments.streamabillity.FieldsStreamabilityContextBuilder;
import ru.yandex.metrika.api.management.client.segments.streamabillity.FunctionsStreamabilityContextBuilder;
import ru.yandex.metrika.api.management.client.segments.streamabillity.QueryStreamabilityContextBuilder;
import ru.yandex.metrika.api.management.client.segments.streamabillity.StreamabilityClass;
import ru.yandex.metrika.auth.EmptyRolesProvider;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.parser.AbstractTest;

import static java.util.function.Predicate.not;
import static ru.yandex.metrika.segments.core.parser.ClickHouseMeta.NotStreamableField;

public class SegmentParseServiceStreamabilityClassificationTest extends AbstractTest {

    private  SegmentParseService segmentParseService;

    public static SegmentParseService buildSegmentParseService(ApiUtils apiUtils) {
        return new SegmentParseService(
                new EmptyRolesProvider(), apiUtils,
                new QueryStreamabilityContextBuilder(
                        new FunctionsStreamabilityContextBuilder(),
                        new FieldsStreamabilityContextBuilder(not(NotStreamableField::equals))
                )
        );
    }

    @Override
    @Before
    public void setUp() throws Exception {
        super.setUp();
        segmentParseService = buildSegmentParseService(apiUtils);
    }

    @Test
    public void simpleVisitsSegment() {
        var segment = getSegment("ym:s:trafficSourceID == 1");
        Assert.assertEquals(
                StreamabilityClass.builder()
                        .streamable()
                        .requiresSimpleFunctions()
                        .requiresVisits()
                        .build(),
                segmentParseService.calculateStreamabilityClass(segment)
        );
    }

    @Test
    public void dictsVisitsSegment() {
        var segment = getSegment("ym:s:regionCountry == 1");
        Assert.assertEquals(
                StreamabilityClass.builder()
                        .streamable()
                        .requiresSimpleFunctions()
                        .requiresDictFunctions()
                        .requiresVisits()
                        .build(),
                segmentParseService.calculateStreamabilityClass(segment)
        );
    }

    @Test
    public void complexVisitsSegment() {
        var segment = getSegment("ym:s:trafficSourceID == 1 AND ym:s:startURL =* 'ya.ru*'");
        Assert.assertEquals(
                StreamabilityClass.builder()
                        .streamable()
                        .requiresSimpleFunctions()
                        .requiresHardFunctions()
                        .requiresVisits()
                        .build(),
                segmentParseService.calculateStreamabilityClass(segment)
        );
    }

    /**
     * Сделать тест с только простыми функциями для хитов не получается, потому что мы сейчас по дефолту строим сегмент
     * через визиты, и подзапрос включает в себя arrayExists (а это сложная функция). Поэтому по факту сейчас все сегменты
     * с хитами будут со сложными функциями. В будущем сделаем выбор правильной таблицы автоматическим и эта проблема пропадёт
     */
    @Test
    public void complexHitsSegment() {
        var segment = getSegment("EXISTS (ym:pv:pageView == 1 AND ym:pv:URL =* 'ya.ru*')");
        Assert.assertEquals(
                StreamabilityClass.builder()
                        .streamable()
                        // здесь на самом деле можно обойтись и без декомпозиции, но так как мы пока отключили
                        // оптимизацию, которая считала что некоторые подзапросы можно свести к простым фильтрам,
                        // то все фильтры по хитам будут сейчас (по мнению классификатора) требовать декомпозиции.
                        .requiresDecomposition()
                        .requiresSimpleFunctions()
                        .requiresHardFunctions()
                        .requiresHits()
                        .build(),
                segmentParseService.calculateStreamabilityClass(segment)
        );
    }

    @Test
    public void visitsAndHitsSegment() {
        var segment = getSegment("ym:s:trafficSourceID == 1 AND ym:pv:pageView == 1");
        Assert.assertEquals(
                StreamabilityClass.builder()
                        .streamable()
                        .requiresDecomposition()
                        .requiresSimpleFunctions()
                        .requiresHardFunctions()
                        .requiresVisits()
                        .requiresHits()
                        .build(),
                segmentParseService.calculateStreamabilityClass(segment)
        );
    }

    @Test
    public void notStreamableAttribute() {
        var segment = getSegment("ym:s:notStreamableAttribute == 'what ever'");
        Assert.assertEquals(
                StreamabilityClass.NOT_STREAMABLE,
                segmentParseService.calculateStreamabilityClass(segment)
        );
    }

    @Nonnull
    private Segment getSegment(String expression) {
        return new Segment(1, 1, "", expression, 1, 1, false, SegmentStatus.active, SegmentSource.API, null, null);
    }
}
