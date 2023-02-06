package ru.yandex.autotests.advapi.steps.management;

import ru.yandex.advapi.*;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;

public class CampaignsSteps extends BaseAdvApiSteps {

    public CampaignsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить кампании")
    public V1ManagementCampaignsGETSchema getCampaignsAndExpectSuccess(IFormParameters... parameters) {
        return getAndExpectSuccess(V1ManagementCampaignsGETSchema.class, "/v1/management/campaigns", parameters);
    }

    @Step("Получить кампании и ожидать ошибку {0}")
    public V1ManagementCampaignsGETSchema getCampaignsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(V1ManagementCampaignsGETSchema.class, "/v1/management/campaigns", error, parameters);
    }

    @Step("Получить кампании рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdCampaignsGETSchema getCampaignsByAdvertiserAndExpectSuccess(long advertiserId, IFormParameters... parameters) {
        return getAndExpectSuccess(V1ManagementAdvertiserAdvertiserIdCampaignsGETSchema.class, format("/v1/management/advertiser/%d/campaigns", advertiserId), parameters);
    }

    @Step("Получить кампании рекламодателя {0} и ожидать ошибку {1}")
    public V1ManagementAdvertiserAdvertiserIdCampaignsGETSchema getCampaignsByAdvertiserAndExpectError(long advertiserId, IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(V1ManagementAdvertiserAdvertiserIdCampaignsGETSchema.class, format("/v1/management/advertiser/%d/campaigns", advertiserId), error, parameters);
    }

    @Step("Получить кампанию {1} рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdGETSchema getCampaignAndExpectSuccess(long advertiserId, long campaignId, IFormParameters... parameters) {
        return getAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdGETSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d", advertiserId, campaignId),
                parameters
        );
    }

    @Step("Получить кампанию {1} рекламодателя {0} и ожидать ошибку {2}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdGETSchema getCampaignAndExpectError(long advertiserId, long campaignId, IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdGETSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d", advertiserId, campaignId),
                error,
                parameters
        );
    }

    @Step("Получить инфомацию о кампании {1} рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdInfoGETSchema getCampaignInfoAndExpectSuccess(long advertiserId, long campaignId, IFormParameters... parameters) {
        return getAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdInfoGETSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/info", advertiserId, campaignId),
                parameters
        );
    }

    @Step("Получить инфомацию о кампании {1} рекламодателя {0} и ожидать ошибку {2}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdInfoGETSchema getCampaignInfoAndExpectError(long advertiserId, long campaignId, IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdInfoGETSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/info", advertiserId, campaignId),
                error,
                parameters
        );
    }

    @Step("Добавить кампанию рекламодателю {0}")
    public V1ManagementAdvertiserAdvertiserIdCampaignsPOSTSchema addCampaignAndExpectSuccess(long advertiserId, V1ManagementAdvertiserAdvertiserIdCampaignsPOSTRequestSchema body, IFormParameters... parameters) {
        return postAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignsPOSTSchema.class,
                format("/v1/management/advertiser/%d/campaigns", advertiserId),
                body,
                parameters
        );
    }

    @Step("Добавить кампанию рекламодателю {0} и ожидать ошибку {2}")
    public V1ManagementAdvertiserAdvertiserIdCampaignsPOSTSchema addCampaignAndExpectError(long advertiserId, V1ManagementAdvertiserAdvertiserIdCampaignsPOSTRequestSchema body, IExpectedError error, IFormParameters... parameters) {
        return postAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignsPOSTSchema.class,
                format("/v1/management/advertiser/%d/campaigns", advertiserId),
                body,
                error,
                parameters
        );
    }

    @Step("Клонировать кампанию {1} рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdClonePOSTSchema cloneCampaignAndExpectSuccess(long advertiserId, long campaignId, IFormParameters... parameters) {
        return postAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdClonePOSTSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/clone", advertiserId, campaignId),
                null,
                parameters
        );
    }

    @Step("Клонировать кампанию {1} рекламодателя {0} и ожидать ошибку {2}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdClonePOSTSchema cloneCampaignAndExpectError(long advertiserId, long campaignId, IExpectedError error, IFormParameters... parameters) {
        return postAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdClonePOSTSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/clone", advertiserId, campaignId),
                null,
                error,
                parameters
        );
    }

    @Step("Изменить кампанию {1} рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTSchema updateCampaignAndExpectSuccess(long advertiserId, long campaignId, V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTRequestSchema body, IFormParameters... parameters) {
        return putAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d", advertiserId, campaignId),
                body,
                parameters
        );
    }

    @Step("Изменить кампанию {1} рекламодателя {0} и ожидать ошибку {3}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTSchema updateCampaignAndExpectError(long advertiserId, long campaignId, V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTRequestSchema body, IExpectedError error, IFormParameters... parameters) {
        return putAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d", advertiserId, campaignId),
                body,
                error,
                parameters
        );
    }

    @Step("Удалить кампанию {1} рекламодателя {0}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdDELETESchema deleteCampaignAndExpectSuccess(long advertiserId, long campaignId, IFormParameters... parameters) {
        return deleteAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdDELETESchema.class,
                format("/v1/management/advertiser/%d/campaign/%d", advertiserId, campaignId),
                parameters
        );
    }

    @Step("Удалить кампанию {1} рекламодателя {0} и ожидать ошибку {2}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdDELETESchema deleteCampaignAndExpectError(long advertiserId, long campaignId, IExpectedError error, IFormParameters... parameters) {
        return deleteAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdDELETESchema.class,
                format("/v1/management/advertiser/%d/campaign/%d", advertiserId, campaignId),
                error,
                parameters
        );
    }
}
