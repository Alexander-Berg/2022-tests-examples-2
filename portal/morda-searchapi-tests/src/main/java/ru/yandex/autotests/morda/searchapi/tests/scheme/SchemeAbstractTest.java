package ru.yandex.autotests.morda.searchapi.tests.scheme;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.github.fge.jsonschema.core.report.ListProcessingReport;
import com.github.fge.jsonschema.main.JsonSchema;
import org.junit.After;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.RuleChain;
import ru.yandex.autotests.morda.rules.allure.AllureStoryRule;
import ru.yandex.autotests.morda.utils.client.requests.RequestBuilder;
import ru.yandex.qatools.allure.annotations.Features;

import static org.junit.Assert.assertTrue;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.ValidateSchemeUtils.OBJECT_MAPPER;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.ValidateSchemeUtils.attach;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/06/15
 */
@Features("JSON-schema validation")
public class SchemeAbstractTest {

    @Rule
    public RuleChain rule;

    protected JsonNode response;
    protected ListProcessingReport report;
    private ValidationCase validationCase;


    public SchemeAbstractTest(ValidationCase validationCase) {
        this.validationCase = validationCase;
        this.rule = RuleChain.outerRule(new AllureStoryRule(validationCase.description));
    }


    @Test
    public void validate() throws Exception {
        response = validationCase.builder
                .build()
                .readAsJsonNode();
        report = ValidateSchemeUtils.validate(response, validationCase.jsonSchema);
        assertTrue("Invalid response", report.isSuccess());
    }

    @After
    public void attachFiles() throws JsonProcessingException {
        attach("response.json", OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(response));
        if (!report.isSuccess()) {
//            System.out.println(OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(report.asJson()));
            attach("error.json", OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(report.asJson()));
        }
    }

    public static class ValidationCase {
        protected String description;
        protected RequestBuilder builder;
        protected JsonSchema jsonSchema;

        private ValidationCase(String description,
                               RequestBuilder requestBuilder,
                               JsonSchema jsonSchema) {
            this.description = description;
            this.builder = requestBuilder;
            this.jsonSchema = jsonSchema;
        }

        public static ValidationCase validationCase(String description,
                                                    RequestBuilder requestBuilder,
                                                    JsonSchema jsonSchema){
            return new ValidationCase(description, requestBuilder, jsonSchema);
        }

        @Override
        public String toString() {
            return description;
        }
    }
}
