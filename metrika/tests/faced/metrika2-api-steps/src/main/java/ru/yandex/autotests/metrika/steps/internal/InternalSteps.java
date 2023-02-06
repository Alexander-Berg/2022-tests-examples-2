package ru.yandex.autotests.metrika.steps.internal;

import com.google.gson.reflect.TypeToken;
import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.beans.schemes.InternalGetAccuracyGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalGetAccuracyGlobalGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalTimezonesGETSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.parameters.management.v1.RoleParams;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.RolesResponse;
import ru.yandex.metrika.api.management.client.TimezonesServiceInnerTimeZone;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;
import java.util.Map;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.utils.Utils.aggregate;

/**
 * Created by sourx on 04.02.2016.
 */
public class InternalSteps extends MetrikaBaseSteps {

    @Step("Получить список часовых поясов")
    public List<TimezonesServiceInnerTimeZone> getTimeZonesListAndExpectSuccess(IFormParameters... parameters) {
        return getTimeZonesList(SUCCESS_MESSAGE, expectSuccess(), parameters).getTimeZones();
    }

    private InternalTimezonesGETSchema getTimeZonesList(String message, Matcher matcher, IFormParameters... parameters) {
        InternalTimezonesGETSchema result = executeAsJson(
                getRequestBuilder("/internal/timezones").get(parameters))
                .readResponse(InternalTimezonesGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить JSON-схемы для сравнения")
    public Map<String, Object> getSchemas() {
        return executeAsJson(getRequestBuilder("/internal/schema").get())
                .readResponse((Class<Map<String, Object>>)
                        new TypeToken<Map<String, Object>>() {}.getRawType());
    }

    public NotificationsSteps onNotificationSteps() {
        return createStepsWithCommonSettings(NotificationsSteps.class);
    }

    public ClientSettingsSteps onClientSettingsSteps() {
        return createStepsWithCommonSettings(ClientSettingsSteps.class);
    }

    @Step("Получить значение точности")
    public Double getAccuracyAndExpectSuccess(IFormParameters... parameters){
        return getAccuracyValue(SUCCESS_MESSAGE, expectSuccess(), parameters).getAccuracy();
    }

    @Step("Получить значение точности для глобального счётчика")
    public Double getAccuracyGlobalAndExpectSuccess(IFormParameters... parameters){
        return getAccuracyGlobalValue(SUCCESS_MESSAGE, expectSuccess(), parameters).getAccuracy();
    }

    @Step("Запросить значение точности и ожидать ошибку {0}")
    public void getAccuracyAndExpectError(IExpectedError error, IFormParameters... parameters) {
        getAccuracyValue(ERROR_MESSAGE, expectError(error), parameters);
    }

    @Step("Запросить значение точности для глоабльного счётчика и ожидать ошибку {0}")
    public void getAccuracyGlobalAndExpectError(IExpectedError error, IFormParameters... parameters) {
        getAccuracyGlobalValue(ERROR_MESSAGE, expectError(error), parameters);
    }

    @Step("Получить роли для пользователя {0}")
    public RolesResponse getRoles(
            Long uid, IFormParameters... parameters) {

        return executeAsJson(
                getRequestBuilder("/internal/rbac/roles")
                        .get(aggregate(
                                new RoleParams().withUid(uid),
                                parameters)))
                .readResponse(RolesResponse.class);
    }

    private InternalGetAccuracyGETSchema getAccuracyValue(String message, Matcher matcher, IFormParameters... parameters){
        InternalGetAccuracyGETSchema result = executeAsJson(
                getRequestBuilder("/internal/get_accuracy").get(parameters))
                .readResponse(InternalGetAccuracyGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    private InternalGetAccuracyGlobalGETSchema getAccuracyGlobalValue(String message, Matcher matcher, IFormParameters... parameters){
        InternalGetAccuracyGlobalGETSchema result = executeAsJson(
                getRequestBuilder("/internal/get_accuracy/global").get(parameters))
                .readResponse(InternalGetAccuracyGlobalGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

}
