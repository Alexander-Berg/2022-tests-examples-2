package ru.yandex.autotests.morda.steps;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.github.fge.jsonschema.core.exceptions.ProcessingException;
import com.github.fge.jsonschema.core.report.ListProcessingReport;
import com.github.fge.jsonschema.core.report.ListReportProvider;
import com.github.fge.jsonschema.core.report.LogLevel;
import com.github.fge.jsonschema.core.report.ReportProvider;
import com.github.fge.jsonschema.main.JsonSchema;
import com.github.fge.jsonschema.main.JsonSchemaFactory;
import com.jayway.restassured.response.Response;
import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.steps.attach.AttachmentUtils;
import ru.yandex.qatools.allure.annotations.Step;

import static org.junit.Assert.fail;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/06/15
 */
public class ValidateSchemaSteps {
    private static final Logger LOGGER = Logger.getLogger(ValidateSchemaSteps.class);
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private static final ReportProvider REPORT_PROVIDER;
    private static final JsonSchemaFactory JSON_SCHEMA_FACTORY;

    static {
        REPORT_PROVIDER = new ListReportProvider(LogLevel.ERROR, LogLevel.FATAL);
        JSON_SCHEMA_FACTORY = JsonSchemaFactory.newBuilder().setReportProvider(REPORT_PROVIDER).freeze();
        OBJECT_MAPPER.enable(SerializationFeature.INDENT_OUTPUT);
    }

    private static JsonSchema getJsonSchema(String jsonFile) {
        try {
            LOGGER.info("Getting json-schema from file " + jsonFile);
            return JSON_SCHEMA_FACTORY.getJsonSchema(ValidateSchemaSteps.class.getResource(jsonFile).toString());
        } catch (ProcessingException e) {
            throw new RuntimeException("Failed to get json-schema", e);
        }
    }

    public static void validate(JsonNode response, String jsonSchemaFile) throws Exception {
        JsonSchema jsonSchema = getJsonSchema(jsonSchemaFile);
        validate(response, jsonSchema);
    }

    public static void validate(Response response, String jsonSchemaFile) {
        JsonNode jsonResponse = response.as(JsonNode.class);
        JsonSchema jsonSchema = getJsonSchema(jsonSchemaFile);
        validate(jsonResponse, jsonSchema);
    }

    @Step("Should see valid response")
    public static void validate(JsonNode response, JsonSchema jsonSchema) {
        try {
            ListProcessingReport report = (ListProcessingReport) jsonSchema.validate(response, true);
            if (!report.isSuccess()) {
                AttachmentUtils.attachJson("validation-error", prepareReportNode(report.asJson()));
                fail("Invalid response.");
            }
        } catch (ProcessingException e) {
            throw new RuntimeException(e);
        }

    }

    private static JsonNode prepareReportNode(JsonNode jsonNode) {
        if (jsonNode instanceof ArrayNode) {
            ArrayNode arrayNode = (ArrayNode) jsonNode;
            arrayNode.forEach(ValidateSchemaSteps::prepareReportNode);
        } else if (jsonNode instanceof ObjectNode) {
            ObjectNode objectNode = (ObjectNode) jsonNode;

            if (objectNode.has("level")) {

                ObjectNode tmpNode = objectNode.deepCopy();

                objectNode.removeAll();

                tmpNode.remove("level");
                tmpNode.remove("schema");
                tmpNode.remove("domain");

                ObjectNode instanceNode = (ObjectNode) tmpNode.get("instance");

                if (instanceNode != null) {
                    objectNode.put("pointer", instanceNode.get("pointer").textValue());
                    tmpNode.remove("instance");
                }

                if (tmpNode.has("message")) {
                    objectNode.put("message", tmpNode.get("message").textValue());
                    tmpNode.remove("message");
                }

                if (tmpNode.has("expected")) {
                    objectNode.putPOJO("expected", tmpNode.get("expected"));
                    tmpNode.remove("expected");
                }

                if (tmpNode.has("found")) {
                    objectNode.putPOJO("found", tmpNode.get("found"));
                    tmpNode.remove("found");
                }

                objectNode.setAll(tmpNode);
            }

            objectNode.forEach(ValidateSchemaSteps::prepareReportNode);
        }

        return jsonNode;
    }
}

