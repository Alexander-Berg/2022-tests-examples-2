package ru.yandex.autotests.advapi.steps.management;

import ru.yandex.advapi.*;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.adv.api.management.placement.external.PlacementIn;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;

public class PlacementsSteps extends BaseAdvApiSteps {

    public PlacementsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить размещение рекламодателя {0}, кампании {1}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsGETSchema getPlacementsAndExpectSuccess(long advertiserId, long campaignId, IFormParameters... parameters) {
        return getAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsGETSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/placements", advertiserId, campaignId),
                parameters
        );
    }

    @Step("Получить размещение рекламодателя {0}, кампании {1} и ожидать ошибку {2}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsGETSchema getPlacementsAndExpectError(long advertiserId, long campaignId, IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsGETSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/placements", advertiserId, campaignId),
                error,
                parameters
        );
    }

    @Step("Получить размещение {2} рекламодателя {0} кампании {1}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdGETSchema getPlacementAndExpectSuccess(long advertiserId, long campaignId, long placementId, IFormParameters... parameters) {
        return getAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdGETSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/placement/%d", advertiserId, campaignId, placementId),
                parameters
        );
    }

    @Step("Получить размещение {2} рекламодателя {0} кампании {1} и ожидать ошибку {3}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdGETSchema getPlacementAndExpectError(long advertiserId, long campaignId, long placementId, IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdGETSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/placement/%d", advertiserId, campaignId, placementId),
                error,
                parameters
        );
    }

    @Step("Создать новое размещение для рекламодателя {0} кампании {1}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsPOSTSchema addPlacementsAndExpectSuccess(long advertiserId, long campaignId, PlacementIn body, IFormParameters... parameters) {
        return postAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsPOSTSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/placements", advertiserId, campaignId),
                new V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsPOSTRequestSchema().withPlacement(body),
                parameters
        );
    }

    @Step("Создать новое размещение для рекламодателя {0} кампании {1} и ожидать ошибку {3}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsPOSTSchema addPlacementsAndExpectError(long advertiserId, long campaignId, PlacementIn settings, IExpectedError error, IFormParameters... parameters) {
        V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsPOSTRequestSchema body = new V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsPOSTRequestSchema().withPlacement(settings);
        return postAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementsPOSTSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/placements", advertiserId, campaignId),
                body,
                error,
                parameters
        );
    }

    @Step("Изменить размещение {2} рекламодателя {0} кампании {1}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdPUTSchema updatePlacementAndExpectSuccess(long advertiserId, long campaignId, long placementId, PlacementIn update, IFormParameters... parameters) {
        V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdPUTRequestSchema body = new V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdPUTRequestSchema().withPlacement(update);
        return putAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdPUTSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/placement/%d", advertiserId, campaignId, placementId),
                body,
                parameters
        );
    }

    @Step("Изменить размещение {2} рекламодателя {0} кампании {1} и ожидать ошибку {4}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdPUTSchema updatePlacementAndExpectError(long advertiserId, long campaignId, long placementId, PlacementIn update, IExpectedError error, IFormParameters... parameters) {
        V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdPUTRequestSchema body = new V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdPUTRequestSchema().withPlacement(update);
        return putAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdPUTSchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/placement/%d", advertiserId, campaignId, placementId),
                body,
                error,
                parameters
        );
    }

    @Step("Удалить размещение {2} рекламодателя {0} кампании {1}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdDELETESchema deletePlacementAndExpectSuccess(long advertiserId, long campaignId, long placementId, IFormParameters... parameters) {
        return deleteAndExpectSuccess(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdDELETESchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/placement/%d", advertiserId, campaignId, placementId),
                parameters
        );
    }

    @Step("Удалить размещение {2} рекламодателя {0} кампании {1} и ожидать ошибку {3}")
    public V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdDELETESchema deletePlacementAndExpectError(long advertiserId, long campaignId, long placementId, IExpectedError error, IFormParameters... parameters) {
        return deleteAndExpectError(
                V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPlacementPlacementIdDELETESchema.class,
                format("/v1/management/advertiser/%d/campaign/%d/placement/%d", advertiserId, campaignId, placementId),
                error,
                parameters
        );
    }
}
