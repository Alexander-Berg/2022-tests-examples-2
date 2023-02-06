package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.List;
import java.util.stream.Collectors;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalPartnerAccountsPartnerIdBindPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalPartnerAccountsPartnerIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalPartnerAccountsPartnerIdGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyTrackingDeepLinkIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyTrackingDeepLinksGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyTrackingDeepLinksPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyTrackingDeepLinksPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyTrackingTargetUrlIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyTrackingTargetUrlsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyTrackingTargetUrlsPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyTrackingTargetUrlsPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingCampaignNewIdGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingCampaignsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingCampaignsMetricsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignAdwordsForbiddenConversionsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignApiKeyTrackingIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignApiKeyTrackingIdGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignApiKeyTrackingIdPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignApiKeyTrackingIdPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignApiKeyTrackingIdPUTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignApiKeyTrackingIdPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignApiKeyTrackingIdRestorePOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignAppIdIsActiveGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignAppIdPostbackPartnerIdCheckPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.core.AppMetricaCsvRawResponse;
import ru.yandex.autotests.metrika.appmetrica.core.AppMetricaCsvResponse;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.info.csv.CsvCampaign;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.TrackerReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.tracker.CampaignsMetricsParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.appmetrica.utils.AdwordsConversionValues;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.model.redirect.AppDeepLink;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.CampaignInfo;
import ru.yandex.metrika.mobmet.model.redirect.CampaignMetrics;
import ru.yandex.metrika.mobmet.model.redirect.Postback;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.UserLoginParameters.userLogin;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.single;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by graev on 02/12/2016.
 */
public class TrackerSteps extends AppMetricaBaseSteps {

    private static final Integer LIMIT_TO_FETCH_ALL_TRACKERS = 1_000_000;

    public TrackerSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Найти или создать целевую ссылку для приложения {0}")
    @ParallelExecution(ALLOW)
    public AppTargetUrl getOrCreateTargetUrl(long appId, AppTargetUrl targetUrl) {
        return getTargetUrls(appId).stream()
                .filter(u -> u.getUrl().equals(targetUrl.getUrl())) // Ищем ссылку с тем же URL
                .findAny()
                .orElseGet(() -> createTargetUrl(appId, targetUrl));
    }

    @Step("Создать целевую ссылку для приложения {0}")
    @ParallelExecution(ALLOW)
    public AppTargetUrl createTargetUrl(long appId, AppTargetUrl targetUrl) {
        return createTargetUrl(SUCCESS_MESSAGE, expectSuccess(), appId, targetUrl).getTargetUrl();
    }

    @Step("Удалить целевую ссылку {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void deleteTargetUrlAndIgnoreResult(long appId, Long targetUrlId) {
        if (targetUrlId == null) {
            return;
        }
        deleteTargetUrl(ANYTHING_MESSAGE, expectAnything(), appId, targetUrlId);
    }

    @Step("Удалить целевую ссылку {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void deleteTargetUrlAndExpectSuccess(Long appId, Long targetUrlId) {
        deleteTargetUrl(SUCCESS_MESSAGE, expectSuccess(), appId, targetUrlId);
    }

    @Step("Удалить целевую ссылку {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void deleteTargetUrlAndExpectError(Long appId, Long targetUrlId, IExpectedError error) {
        deleteTargetUrl(ERROR_MESSAGE, expectError(error), appId, targetUrlId);
    }

    @Step("Получить список целевых ссылок для приложения {0}")
    @ParallelExecution(ALLOW)
    public List<AppTargetUrl> getTargetUrls(long appId) {
        return getTargetUrls(SUCCESS_MESSAGE, expectSuccess(), appId).getTargetUrls();
    }

    @Step("Найти или создать deep link для приложения {0}")
    @ParallelExecution(ALLOW)
    public AppDeepLink getOrCreateDeepLink(long appId, AppDeepLink deepLink) {
        return getDeepLinks(appId).stream()
                .filter(u -> u.getUrl().equals(deepLink.getUrl())) // Ищем ссылку с тем же URL
                .findAny()
                .orElseGet(() -> createDeepLink(appId, deepLink));
    }

