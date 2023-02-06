package ru.yandex.autotests.morda.searchapi.tests.scheme;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.github.fge.jsonschema.core.exceptions.ProcessingException;
import com.github.fge.jsonschema.core.report.ListProcessingReport;
import com.github.fge.jsonschema.core.report.ListReportProvider;
import com.github.fge.jsonschema.core.report.LogLevel;
import com.github.fge.jsonschema.core.report.ReportProvider;
import com.github.fge.jsonschema.main.JsonSchema;
import com.github.fge.jsonschema.main.JsonSchemaFactory;
import ru.yandex.autotests.morda.region.Region;
import ru.yandex.autotests.morda.searchapi.tests.MordaSearchApiTestsProperties;
import ru.yandex.qatools.allure.annotations.Attachment;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.region.Region.DUBNA;
import static ru.yandex.autotests.morda.region.Region.KAZAN;
import static ru.yandex.autotests.morda.region.Region.KHARKIV;
import static ru.yandex.autotests.morda.region.Region.KYIV;
import static ru.yandex.autotests.morda.region.Region.MINSK;
import static ru.yandex.autotests.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.morda.region.Region.NIZHNY_NOVGOROD;
import static ru.yandex.autotests.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.morda.region.Region.OMSK;
import static ru.yandex.autotests.morda.region.Region.SAINT_PETERSBURG;
import static ru.yandex.autotests.morda.region.Region.SAMARA;
import static ru.yandex.autotests.morda.region.Region.VLADIVOSTOK;
import static ru.yandex.autotests.morda.region.Region.VORONEZH;
import static ru.yandex.autotests.morda.region.Region.YEKATERINBURG;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/06/15
 */
public class ValidateSchemeUtils {
    private static final MordaSearchApiTestsProperties CONFIG = new MordaSearchApiTestsProperties();
    public static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    public static final Map<String, JsonSchema> TEST_SCHEMAS = new HashMap<>();
    public static final Map<String, JsonSchema> COUNT_SCHEMAS = new HashMap<>();
    public static final List<String> TEST_BLOCKS = asList("afisha", "application", "informer", "now", "poi", "stocks",
            "topnews", "transport", "tv", "football");
    public static final List<String> COUNT_BLOCKS = asList("afisha", "topnews", "tv");
    private static final ReportProvider REPORT_PROVIDER;
    private static final JsonSchemaFactory JSON_SCHEMA_FACTORY;

    public static final List<String> langs = asList("ru", "uk", "kk", "be", "tt");
    public static final List<Region> regions = asList(MOSCOW, SAINT_PETERSBURG, NOVOSIBIRSK, VLADIVOSTOK, YEKATERINBURG,
            DUBNA, VORONEZH, OMSK, KAZAN, NIZHNY_NOVGOROD, SAMARA, KYIV, KHARKIV, MINSK);

    static {
        REPORT_PROVIDER = new ListReportProvider(LogLevel.ERROR, LogLevel.FATAL);
        JSON_SCHEMA_FACTORY = JsonSchemaFactory.newBuilder().setReportProvider(REPORT_PROVIDER).freeze();
        OBJECT_MAPPER.enable(SerializationFeature.INDENT_OUTPUT);

        for (String block : TEST_BLOCKS) {
            TEST_SCHEMAS.put(block, getJsonSchema(getTestSchemeURI(block).toString()));
        }
        for (String block : COUNT_BLOCKS) {
            COUNT_SCHEMAS.put(block, getJsonSchema(getMonitoringSchemeURI(block).toString()));
        }
    }

    private static JsonSchema getJsonSchema(String uri) {
        try {
            return JSON_SCHEMA_FACTORY.getJsonSchema(uri);
        } catch (ProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    private static URI getTestSchemeURI(String block) {
        String schemaUrl = String.format("/jsonschema/blocks/%s/response-%s-test.json", block, block);
        try {
            return ValidateSchemeUtils.class.getResource(schemaUrl).toURI();
        } catch (URISyntaxException e) {
            throw new RuntimeException(e);
        }
    }

    private static URI getMonitoringSchemeURI(String block) {
        String schemaUrl = String.format("/jsonschema/blocks/%s/response-%s-count.json", block, block);
        try {
            return ValidateSchemeUtils.class.getResource(schemaUrl).toURI();
        } catch (URISyntaxException e) {
            throw new RuntimeException(e);
        }
    }

    public static ListProcessingReport validate(JsonNode response, JsonSchema schema) throws Exception {
        return (ListProcessingReport) schema.validate(response, true);
    }

    @Attachment(value = "{0}", type = "application/json")
    public static String attach(String name, String content) {
        return content;
    }

 /*   public static final MordaSearchApiParameterBuilder TESTS_SCHEME_DATA = searchApiParameters()
            .withLangs(asList("ru", "uk", "kk", "be", "tt"))
            .withRegions(asList(Region.values()))
            .withSchemaMap(TEST_SCHEMAS);

    public static final MordaSearchApiParameterBuilder TESTS_SCHEME_COUNT_DATA = searchApiParameters()
            .withLangs(asList("ru", "uk", "kk", "be", "tt"))
            .withRegions(asList(MOSCOW, SAINT_PETERSBURG, NOVOSIBIRSK, VLADIVOSTOK, YEKATERINBURG,
                    DUBNA, VORONEZH, OMSK, KAZAN, NIZHNY_NOVGOROD, SAMARA, KYIV, KHARKIV, MINSK))
            .withSchemaMap(COUNT_SCHEMAS);

    public static final MordaSearchApiParameterBuilder MONITORINGS_SCHEME_DATA = searchApiParameters()
            .withLangs(asList("ru", "uk", "kk", "be", "tt"))
            .withRegions(asList(MOSCOW, SAINT_PETERSBURG, NOVOSIBIRSK, VLADIVOSTOK, YEKATERINBURG,
                    DUBNA, VORONEZH, OMSK, KAZAN, NIZHNY_NOVGOROD, SAMARA, KYIV, KHARKIV, MINSK))
            .withSchemaMap(TEST_SCHEMAS);

    public static final MordaSearchApiParameterBuilder MONITORINGS_SCHEME_COUNT_DATA = searchApiParameters()
            .withLangs(asList("ru", "uk", "kk", "be", "tt"))
            .withRegions(asList(MOSCOW, SAINT_PETERSBURG, NOVOSIBIRSK, VLADIVOSTOK, YEKATERINBURG,
                    DUBNA, VORONEZH, OMSK, KAZAN, NIZHNY_NOVGOROD, SAMARA, KYIV, KHARKIV, MINSK))
            .withSchemaMap(COUNT_SCHEMAS);*/

}
