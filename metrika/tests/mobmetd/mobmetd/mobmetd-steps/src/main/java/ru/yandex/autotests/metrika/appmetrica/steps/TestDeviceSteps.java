package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.List;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyTestdevicesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdTestdevicesDeviceIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdTestdevicesPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdTestdevicesPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.appmetrica.wrappers.TestDeviceWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.model.TestDevice;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.aggregate;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by graev on 18/01/2017.
 */
public class TestDeviceSteps extends AppMetricaBaseSteps {
    public TestDeviceSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список устройств для приложения {0}")
    @ParallelExecution(ALLOW)
    public List<TestDevice> getDevicesList(long appId, IFormParameters... parameters) {
        return getTestDevices(SUCCESS_MESSAGE, expectSuccess(), appId, parameters).getDevices();
    }

    @Step("Создать тестовое устройство {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public TestDevice createTestDevice(long appId, TestDeviceWrapper device) {
        return createOrUpdate(SUCCESS_MESSAGE, expectSuccess(), appId, device.get()).getDevice();
    }

    @Step("Создать тестовое устройство {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public TestDevice createTestDeviceAndExpectError(long appId, TestDeviceWrapper device, IExpectedError error) {
        return createOrUpdate(SUCCESS_MESSAGE, expectError(error), appId, device.get()).getDevice();
    }

    @Step("Изменить тестовое устройство для приложения {0} на {1}")
    @ParallelExecution(ALLOW)
    public TestDevice updateTestDevice(long appId, TestDeviceWrapper device) {
        return createOrUpdate(SUCCESS_MESSAGE, expectSuccess(), appId, device.get()).getDevice();
    }

    @Step("Удалить тестовое устройство {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void deleteTestDevice(long appId, TestDeviceWrapper device) {
        deleteTestDevice(SUCCESS_MESSAGE, expectSuccess(), appId, device.get().getId());
    }

    @Step("Удалить тестовое устройство {1} для приложения {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteTestDeviceAndIgnoreResult(Long appId, TestDeviceWrapper device) {
        if (appId != null && device != null && device.get() != null && device.get().getId() != null) {
            deleteTestDevice(ANYTHING_MESSAGE, expectAnything(), appId, device.get().getId());
        }
    }

    private ManagementV1ApplicationApiKeyTestdevicesGETSchema getTestDevices(String message, Matcher matcher, long appId,
                                                                            IFormParameters... parameters) {
        ManagementV1ApplicationApiKeyTestdevicesGETSchema result = get(
                ManagementV1ApplicationApiKeyTestdevicesGETSchema.class,
                format("/management/v1/application/%s/testdevices", appId),
                aggregate(parameters));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationAppIdTestdevicesPOSTSchema createOrUpdate(String message, Matcher matcher,
                                                                                   long appId, TestDevice device) {
        ManagementV1ApplicationAppIdTestdevicesPOSTSchema result = post(
                ManagementV1ApplicationAppIdTestdevicesPOSTSchema.class,
                String.format("/management/v1/application/%s/testdevices", appId),
                new ManagementV1ApplicationAppIdTestdevicesPOSTRequestSchema().withDevice(device));

        assertThat(message, result, matcher);

        return result;
    }

    private void deleteTestDevice(String message, Matcher matcher, Long appId, Long deviceId) {
        ManagementV1ApplicationAppIdTestdevicesDeviceIdDELETESchema result = delete(
                ManagementV1ApplicationAppIdTestdevicesDeviceIdDELETESchema.class,
                String.format("/management/v1/application/%s/testdevices/%s", appId, deviceId));

        assertThat(message, result, matcher);
    }

}
