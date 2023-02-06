package ru.yandex.autotests.morda.tests;

import com.jayway.restassured.response.Response;
import org.apache.log4j.Logger;
import org.junit.Rule;
import org.junit.Test;
import ru.yandex.autotests.morda.restassured.requests.Request;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.ValidateSchemaSteps;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.morda.tests.MordaTestTags.SCHEMA;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/08/16
 */
public abstract class AbstractSchemaTest {
    protected static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    protected final Logger LOGGER = Logger.getLogger(this.getClass());

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    protected Request request;
    protected String jsonSchemaFile;

    public AbstractSchemaTest(Request request, String jsonSchemaFile) {
        this.request = request;
        this.jsonSchemaFile = jsonSchemaFile;
    }

    @Test
    @Stories(SCHEMA)
    public void schema() throws Exception {
        Response response = request
                .readAsResponse();

        ValidateSchemaSteps.validate(response, jsonSchemaFile);
    }
}
