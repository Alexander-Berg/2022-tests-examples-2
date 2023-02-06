package ru.yandex.autotests.morda.tests;

import com.fasterxml.jackson.databind.JsonNode;
import org.apache.log4j.Logger;
import org.junit.Rule;
import org.junit.Test;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.main.DesktopFamilyMainMorda;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.TouchMainMorda;
import ru.yandex.autotests.morda.restassured.requests.Request;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.ValidateSchemaSteps;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.tests.MordaTestTags.SCHEMA;

/**
 * User: asamar
 * Date: 14.02.17
 */
public abstract class AbstractCleanvarsSchemaTest {
    protected static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    protected final Logger LOGGER = Logger.getLogger(this.getClass());

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    protected Request request;
    protected String jsonSchemaFile;
    protected String block;
    protected MordaClient mordaClient;

    public AbstractCleanvarsSchemaTest(Morda<?> morda, String jsonSchemaFile, String block) {
        this.mordaClient = new MordaClient();
        this.request = mordaClient.cleanvars(morda, block);
        this.jsonSchemaFile = jsonSchemaFile;
        this.block = block;

    }

    @Test
    @Stories(SCHEMA)
    public void schema() throws Exception {
        JsonNode response = request
                .readAsResponse()
                .as(JsonNode.class)
                .get(block);

        ValidateSchemaSteps.validate(response, jsonSchemaFile);
    }

    protected static Collection<Object[]> getMordas(String desktopSchemaFile, String touchSchemaFile) {
        List<Object[]> reqs = new ArrayList<>();
        List<Morda<?>> desktopMordas = new ArrayList<>();

        desktopMordas.addAll(DesktopMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        desktopMordas.addAll(DesktopFamilyMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));

        desktopMordas.forEach(morda ->
                reqs.add(new Object[]{
                        morda,
                        desktopSchemaFile
                })
        );

        TouchMainMorda.getDefaultList(CONFIG.pages().getEnvironment()).forEach(morda ->
                reqs.add(new Object[]{
                        morda,
                        touchSchemaFile
                })
        );

        return reqs;
    }
}
