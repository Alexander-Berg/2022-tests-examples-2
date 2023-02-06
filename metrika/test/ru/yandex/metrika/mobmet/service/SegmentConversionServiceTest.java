package ru.yandex.metrika.mobmet.service;

import java.util.Map;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.report.ReportType;
import ru.yandex.metrika.mobmet.report.SegmentGeneratorMocks;
import ru.yandex.metrika.mobmet.report.SegmentGeneratorsFactory;
import ru.yandex.metrika.mobmet.report.generator.SegmentGenerator;
import ru.yandex.metrika.mobmet.report.model.frontend.MobmetFrontendParamsParser;
import ru.yandex.metrika.segments.apps.schema.MobmetTableSchema;
import ru.yandex.metrika.util.ApiInputValidator;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.mock;

public class SegmentConversionServiceTest {

    private static final String TEST_PARAMS = "{\"filters\":[" +
            "{\"id\":\"commonGeo\",\"data\":{\"inverted\":false,\"paths\":[{\"path\":[\"187\"]}]}}" +
            "]}";

    private SegmentConversionService service;

    @Before
    public void before() {
        final MobmetFrontendParamsParser parsedSegment = new MobmetFrontendParamsParser();
        final Map<ReportType, SegmentGenerator> generators =
                new SegmentGeneratorsFactory(SegmentGeneratorMocks.emptyPushMetaService()).build();
        service = new SegmentConversionService(parsedSegment, generators, mock(ApiInputValidator.class));
    }

    @Test
    public void convertForReport() {
        String actual = service.convertForReport(ReportType.AUDIENCE, TEST_PARAMS);
        assertEquals("(regionCountry=='187')", actual);
    }

    @Test
    public void convertForFilterValueSimple() {
        String actual = service.convertForFilterValue(
                MobmetTableSchema.USERS, MobmetTableSchema.USERS, TEST_PARAMS);
        assertEquals("(regionCountry=='187')", actual);
    }

    @Test
    public void convertForFilterValueExists() {
        String actual = service.convertForFilterValue(
                MobmetTableSchema.USERS, MobmetTableSchema.PUSH_EVENTS, TEST_PARAMS);
        assertEquals("exists ym:u:device with ((regionCountry=='187'))", actual);
    }

    @Test
    public void convertIgnoredFilters() {
        String actual = service.convertForFilterValue(
                MobmetTableSchema.PROFILES, MobmetTableSchema.INSTALLATIONS, TEST_PARAMS);
        assertEquals("", actual);
    }
}
