package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdSkadConversionValueConfigGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdSkadConversionValueConfigPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.SkadnetworkV1EventsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.parameters.skad.SKAdCVParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.controller.SKAdCVControllerInnerSKAdCVConfigWrapper;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConfig;
import ru.yandex.metrika.mobmet.model.cv.events.SKAdCVEvent;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

public class SKAdConversionValueSteps extends AppMetricaBaseSteps {

    public SKAdConversionValueSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить информацию о SKAd ConversionValue для приложения {0}")
    @ParallelExecution(ALLOW)
    public SKAdCVConfig getConfig(Long appId) {
        return getConfig(SUCCESS_MESSAGE, expectSuccess(), appId).getConfig();
    }

    @Step("Обновить SKAd ConversionValue для приложения {0}")
    @ParallelExecution(ALLOW)
    public SKAdCVConfig updateConfig(Long appId, SKAdCVConfig config, IFormParameters... parameters) {
        return updateConfig(SUCCESS_MESSAGE, expectSuccess(), appId, config, parameters).getConfig();
    }

    @Step("Обновить информацию о SKAd ConversionValue для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void updateConfigAndExpectError(Long appId, SKAdCVConfig config, IExpectedError error, IFormParameters... parameters) {
        updateConfig(SUCCESS_MESSAGE, expectError(error), appId, config, parameters);
    }

    @Step("Получить список событий SKAd ConversionValue")
    @ParallelExecution(RESTRICT)
    public List<SKAdCVEvent> getEvents(SKAdCVParameters parameters) {
        return getEvents(SUCCESS_MESSAGE, expectSuccess(), parameters).getEvents();
    }

    private ManagementV1ApplicationAppIdSkadConversionValueConfigGETSchema getConfig(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdSkadConversionValueConfigGETSchema result = get(
                ManagementV1ApplicationAppIdSkadConversionValueConfigGETSchema.class,
                format("/management/v1/application/%s/skad/conversion_value/config", appId));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdSkadConversionValueConfigPUTSchema updateConfig(
            String message, Matcher matcher, Long appId, SKAdCVConfig config, IFormParameters... parameters) {
        ManagementV1ApplicationAppIdSkadConversionValueConfigPUTSchema result = put(
                ManagementV1ApplicationAppIdSkadConversionValueConfigPUTSchema.class,
                format("/management/v1/application/%s/skad/conversion_value/config", appId),
                new SKAdCVControllerInnerSKAdCVConfigWrapper().withConfig(config),
                parameters);
        assertThat(message, result, matcher);
        return result;
    }

    private SkadnetworkV1EventsGETSchema getEvents(String message, Matcher matcher, IFormParameters... parameters) {
        SkadnetworkV1EventsGETSchema result = get(
                SkadnetworkV1EventsGETSchema.class,
                "/skadnetwork/v1/events",
                parameters);
        assertThat(message, result, matcher);
        return result;
    }
}
