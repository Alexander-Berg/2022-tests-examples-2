package ru.yandex.autotests.advapi.steps;

import org.apache.http.Header;
import org.apache.http.HttpHost;
import org.apache.http.client.HttpClient;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.config.Registry;
import org.apache.http.config.RegistryBuilder;
import org.apache.http.conn.HttpClientConnectionManager;
import org.apache.http.conn.socket.ConnectionSocketFactory;
import org.apache.http.conn.socket.PlainConnectionSocketFactory;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.impl.client.StandardHttpRequestRetryHandler;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.apache.http.message.BasicHeader;
import ru.yandex.autotests.advapi.core.MetrikaRequestBuilder;
import ru.yandex.autotests.advapi.core.MetrikaResponseHandler;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.parameters.CommonHeaders;
import ru.yandex.autotests.advapi.parameters.CommonParameters;
import ru.yandex.autotests.advapi.properties.AdvApiProperties;
import ru.yandex.autotests.advapi.properties.HttpClientProperties;
import ru.yandex.autotests.advapi.steps.management.AdvertisersSteps;
import ru.yandex.autotests.advapi.steps.management.CampaignsSteps;
import ru.yandex.autotests.advapi.steps.management.PlacementsSteps;
import ru.yandex.autotests.advapi.steps.management.SitesSteps;
import ru.yandex.autotests.advapi.steps.report.BaseReportSteps;
import ru.yandex.autotests.advapi.steps.report.MetadataSteps;
import ru.yandex.autotests.advapi.steps.report.ReportSteps;
import ru.yandex.autotests.advapi.steps.report.ResultSteps;
import ru.yandex.autotests.httpclient.lite.core.config.AllowAllSSLContext;
import ru.yandex.autotests.httpclient.lite.core.config.HttpClientConnectionConfig;
import ru.yandex.autotests.httpclient.lite.core.config.HttpStepsConfig;
import ru.yandex.autotests.httpclient.lite.core.steps.BackEndBaseSteps;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.httpclientlite.core.response.multi.MultiParserAdapter;
import ru.yandex.autotests.metrika.commons.clients.http.*;
import ru.yandex.autotests.metrika.commons.clients.http.logger.HttpClientLiteLogger;
import ru.yandex.autotests.metrika.commons.schemas.CsvResponseSchema;
import ru.yandex.autotests.metrika.commons.schemas.XlsxResponseSchema;

import java.net.URL;

import static org.apache.commons.lang3.StringUtils.isBlank;
import static ru.yandex.autotests.advapi.Utils.toUrl;
import static ru.yandex.autotests.advapi.core.AdvApiJson.GSON_REQUEST;
import static ru.yandex.autotests.advapi.core.AdvApiJson.GSON_RESPONSE;
import static ru.yandex.autotests.advapi.data.users.User.OAUTH_TOKEN;
import static ru.yandex.autotests.httpclientlite.utils.client.HttpClientBuilderUtils.defaultTestConfiguration;

public class UserSteps {

    private HttpStepsConfig  httpStepsConfig;
    private User user;

    private final CommonParameters commonParameters = new CommonParameters()
            .withLang("ru");

    private final AdvertisersSteps advertisersSteps;
    private final CampaignsSteps campaignsSteps;
    private final PlacementsSteps placementsSteps;
    private final SitesSteps sitesSteps;

    public UserSteps() {
        HttpClientLite client = new HttpClientLite.Builder()
                .withClient(defaultTestConfiguration()
                        .setDefaultRequestConfig(RequestConfig
                                .custom()
                                .setSocketTimeout(HttpClientTimeoutProperties.getInstance().getReadTimeout())
                                .setConnectTimeout(HttpClientTimeoutProperties.getInstance().getConnectTimeout())
                                .build())
                        .build())
                .withRequestBuilder(new JsonRequestBuilder(GSON_REQUEST))
                .withResponseParser(new MultiParserAdapter()
                        .registerDefault(new JsonResponseParser(GSON_RESPONSE))
                        .register(CsvResponseSchema.class, new CsvResponseParser())
                        .register(XlsxResponseSchema.class, new XlsxResponseParser())
                )
                .withLogger(new HttpClientLiteLogger())
                .build();

        advertisersSteps = new AdvertisersSteps(AdvApiProperties.getInstance().getApiUrl(), client);
        campaignsSteps = new CampaignsSteps(AdvApiProperties.getInstance().getApiUrl(), client);
        placementsSteps = new PlacementsSteps(AdvApiProperties.getInstance().getApiUrl(), client);
        sitesSteps = new SitesSteps(AdvApiProperties.getInstance().getApiUrl(), client);
    }

