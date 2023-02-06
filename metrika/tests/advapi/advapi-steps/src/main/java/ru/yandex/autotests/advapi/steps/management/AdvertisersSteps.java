package ru.yandex.autotests.advapi.steps.management;

import ru.yandex.advapi.*;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.adv.api.management.advertiser.external.AdvertiserSettings;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;

public class AdvertisersSteps extends BaseAdvApiSteps {

    public AdvertisersSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список рекламодателей")
    public V1ManagementAdvertisersListGETSchema getAdvertisersListAndExpectSuccess(IFormParameters... parameters) {
        return getAndExpectSuccess(V1ManagementAdvertisersListGETSchema.class, "/v1/management/advertisers_list", parameters);
    }

    @Step("Получить список рекламодателей и ожидать ошибку {0}")
    public V1ManagementAdvertisersListGETSchema getAdvertisersListAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(V1ManagementAdvertisersListGETSchema.class, "/v1/management/advertisers_list", error, parameters);
    }

    @Step("Получить рекламодателей")
    public V1ManagementAdvertisersGETSchema getAdvertisersAndExpectSuccess(IFormParameters... parameters) {
        return getAndExpectSuccess(V1ManagementAdvertisersGETSchema.class, "/v1/management/advertisers", parameters);
    }

    @Step("Получить рекламодателей и ожидать ошибку {0}")
    public V1ManagementAdvertisersGETSchema getAdvertisersAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(V1ManagementAdvertisersGETSchema.class, "/v1/management/advertisers", error, parameters);
    }

    @Step("Получить рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdGETSchema getAdvertiserAndExpectSuccess(long advertiserId, IFormParameters... parameters) {
        return getAndExpectSuccess(V1ManagementAdvertiserAdvertiserIdGETSchema.class, format("/v1/management/advertiser/%d", advertiserId), parameters);
    }

    @Step("Получить рекламодателя {0} и ожидать ошибку {1}")
    public V1ManagementAdvertiserAdvertiserIdGETSchema getAdvertiserAndExpectError(long advertiserId, IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(V1ManagementAdvertiserAdvertiserIdGETSchema.class, format("/v1/management/advertiser/%d", advertiserId), error, parameters);
    }

    @Step("Получить информацию о рекламодателе {0}")
    public V1ManagementAdvertiserAdvertiserIdInfoGETSchema getAdvertiserInfoAndExpectSuccess(long advertiserId, IFormParameters... parameters) {
        return getAndExpectSuccess(V1ManagementAdvertiserAdvertiserIdInfoGETSchema.class, format("/v1/management/advertiser/%d/info", advertiserId), parameters);
    }

    @Step("Получить информацию о рекламодателе {0} и ожидать ошибку {1}")
    public V1ManagementAdvertiserAdvertiserIdInfoGETSchema getAdvertiserInfoAndExpectError(long advertiserId, IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(V1ManagementAdvertiserAdvertiserIdInfoGETSchema.class, format("/v1/management/advertiser/%d/info", advertiserId), error, parameters);
    }

    @Step("Добавить рекламодателя")
    public V1ManagementAdvertisersPOSTSchema addAdvertisersAndExpectSuccess(V1ManagementAdvertisersPOSTRequestSchema body, IFormParameters... parameters) {
        return postAndExpectSuccess(
                V1ManagementAdvertisersPOSTSchema.class,
                "/v1/management/advertisers",
                body,
                parameters
        );
    }

    public V1ManagementAdvertiserAdvertiserIdGrantMultiplierGETSchema getAdvertiserGrantMultiplierAndExpectSuccess(long advertiserId, IFormParameters... parameters) {
        return getAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdGrantMultiplierGETSchema.class,
                format("/v1/management/advertiser/%d/grant_multiplier", advertiserId),
                parameters
        );
    }

    public V1ManagementAdvertiserAdvertiserIdGrantMultiplierGETSchema getAdvertiserGrantMultiplierAndExpectError(long advertiserId, IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(
                V1ManagementAdvertiserAdvertiserIdGrantMultiplierGETSchema.class,
                format("/v1/management/advertiser/%d/grant_multiplier", advertiserId),
                error,
                parameters
        );
    }

    public InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierPOSTSchema setAdvertiserGrantMultiplierAndExpectSuccess(
            long advertiserId,
            InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierPOSTSchema body,
            IFormParameters... parameters
    ) {
        return postAndExpectSuccess(
                InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierPOSTSchema.class,
                format("/internal/v1/management/advertiser/%d/grant_multiplier", advertiserId),
                body,
                parameters
        );
    }

    public InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierPOSTSchema setAdvertiserGrantMultiplierAndExpectError(
            long advertiserId,
            InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierPOSTSchema body,
            IExpectedError error
    ) {
        return postAndExpectError(
                InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierPOSTSchema.class,
                format("/internal/v1/management/advertiser/%d/grant_multiplier", advertiserId),
                body,
                error
        );
    }

    public InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierDELETESchema deleteAdvertiserGrantMultiplierAndExpectSuccess(
            long advertiserId,
            IFormParameters... parameters
    ) {
        return deleteAndExpectSuccess(
                InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierDELETESchema.class,
                format("/internal/v1/management/advertiser/%d/grant_multiplier", advertiserId),
                parameters
        );
    }

    public InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierDELETESchema deleteAdvertiserGrantMultiplierAndExpectError(
            long advertiserId,
            IExpectedError error
    ) {
        return deleteAndExpectError(
                InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierDELETESchema.class,
                format("/internal/v1/management/advertiser/%d/grant_multiplier", advertiserId),
                error
        );
    }

    @Step("Добавить рекламодателя и ожидать ошибку {1}")
    public V1ManagementAdvertisersPOSTSchema addAdvertisersAndExpectError(V1ManagementAdvertisersPOSTRequestSchema body, IExpectedError error) {
        return postAndExpectError(
                V1ManagementAdvertisersPOSTSchema.class,
                "/v1/management/advertisers",
                body,
                error
        );
    }

    @Step("Изменить рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdPUTSchema updateAdvertiser(long advertiserId, AdvertiserSettings body, IFormParameters... parameters) {
        return put(
                V1ManagementAdvertiserAdvertiserIdPUTSchema.class,
                format("/v1/management/advertiser/%d", advertiserId),
                new V1ManagementAdvertiserAdvertiserIdPUTRequestSchema().withAdvertiser(body),
                parameters
        );
    }

    @Step("Изменить рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdPUTSchema updateAdvertiserAndExpectSuccess(long advertiserId, V1ManagementAdvertiserAdvertiserIdPUTRequestSchema body, IFormParameters... parameters) {
        return putAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdPUTSchema.class,
                format("/v1/management/advertiser/%d", advertiserId),
                body,
                parameters
        );
    }

    @Step("Изменить рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdPUTSchema updateAdvertiserAndExpectSuccess(long advertiserId, AdvertiserSettings body, IFormParameters... parameters) {
        return putAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdPUTSchema.class,
                format("/v1/management/advertiser/%d", advertiserId),
                new V1ManagementAdvertiserAdvertiserIdPUTRequestSchema().withAdvertiser(body),
                parameters
        );
    }

    @Step("Изменить рекламодателя {0} и ожидать ошибку {2}")
    public V1ManagementAdvertiserAdvertiserIdPUTSchema updateAdvertiserAndExpectError(long advertiserId, AdvertiserSettings body, IExpectedError error, IFormParameters... parameters) {
        return putAndExpectError(
                V1ManagementAdvertiserAdvertiserIdPUTSchema.class,
                format("/v1/management/advertiser/%d", advertiserId),
                new V1ManagementAdvertiserAdvertiserIdPUTRequestSchema().withAdvertiser(body),
                error,
                parameters
        );
    }

    @Step("Удалить рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdDELETESchema deleteAdvertiserAndExpectSuccess(long advertiserId, IFormParameters... parameters) {
        return deleteAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdDELETESchema.class,
                format("/v1/management/advertiser/%d", advertiserId),
                parameters
        );
    }

    @Step("Удалить рекламодателя {0} и ожидать ошибку {1}")
    public V1ManagementAdvertiserAdvertiserIdDELETESchema deleteAdvertiserAndExpectError(long advertiserId, IExpectedError error) {
        return deleteAndExpectError(
                V1ManagementAdvertiserAdvertiserIdDELETESchema.class,
                format("/v1/management/advertiser/%d", advertiserId),
                error
        );
    }
}