    @Step("Создать deep link для приложения {0}")
    @ParallelExecution(ALLOW)
    public AppDeepLink createDeepLink(long appId, AppDeepLink deepLink) {
        return createDeepLink(SUCCESS_MESSAGE, expectSuccess(), appId, deepLink).getDeepLink();
    }

    @Step("Удалить deep link {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void deleteDeepLinkAndIgnoreResult(long appId, long deepLinkId) {
        deleteDeepLink(ANYTHING_MESSAGE, expectAnything(), appId, deepLinkId);
    }

    @Step("Удалить deep link {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void deleteDeepLinkAndExpectSuccess(Long appId, Long deepLinkId) {
        deleteDeepLink(SUCCESS_MESSAGE, expectSuccess(), appId, deepLinkId);
    }

    @Step("Удалить deep link {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void deleteDeepLinkAndExpectError(Long appId, Long deepLinkId, IExpectedError error) {
        deleteDeepLink(ERROR_MESSAGE, expectError(error), appId, deepLinkId);
    }

    @Step("Получить список deep link-ов для приложения {0}")
    @ParallelExecution(ALLOW)
    public List<AppDeepLink> getDeepLinks(long appId) {
        return getDeepLinks(SUCCESS_MESSAGE, expectSuccess(), appId).getDeepLinks();
    }

    @Step("Получить информацию о трекере {1} приложения {0}")
    @ParallelExecution(ALLOW)
    public Campaign getTracker(long appId, String trackingId) {
        return single(getTracker(SUCCESS_MESSAGE, expectSuccess(), appId, trackingId).getCampaigns());
    }

    @Step("Получить информацию о единстенном постбеке трекера {1} приложения {0}")
    @ParallelExecution(ALLOW)
    public Postback getSinglePostback(long appId, String trackingId) {
        return single(single(getTracker(SUCCESS_MESSAGE, expectSuccess(), appId, trackingId).getCampaigns()).getPostbacks());
    }

    @Step("Получить информацию о трекере {1} приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void getTrackerAndExpectError(long appId, String trackingId, IExpectedError error) {
        getTracker(ERROR_MESSAGE, expectError(error), appId, trackingId);
    }

    @Step("Получить список трекеров для приложения {0}")
    @ParallelExecution(ALLOW)
    public List<Campaign> getTrackerList(long appId) {
        return getTrackerList(SUCCESS_MESSAGE, expectSuccess(), new TrackerReportParameters().withAppId(appId)).getCampaigns().stream()
                .map(CampaignInfo::getCampaign)
                .collect(Collectors.toList());
    }

    @Step("Получить список трекеров для приложения {0} пользователя {1}")
    @ParallelExecution(ALLOW)
    public List<Campaign> getTrackerList(long appId, long uid) {
        return getTrackerList(SUCCESS_MESSAGE, expectSuccess(), new TrackerReportParameters().withAppId(appId).withUid(uid)).getCampaigns().stream()
                .map(CampaignInfo::getCampaign)
                .collect(Collectors.toList());
    }

    @Step("Получить все трекеры пользователя")
    @ParallelExecution(ALLOW)
    public List<Campaign> getTrackerList() {
        return getTrackerList(SUCCESS_MESSAGE, expectSuccess(), new TrackerReportParameters()).getCampaigns().stream()
                .map(CampaignInfo::getCampaign)
                .collect(Collectors.toList());
    }

    @Step("Привязать партнера {0} к пользователю {1}, если этого еще не произошло")
    @ParallelExecution(ALLOW)
    public void createAgencyAccountIfNotExists(long partnerId, String login) {
        final List<String> accounts = getAgencyAccounts(partnerId);

        if (!accounts.contains(login)) {
            createAgencyAccount(partnerId, login);
        }
    }

    @Step("Получить список аккаунтов для партнера {0}")
    @ParallelExecution(ALLOW)
    private List<String> getAgencyAccounts(long partnerId) {
        return getAgencyAccounts(SUCCESS_MESSAGE, expectSuccess(), partnerId).getList();
    }

