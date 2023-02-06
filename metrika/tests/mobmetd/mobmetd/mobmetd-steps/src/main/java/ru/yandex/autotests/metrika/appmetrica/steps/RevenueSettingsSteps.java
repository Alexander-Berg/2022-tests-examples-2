package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdRevenueSettingsPostbackGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdRevenueSettingsPostbackPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdRevenueSettingsReportGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdRevenueSettingsReportPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.segments.apps.misc.revenue.RevenueSettings;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class RevenueSettingsSteps extends AppMetricaBaseSteps {

    public RevenueSettingsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить настройки отчётов по Revenue для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueSettings getRevenueReportSettings(Long appId) {
        return getRevenueReportSettings(SUCCESS_MESSAGE, expectSuccess(), appId).getSettings();
    }

    @Step("Поменять настройки отчётов по Revenue для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueSettings storeRevenueReportSettings(Long appId, RevenueSettings revenueSettings) {
        return storeRevenueReportSettings(SUCCESS_MESSAGE, expectSuccess(), appId, revenueSettings).getSettings();
    }

    @Step("Поменять настройки отчётов по Revenue для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public RevenueSettings storeRevenueReportSettingsAndExpectError(Long appId, RevenueSettings revenueSettings,
                                                                    IExpectedError error) {
        return storeRevenueReportSettings(ERROR_MESSAGE, expectError(error), appId, revenueSettings).getSettings();
    }

    @Step("Получить настройки постбеков по Revenue для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueSettings getRevenuePostbackSettings(Long appId) {
        return getRevenuePostbackSettings(SUCCESS_MESSAGE, expectSuccess(), appId).getSettings();
    }

    @Step("Поменять настройки постбеков по Revenue для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueSettings storeRevenuePostbackSettings(Long appId, RevenueSettings revenueSettings) {
        return storeRevenuePostbackSettings(SUCCESS_MESSAGE, expectSuccess(), appId, revenueSettings).getSettings();
    }

    private ManagementV1ApplicationAppIdRevenueSettingsReportGETSchema getRevenueReportSettings(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdRevenueSettingsReportGETSchema result = get(
                ManagementV1ApplicationAppIdRevenueSettingsReportGETSchema.class,
                format("/management/v1/application/%s/revenue/settings/report", appId));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdRevenueSettingsReportPOSTSchema storeRevenueReportSettings(
            String message, Matcher matcher, Long appId, RevenueSettings revenueSettings) {
        ManagementV1ApplicationAppIdRevenueSettingsReportPOSTSchema result = post(
                ManagementV1ApplicationAppIdRevenueSettingsReportPOSTSchema.class,
                format("/management/v1/application/%s/revenue/settings/report", appId),
                revenueSettings);
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdRevenueSettingsPostbackGETSchema getRevenuePostbackSettings(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdRevenueSettingsPostbackGETSchema result = get(
                ManagementV1ApplicationAppIdRevenueSettingsPostbackGETSchema.class,
                format("/management/v1/application/%s/revenue/settings/postback", appId));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdRevenueSettingsPostbackPOSTSchema storeRevenuePostbackSettings(
            String message, Matcher matcher, Long appId, RevenueSettings revenueSettings) {
        ManagementV1ApplicationAppIdRevenueSettingsPostbackPOSTSchema result = post(
                ManagementV1ApplicationAppIdRevenueSettingsPostbackPOSTSchema.class,
                format("/management/v1/application/%s/revenue/settings/postback", appId),
                revenueSettings);
        assertThat(message, result, matcher);
        return result;
    }
}
