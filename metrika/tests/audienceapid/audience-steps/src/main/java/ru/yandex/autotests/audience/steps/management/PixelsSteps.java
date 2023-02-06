package ru.yandex.autotests.audience.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.audience.pixel.Pixel;
import ru.yandex.autotests.audience.beans.schemes.*;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.PixelControllerInnerPixelRequest;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by konkov on 28.03.2017.
 */
public class PixelsSteps extends HttpClientLiteFacade {
    public PixelsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список пикселей")
    public List<Pixel> getPixels(IFormParameters... parameters) {
        return getPixels(SUCCESS_MESSAGE, expectSuccess(), parameters).getPixels();
    }

    @Step("Получить список пикселей и ожидать ошибку {0}")
    public List<Pixel> getPixelsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getPixels(ERROR_MESSAGE, expectError(error), parameters).getPixels();
    }

    private V1ManagementPixelsGETSchema getPixels(String message, Matcher matcher, IFormParameters... parameters) {
        V1ManagementPixelsGETSchema result = get(V1ManagementPixelsGETSchema.class,
                "/v1/management/pixels", parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать пиксель \"{0}\"")
    public Pixel createPixel(String name, IFormParameters... parameters) {
        return createPixel(SUCCESS_MESSAGE, expectSuccess(), name, parameters).getPixel();
    }

    @Step("Создать пиксель \"{1}\" и ожидать ошибку {0}")
    public Pixel createPixelAndAndExpectError(IExpectedError error, String name, IFormParameters... parameters) {
        return createPixel(ERROR_MESSAGE, expectError(error), name, parameters).getPixel();
    }

    private V1ManagementPixelsPOSTSchema createPixel(String message, Matcher matcher,
                                                     String name,
                                                     IFormParameters... parameters) {
        V1ManagementPixelsPOSTSchema result = post(V1ManagementPixelsPOSTSchema.class,
                "/v1/management/pixels", new V1ManagementPixelsPOSTRequestSchema()
                        .withPixel(new PixelControllerInnerPixelRequest().withName(name)),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Редактировать пиксель {0} на \"{1}\"")
    public Pixel editPixel(Long pixelId, String name, IFormParameters... parameters) {
        return editPixel(SUCCESS_MESSAGE, expectSuccess(), pixelId, name, parameters).getPixel();
    }

    @Step("Редактировать пиксель {1} на \"{2}\" и ожидать ошибку {0}")
    public Pixel editPixelAndExpectError(IExpectedError error,
                                         Long pixelId, String name, IFormParameters... parameters) {
        return editPixel(ERROR_MESSAGE, expectError(error), pixelId, name, parameters).getPixel();
    }

    private V1ManagementPixelPixelIdPUTSchema editPixel(String message, Matcher matcher,
                                                        Long pixelId,
                                                        String name,
                                                        IFormParameters... parameters) {
        V1ManagementPixelPixelIdPUTSchema result = put(V1ManagementPixelPixelIdPUTSchema.class,
                format("/v1/management/pixel/%s", pixelId),
                new V1ManagementPixelPixelIdPUTRequestSchema()
                        .withPixel(new PixelControllerInnerPixelRequest().withName(name)),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить пиксель {0}")
    public Boolean deletePixel(Long pixelId, IFormParameters... parameters) {
        return deletePixel(SUCCESS_MESSAGE, expectSuccess(), pixelId, parameters).getSuccess();
    }

    @Step("Удалить пиксель {1} и ожидать ошибку {0}")
    public Boolean deletePixelAndExpectError(IExpectedError error, Long pixelId, IFormParameters... parameters) {
        return deletePixel(ERROR_MESSAGE, expectError(error), pixelId, parameters).getSuccess();
    }

    @Step("Удалить пиксель {0} и игнорировать статус")
    public Boolean deletePixelAndIgnoreStatus(Long pixelId, IFormParameters... parameters) {
        if (pixelId != null) {
            return deletePixel(ANYTHING_MESSAGE, expectAnything(), pixelId, parameters).getSuccess();
        } else {
            return true;
        }
    }

    private V1ManagementPixelPixelIdDELETESchema deletePixel(String message, Matcher matcher,
                                                             Long pixelId, IFormParameters... parameters) {
        V1ManagementPixelPixelIdDELETESchema result = delete(V1ManagementPixelPixelIdDELETESchema.class,
                format("/v1/management/pixel/%s", pixelId), parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Восстановить пиксель {0}")
    public Boolean restorePixel(Long pixelId, IFormParameters... parameters) {
        return restorePixel(SUCCESS_MESSAGE, expectSuccess(), pixelId, parameters).getSuccess();
    }

    @Step("Восстановить пиксель {1} и ожидать ошибку {0}")
    public Boolean restorePixelAndExpectError(IExpectedError error, Long pixelId, IFormParameters... parameters) {
        return restorePixel(ERROR_MESSAGE, expectError(error), pixelId, parameters).getSuccess();
    }

    private V1ManagementPixelPixelIdUndeletePOSTSchema restorePixel(String message, Matcher matcher,
                                                                    Long pixelId, IFormParameters... parameters) {
        V1ManagementPixelPixelIdUndeletePOSTSchema result = post(V1ManagementPixelPixelIdUndeletePOSTSchema.class,
                format("/v1/management/pixel/%s/undelete", pixelId), null, parameters);

        assertThat(message, result, matcher);

        return result;
    }
}