    @Step("Привязать партнера {0} к пользователю {1}")
    @ParallelExecution(ALLOW)
    private void createAgencyAccount(long partnerId, String login) {
        createAgencyAccount(SUCCESS_MESSAGE, expectSuccess(), partnerId, login);
    }

    @Step("Отвязать партнера {0} от пользователя {1} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void unbindAgencyAccountAndIgnoreResult(long partnerId, String login) {
        unbindAgencyAccount(ANYTHING_MESSAGE, expectAnything(), partnerId, login);
    }

    @Step("Получить свободный ID трекера")
    @ParallelExecution(ALLOW)
    public String generateNewTrackerId() {
        return generateNewTrackerId(SUCCESS_MESSAGE, expectSuccess()).getTrackingId();
    }

    @Step("Создать трекер {1} для приложения {0}")
    @ParallelExecution(RESTRICT)
    public Campaign createTracker(long appId, CampaignWrapper tracker) {
        String trackingId = generateNewTrackerId();
        return single(createTracker(SUCCESS_MESSAGE, expectSuccess(), appId, trackingId, tracker.getCampaign(), false).getCampaigns());
    }

    @Step("Создать трекер {1} для приложения {0} с проверкой активности {2}")
    @ParallelExecution(RESTRICT)
    public Campaign createTracker(long appId, CampaignWrapper tracker, boolean activeAppCheck) {
        String trackingId = generateNewTrackerId();
        return single(createTracker(SUCCESS_MESSAGE, expectSuccess(), appId, trackingId, tracker.getCampaign(), activeAppCheck).getCampaigns());
    }

    @Step("Создать трекер {2} с Tracking ID {1} для приложения {0}")
    @ParallelExecution(RESTRICT)
    public Campaign createTracker(long appId, String trackingId, CampaignWrapper tracker) {
        return single(createTracker(SUCCESS_MESSAGE, expectSuccess(), appId, trackingId, tracker.getCampaign(), false).getCampaigns());
    }

