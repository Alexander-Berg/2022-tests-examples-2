package ru.yandex.autotests.morda.monitorings;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.jayway.restassured.response.Response;
import org.junit.Before;
import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.Test;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiRequest;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.SearchApiVersion;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.ValidateSchemaSteps;
import ru.yandex.qatools.monitoring.MonitoringNotifierRule;
import ru.yandex.qatools.monitoring.graphite.GraphiteMetricPrefix;

import java.util.List;
import java.util.Random;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.qatools.monitoring.MonitoringNotifierRule.notifierRule;

/**
 * User: asamar
 * Date: 05.10.16
 */
@GraphiteMetricPrefix("servers.portal.eoff.monitorings")
public abstract class BaseSearchApiSchemaMonitoring {
    protected static final MordaMonitoringsProperties CONFIG = new MordaMonitoringsProperties();
    protected static final List<MordaLanguage> LANGUAGES = asList(RU, UK, BE, KK);
    protected static final Random RANDOM = new Random();

    protected MordaClient mordaClient = new MordaClient();
    protected SearchApiRequestData requestData;
    protected Response response;

    @Rule
    @ClassRule
    public static MonitoringNotifierRule notifierRule = notifierRule();

    @Rule
    public AllureLoggingRule loggingRule = new AllureLoggingRule();

    public BaseSearchApiSchemaMonitoring(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    protected static MordaLanguage getRandomLanguage() {
        return LANGUAGES.get(RANDOM.nextInt(LANGUAGES.size()));
    }

    protected abstract SearchApiVersion getVersion();

    protected SearchApiRequest getSearchApiRequest() {
        requestData.setVersion(getVersion());
        return mordaClient.search().request(CONFIG.getEnvironment(), requestData);
    }

    protected String getJsonSchemaFile() {
        return String.format("/api/search/%s/%s/%s-response.json", getVersion(),
                requestData.getBlock().getValue(), requestData.getBlock().getValue());
    }

    @Before
    public void init() throws JsonProcessingException {
        response = getSearchApiRequest().readAsResponse();
    }

    @Test
    public void schema() {
        ValidateSchemaSteps.validate(response, getJsonSchemaFile());
    }
}