    private UserSteps(Builder builder) {
        user = builder.user;

        HttpClientLite client = new HttpClientLite.Builder()
                .withClient(defaultTestConfiguration()
                        .setDefaultRequestConfig(RequestConfig
                                .custom()
                                .setSocketTimeout(HttpClientTimeoutProperties.getInstance().getReadTimeout())
                                .setConnectTimeout(HttpClientTimeoutProperties.getInstance().getConnectTimeout())
                                .build())
                        .build())
                .withRequestBuilder(new JsonRequestBuilder(GSON_REQUEST)
                        .withCommonParameters(commonParameters)
                        .setHeaders(new CommonHeaders()
                                .withOAuthToken(builder.user.get(OAUTH_TOKEN))
                                .getParameters()
                                .stream()
                                .map(p -> new BasicHeader(p.getName(), p.getValue()))
                                .toArray(Header[]::new)))
                .withResponseParser(new JsonResponseParser(GSON_RESPONSE))
                .withLogger(new HttpClientLiteLogger())
                .build();

        advertisersSteps = new AdvertisersSteps(AdvApiProperties.getInstance().getApiUrl(), client);
        campaignsSteps = new CampaignsSteps(AdvApiProperties.getInstance().getApiUrl(), client);
        placementsSteps = new PlacementsSteps(AdvApiProperties.getInstance().getApiUrl(), client);
        sitesSteps = new SitesSteps(AdvApiProperties.getInstance().getApiUrl(), client);
    }

    private static HttpStepsConfig getHttpStepsConfig(HttpClientConnectionConfig httpClientConnectionConfig) {
        return new HttpStepsConfig()
                .useClientConfig(httpClientConnectionConfig)
                .useRequestBuilder(new MetrikaRequestBuilder(httpClientConnectionConfig))
                .useHandler(new MetrikaResponseHandler())
                .useHttpClient(getHttpClientWithCustomTimeouts(httpClientConnectionConfig));
    }

    private static HttpClient getHttpClientWithCustomTimeouts(HttpClientConnectionConfig config) {
        SSLConnectionSocketFactory sslConnectionSocketFactory = new SSLConnectionSocketFactory(
                AllowAllSSLContext.get(),
                SSLConnectionSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER);

        ConnectionSocketFactory plainConnectionSocketFactory = PlainConnectionSocketFactory.getSocketFactory();

        Registry<ConnectionSocketFactory> r = RegistryBuilder.<ConnectionSocketFactory>create()
                .register("http", plainConnectionSocketFactory)
                .register("https", sslConnectionSocketFactory)
                .build();

        HttpClientConnectionManager cm = new PoolingHttpClientConnectionManager(r);

        HttpHost proxy = null;
        if (config.getProxyAddress() != null && config.getProxyPort() != null) {
            proxy = new HttpHost(config.getProxyAddress(), config.getProxyPort());
        }

        return HttpClients.custom()
                .setConnectionManager(cm)
                .setProxy(proxy)
                .setDefaultRequestConfig(RequestConfig
                        .custom()
                        .setSocketTimeout(HttpClientProperties.getInstance().getSocketTimeout())
                        .setConnectTimeout(HttpClientProperties.getInstance().getConnectTimeout())
                        .build())
                .setRetryHandler(StandardHttpRequestRetryHandler.INSTANCE)
                .build();
    }

    private static HttpClientConnectionConfig getClientConnectionConfig(URL url) {
        return new HttpClientConnectionConfig()
                .scheme(url.getProtocol())
                .host(url.getHost())
                .port(url.getPort());
    }

    private <T extends BaseReportSteps> T createStepsWithCommonSettings(Class<T> stepsClass) {
        CommonHeaders headers = new CommonHeaders();
        if (user != null) {
            headers.withOAuthToken(user.get(OAUTH_TOKEN));
        }
        return BackEndBaseSteps.getInstance(stepsClass, httpStepsConfig)
                .withCommonParameters(commonParameters)
                .withCommonHeaders(headers);
    }

    private <T extends BackEndBaseSteps> T createStepsWithHttpConfigOnly(Class<T> stepsClass) {
        return BackEndBaseSteps.getInstance(stepsClass, httpStepsConfig);
    }

    public AdvertisersSteps onAdvertisersSteps() {
        return advertisersSteps;
    }

    public CampaignsSteps onCampaignsSteps() {
        return campaignsSteps;
    }

    public PlacementsSteps onPlacementsSteps() {
        return placementsSteps;
    }

    public SitesSteps onSitesSteps() {
        return sitesSteps;
    }

    public ReportSteps onReportSteps() {
        return createStepsWithCommonSettings(ReportSteps.class);
    }

    public ResultSteps onResultSteps() {
        return createStepsWithHttpConfigOnly(ResultSteps.class);
    }

    public MetadataSteps onMetadataSteps() {
        return createStepsWithCommonSettings(MetadataSteps.class);
    }

    public static UserSteps withUser(User user) {
        return new Builder()
                .withUser(user)
                .withBaseUrl(AdvApiProperties.getInstance().getApiUrl())
                .build();
    }

    public UserSteps withDefaultAccuracy() {
        if (!isBlank(AdvApiProperties.getInstance().getDefaultAccuracy())) {
            commonParameters.setDefaultAccuracy(AdvApiProperties.getInstance().getDefaultAccuracy());
        }
        return this;
    }

    public UserSteps useTesting() {
        httpStepsConfig = getHttpStepsConfig(
                getClientConnectionConfig(toUrl(AdvApiProperties.getInstance().getApiTesting())));
        return this;
    }

    public UserSteps useReference() {
        httpStepsConfig = getHttpStepsConfig(
                getClientConnectionConfig(toUrl(AdvApiProperties.getInstance().getApiReference())));
        return this;
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private URL baseUrl;
        private User user;

        public Builder withBaseUrl(final URL baseUrl) {
            this.baseUrl = baseUrl;
            return this;
        }

        public Builder withUser(final User user) {
            this.user = user;
            return this;
        }

        public UserSteps build() {
            return new UserSteps(this);
        }
    }
}
