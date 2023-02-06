package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.model.Funnel;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

public class FunnelsSteps extends AppMetricaBaseSteps {

    public FunnelsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить воронку {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public Funnel getFunnel(Long appId, Long funnelId) {
        return getFunnel(SUCCESS_MESSAGE, expectSuccess(), appId, funnelId).getFunnel();
    }

    @Step("Получить воронку {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public Funnel getFunnelAndExpectError(Long appId, Long funnelId, IExpectedError error) {
        return getFunnel(ERROR_MESSAGE, expectError(error), appId, funnelId).getFunnel();
    }

    @Step("Получить список воронок для приложения {0}")
    @ParallelExecution(ALLOW)
    public List<Funnel> getFunnelsList(Long appId) {
        return getFunnelsList(SUCCESS_MESSAGE, expectSuccess(), appId).getFunnels();
    }

    @Step("Добавить воронку для приложения {0}")
    @ParallelExecution(ALLOW)
    public Funnel addFunnel(Long appId, Funnel funnel) {
        return addFunnel(SUCCESS_MESSAGE, expectSuccess(), appId, funnel).getFunnel();
    }

    @Step("Обновить воронку {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public Funnel updateFunnel(Long appId, Long funnelId, Funnel funnel) {
        return updateFunnel(SUCCESS_MESSAGE, expectSuccess(), appId, funnelId, funnel).getFunnel();
    }

    @Step("Обновить воронку {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public Funnel updateFunnelAndExpectError(Long appId, Long funnelId, Funnel funnel, IExpectedError error) {
        return updateFunnel(ERROR_MESSAGE, expectError(error), appId, funnelId, funnel).getFunnel();
    }

    @Step("Удалить воронку {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void deleteFunnel(Long appId, Long funnelId) {
        deleteFunnel(SUCCESS_MESSAGE, expectSuccess(), appId, funnelId);
    }

    @Step("Удалить воронку {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void deleteFunnelAndExpectError(Long appId, Long funnelId, IExpectedError error) {
        deleteFunnel(ERROR_MESSAGE, expectError(error), appId, funnelId);
    }

    @Step("Удалить воронку {1} для приложения {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteFunnelAndIgnoreResult(Long appId, Long funnelId) {
        if (appId != null && funnelId != null) {
            deleteFunnel(ANYTHING_MESSAGE, expectAnything(), appId, funnelId);
        }
    }

    private ManagementV1ApplicationAppIdFunnelIdGETSchema getFunnel(String message, Matcher matcher,
                                                                    Long appId, Long funnelId) {
        final ManagementV1ApplicationAppIdFunnelIdGETSchema result = get(
                ManagementV1ApplicationAppIdFunnelIdGETSchema.class,
                String.format("/management/v1/application/%s/funnel/%s", appId, funnelId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationAppIdFunnelsGETSchema getFunnelsList(String message, Matcher matcher, Long appId) {
        final ManagementV1ApplicationAppIdFunnelsGETSchema result = get(
                ManagementV1ApplicationAppIdFunnelsGETSchema.class,
                String.format("/management/v1/application/%s/funnels", appId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationAppIdFunnelPOSTSchema addFunnel(String message, Matcher matcher,
                                                                   Long appId, Funnel funnel) {
        final ManagementV1ApplicationAppIdFunnelPOSTSchema result = post(
                ManagementV1ApplicationAppIdFunnelPOSTSchema.class,
                String.format("/management/v1/application/%s/funnel", appId),
                new ManagementV1ApplicationAppIdFunnelPOSTRequestSchema().withFunnel(funnel));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationAppIdFunnelIdPUTSchema updateFunnel(String message, Matcher matcher,
                                                                       Long appId, Long funnelId, Funnel funnel) {
        final ManagementV1ApplicationAppIdFunnelIdPUTSchema result = put(
                ManagementV1ApplicationAppIdFunnelIdPUTSchema.class,
                String.format("/management/v1/application/%s/funnel/%s", appId, funnelId),
                new ManagementV1ApplicationAppIdFunnelIdPUTRequestSchema().withFunnel(funnel));

        assertThat(message, result, matcher);

        return result;
    }

    private void deleteFunnel(String message, Matcher matcher, Long appId, Long funnelId) {
        final ManagementV1ApplicationAppIdFunnelIdDELETESchema result = delete(
                ManagementV1ApplicationAppIdFunnelIdDELETESchema.class,
                String.format("/management/v1/application/%s/funnel/%s", appId, funnelId));

        assertThat(message, result, matcher);
    }
}