    @Step("Создать трекер {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(RESTRICT)
    public void createTrackerAndExpectError(long appId, CampaignWrapper tracker, IExpectedError error) {
        String trackingId = generateNewTrackerId();
        createTracker(ERROR_MESSAGE, expectError(error), appId, trackingId, tracker.getCampaign(), false);
    }

    @Step("Создать трекер {1} для приложения {0} с проверкой активности {2} и ожидать ошибку {3}")
    @ParallelExecution(RESTRICT)
    public void createTrackerAndExpectError(long appId, CampaignWrapper tracker, boolean activeAppCheck, IExpectedError error) {
        String trackingId = generateNewTrackerId();
        createTracker(ERROR_MESSAGE, expectError(error), appId, trackingId, tracker.getCampaign(), activeAppCheck);
    }

    @Step("Создать трекер {2} с Tracking ID {1} для приложения {0} и ожидать ошибку {3}")
    @ParallelExecution(RESTRICT)
    public void createTrackerAndExpectError(long appId, String trackingId, CampaignWrapper tracker, IExpectedError error) {
        createTracker(ERROR_MESSAGE, expectError(error), appId, trackingId, tracker.getCampaign(), false);
    }

    @Step("Редактировать трекер {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public Campaign editTracker(long appId, String trackingId, CampaignWrapper tracker) {
        return single(editTracker(SUCCESS_MESSAGE, expectSuccess(), appId, trackingId, tracker.getCampaign()).getCampaigns());
    }

    @Step("Редактировать трекер {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void editTrackerAndExpectError(long appId, String trackingId, CampaignWrapper tracker, IExpectedError error) {
        editTracker(ERROR_MESSAGE, expectError(error), appId, trackingId, tracker.getCampaign()).getCampaigns();
    }

    @Step("Удалить трекер {1} приложения {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void removeTrackerAndIgnoreResult(Long appId, String trackingId) {
        if (appId == null || trackingId == null) {
            return;
        }
        removeTracker(ANYTHING_MESSAGE, expectAnything(), appId, trackingId);
    }

    @Step("Удалить трекер {1} приложения {0}")
    @ParallelExecution(ALLOW)
    public void removeTracker(long appId, String trackingId) {
        removeTracker(SUCCESS_MESSAGE, expectSuccess(), appId, trackingId);
    }

    @Step("Восстановить трекер {1} приложения {0}")
    @ParallelExecution(ALLOW)
    public void restoreTracker(long appId, String trackingId) {
        restoreTracker(SUCCESS_MESSAGE, expectSuccess(), appId, trackingId);
    }

    @Step("Восстановить трекер {1} приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void restoreTrackerAndExpectError(long appId, String trackingId, IExpectedError error) {
        restoreTracker(SUCCESS_MESSAGE, expectError(error), appId, trackingId);
    }

    @Step("Получить метрики для трекеров {0}")
    @ParallelExecution(ALLOW)
    public List<CampaignMetrics> getTrackerMetrics(List<String> trackingIds) {
        return getTrackerMetrics(SUCCESS_MESSAGE, expectSuccess(), trackingIds).getMetrics();
    }

    @Step("Получить метрики для трекеров {0} пользователя {1}")
    @ParallelExecution(ALLOW)
    public List<CampaignMetrics> getTrackerMetrics(List<String> trackingIds, long uid) {
        return getTrackerMetrics(SUCCESS_MESSAGE, expectSuccess(), trackingIds, uid).getMetrics();
    }

    @Step("Запросить метрики для трекеров {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public List<CampaignMetrics> getTrackerMetricsAndExpectError(List<String> trackingIds, IExpectedError error) {
        return getTrackerMetrics(ERROR_MESSAGE, expectError(error), trackingIds).getMetrics();
    }

    @Step("Получить список трекеров из запроса csv с локалью {0}")
    @ParallelExecution(ALLOW)
    public AppMetricaCsvResponse<CsvCampaign> getTrackerCsv(String locale) {
        return get(AppMetricaCsvRawResponse.class,
                "management/v1/tracking/campaigns.csv",
                new CommonReportParameters().withLang(locale))
                .withMapper(CsvCampaign::new);
    }

    @Step("Получить видимые конверсии AdWords для пользователя {0}")
    @ParallelExecution(ALLOW)
    public List<AdwordsConversionValues> getAdwordsConversions(User user) {
        return getAdwordsConversions(SUCCESS_MESSAGE, expectSuccess()).getResponse().stream()
                .map(AdwordsConversionValues::of)
                .collect(Collectors.toList());
    }

    @Step("Проверить, активно ли приложение {0}")
    @ParallelExecution(RESTRICT)
    public String isAppActive(long appId) {
        return isAppActive(SUCCESS_MESSAGE, expectSuccess(), appId).getCheck();
    }

    @Step("Проверить постбек для приложения {0} и партнёра {1}")
    @ParallelExecution(ALLOW)
    public RedirectsCampaignAppIdPostbackPartnerIdCheckPUTSchema checkPostback(long appId, long partnerId,
                                                                               Postback postback) {
        return checkPostback(SUCCESS_MESSAGE, expectSuccess(), appId, partnerId, postback);
    }

    private RedirectsCampaignApiKeyTrackingIdGETSchema getTracker(String message, Matcher matcher,
                                                                  long appId, String trackingId) {
        RedirectsCampaignApiKeyTrackingIdGETSchema result = get(
                RedirectsCampaignApiKeyTrackingIdGETSchema.class,
                format("/redirects/campaign/%s/%s", appId, trackingId));

        assertThat(message, result, matcher);

        return result;
    }

    private RedirectsCampaignApiKeyTrackingIdPUTSchema editTracker(String message, Matcher matcher, long appId,
                                                                   String trackingId, Campaign tracker) {
        RedirectsCampaignApiKeyTrackingIdPUTSchema result = put(
                RedirectsCampaignApiKeyTrackingIdPUTSchema.class,
                format("/redirects/campaign/%s/%s", appId, trackingId),
                new RedirectsCampaignApiKeyTrackingIdPUTRequestSchema().withCampaign(tracker));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1TrackingCampaignsGETSchema getTrackerList(String message, Matcher matcher, TrackerReportParameters params) {
        ManagementV1TrackingCampaignsGETSchema result = get(
                ManagementV1TrackingCampaignsGETSchema.class,
                "/management/v1/tracking/campaigns",
                params.withLimit(LIMIT_TO_FETCH_ALL_TRACKERS));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1TrackingCampaignNewIdGETSchema generateNewTrackerId(String message, Matcher matcher) {
        ManagementV1TrackingCampaignNewIdGETSchema result = get(
                ManagementV1TrackingCampaignNewIdGETSchema.class,
                "/management/v1/tracking/campaign/new_id");

        assertThat(message, result, matcher);

        return result;
    }

    private RedirectsCampaignApiKeyTrackingIdPOSTSchema createTracker(String message, Matcher matcher,
                                                                      long appId, String trackingId, Campaign tracker,
                                                                      boolean activeAppCheck) {
        RedirectsCampaignApiKeyTrackingIdPOSTSchema result = post(
                RedirectsCampaignApiKeyTrackingIdPOSTSchema.class,
                format("/redirects/campaign/%s/%s", appId, trackingId),
                new RedirectsCampaignApiKeyTrackingIdPOSTRequestSchema().withCampaign(tracker),
                FreeFormParameters.makeParameters().append("active_app_check", activeAppCheck));

        assertThat(message, result, matcher);

        return result;
    }

    private void removeTracker(String message, Matcher matcher, long appId, String trackingId) {
        RedirectsCampaignApiKeyTrackingIdDELETESchema result = delete(
                RedirectsCampaignApiKeyTrackingIdDELETESchema.class,
                format("/redirects/campaign/%s/%s", appId, trackingId));

        assertThat(message, result, matcher);
    }

    private void restoreTracker(String message, Matcher matcher, long appId, String trackingId) {
        RedirectsCampaignApiKeyTrackingIdRestorePOSTSchema result = post(
                RedirectsCampaignApiKeyTrackingIdRestorePOSTSchema.class,
                format("/redirects/campaign/%s/%s/restore", appId, trackingId),
                null);

        assertThat(message, result, matcher);
    }

    private ManagementV1ApplicationApiKeyTrackingTargetUrlsGETSchema getTargetUrls(String message, Matcher matcher,
                                                                                   long appId) {
        ManagementV1ApplicationApiKeyTrackingTargetUrlsGETSchema result = get(
                ManagementV1ApplicationApiKeyTrackingTargetUrlsGETSchema.class,
                format("/management/v1/application/%s/tracking/target_urls", appId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationApiKeyTrackingTargetUrlsPOSTSchema createTargetUrl(String message, Matcher matcher,
                                                                                      long appId, AppTargetUrl targetUrl) {
        ManagementV1ApplicationApiKeyTrackingTargetUrlsPOSTSchema result = post(
                ManagementV1ApplicationApiKeyTrackingTargetUrlsPOSTSchema.class,
                format("/management/v1/application/%s/tracking/target_urls", appId),
                new ManagementV1ApplicationApiKeyTrackingTargetUrlsPOSTRequestSchema().withTargetUrl(targetUrl));

        assertThat(message, result, matcher);

        return result;
    }

    private void deleteTargetUrl(String message, Matcher matcher, long appId, long targetUrlId) {
        ManagementV1ApplicationApiKeyTrackingTargetUrlIdDELETESchema result = delete(
                ManagementV1ApplicationApiKeyTrackingTargetUrlIdDELETESchema.class,
                format("/management/v1/application/%s/tracking/target_url/%s", appId, targetUrlId));

        assertThat(message, result, matcher);
    }

    private ManagementV1ApplicationApiKeyTrackingDeepLinksGETSchema getDeepLinks(String message, Matcher matcher,
                                                                                 long appId) {
        ManagementV1ApplicationApiKeyTrackingDeepLinksGETSchema result = get(
                ManagementV1ApplicationApiKeyTrackingDeepLinksGETSchema.class,
                format("/management/v1/application/%s/tracking/deep_links", appId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationApiKeyTrackingDeepLinksPOSTSchema createDeepLink(String message, Matcher matcher,
                                                                                    long appId, AppDeepLink deepLink) {
        ManagementV1ApplicationApiKeyTrackingDeepLinksPOSTSchema result = post(
                ManagementV1ApplicationApiKeyTrackingDeepLinksPOSTSchema.class,
                format("/management/v1/application/%s/tracking/deep_links", appId),
                new ManagementV1ApplicationApiKeyTrackingDeepLinksPOSTRequestSchema().withDeepLink(deepLink));

        assertThat(message, result, matcher);

        return result;
    }

    private void deleteDeepLink(String message, Matcher matcher, long appId, long deepLinkId) {
        ManagementV1ApplicationApiKeyTrackingDeepLinkIdDELETESchema result = delete(
                ManagementV1ApplicationApiKeyTrackingDeepLinkIdDELETESchema.class,
                format("/management/v1/application/%s/tracking/deep_link/%s", appId, deepLinkId));

        assertThat(message, result, matcher);
    }

    private InternalPartnerAccountsPartnerIdGETSchema getAgencyAccounts(String message, Matcher matcher, long partnerId) {
        InternalPartnerAccountsPartnerIdGETSchema result = get(
                InternalPartnerAccountsPartnerIdGETSchema.class,
                format("/internal/partner/accounts/%s", partnerId));

        assertThat(message, result, matcher);

        return result;
    }

    private void createAgencyAccount(String message, Matcher matcher, long partnerId, String login) {
        InternalPartnerAccountsPartnerIdBindPOSTSchema result = post(
                InternalPartnerAccountsPartnerIdBindPOSTSchema.class,
                format("/internal/partner/accounts/%s/bind", partnerId),
                userLogin(login));

        assertThat(message, result, matcher);
    }

    private void unbindAgencyAccount(String message, Matcher matcher, long partnerId, String login) {
        InternalPartnerAccountsPartnerIdDELETESchema result = delete(
                InternalPartnerAccountsPartnerIdDELETESchema.class,
                format("/internal/partner/accounts/%s", partnerId),
                userLogin(login));

        assertThat(message, result, matcher);
    }

    private ManagementV1TrackingCampaignsMetricsGETSchema getTrackerMetrics(String message,
                                                                            Matcher matcher,
                                                                            List<String> trackingIds) {
        ManagementV1TrackingCampaignsMetricsGETSchema result = get(
                ManagementV1TrackingCampaignsMetricsGETSchema.class,
                "/management/v1/tracking/campaigns/metrics",
                new CampaignsMetricsParameters().withTrackingIds(trackingIds));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1TrackingCampaignsMetricsGETSchema getTrackerMetrics(String message,
                                                                            Matcher matcher,
                                                                            List<String> trackingIds,
                                                                            long uid) {
        ManagementV1TrackingCampaignsMetricsGETSchema result = get(
                ManagementV1TrackingCampaignsMetricsGETSchema.class,
                "/management/v1/tracking/campaigns/metrics",
                new CampaignsMetricsParameters().withTrackingIds(trackingIds).withUid(uid));

        assertThat(message, result, matcher);

        return result;
    }

    private RedirectsCampaignAdwordsForbiddenConversionsGETSchema getAdwordsConversions(String message, Matcher matcher) {
        RedirectsCampaignAdwordsForbiddenConversionsGETSchema result = get(
                RedirectsCampaignAdwordsForbiddenConversionsGETSchema.class,
                "/redirects/campaign/adwords/forbidden/conversions"
        );

        assertThat(message, result, matcher);

        return result;
    }

    private RedirectsCampaignAppIdIsActiveGETSchema isAppActive(String message, Matcher matcher, long appId) {
        RedirectsCampaignAppIdIsActiveGETSchema result = get(
                RedirectsCampaignAppIdIsActiveGETSchema.class,
                format("/redirects/campaign/%s/is_active", appId)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private RedirectsCampaignAppIdPostbackPartnerIdCheckPUTSchema checkPostback(String message,
                                                                                Matcher matcher,
                                                                                long appId,
                                                                                long partnerId,
                                                                                Postback postback) {
        RedirectsCampaignAppIdPostbackPartnerIdCheckPUTSchema result = put(
                RedirectsCampaignAppIdPostbackPartnerIdCheckPUTSchema.class,
                format("/redirects/campaign/%s/postback/%s/check", appId, partnerId),
                postback
        );

        assertThat(message, result, matcher);

        return result;
    }
}
