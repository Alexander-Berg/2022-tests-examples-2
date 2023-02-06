package ru.yandex.autotests.metrika.steps;

import java.net.URL;

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

import ru.yandex.autotests.httpclient.lite.core.config.AllowAllSSLContext;
import ru.yandex.autotests.httpclient.lite.core.config.HttpClientConnectionConfig;
import ru.yandex.autotests.httpclient.lite.core.config.HttpStepsConfig;
import ru.yandex.autotests.httpclient.lite.core.steps.BackEndBaseSteps;
import ru.yandex.autotests.metrika.core.MetrikaRequestBuilder;
import ru.yandex.autotests.metrika.core.MetrikaResponseHandler;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.data.parameters.CommonHeaders;
import ru.yandex.autotests.metrika.data.parameters.CommonParameters;
import ru.yandex.autotests.metrika.properties.HttpClientProperties;
import ru.yandex.autotests.metrika.properties.MetrikaApiProperties;
import ru.yandex.autotests.metrika.steps.internal.InternalSteps;
import ru.yandex.autotests.metrika.steps.metadata.MetadataSteps;
import ru.yandex.autotests.metrika.steps.metadata.UserCentricMetadataSteps;
import ru.yandex.autotests.metrika.steps.metadata.WebVisorMetadataSteps;
import ru.yandex.autotests.metrika.steps.report.InpageSteps;
import ru.yandex.autotests.metrika.steps.report.ReportSteps;
import ru.yandex.autotests.metrika.steps.report.ResultSteps;
import ru.yandex.autotests.metrika.steps.report.WebVisorSteps;

import static org.apache.commons.lang3.StringUtils.isBlank;

/**
 * Created by proxeter (Nikolay Mulyar - proxeter@yandex-team.ru) on 17.06.2014.
 */
public class UserSteps {

    private HttpStepsConfig httpStepsConfig;

    private HttpStepsConfig httpFacedConfig;

    private final CommonParameters commonParameters;

    private final CommonHeaders commonHeaders;

    public UserSteps() {
        useTesting();
        commonParameters = new CommonParameters()
                .withPretty(true)
                .withRequestSource("interface")
                .withRequestDomain("ru")
                .withLang("ru");
        commonHeaders = new CommonHeaders()
                .withOAuthToken(Users.MANAGER_DIRECT.get(User.OAUTH_TOKEN));
        httpFacedConfig = getHttpStepsConfig(
                getClientConnectionConfig(MetrikaApiProperties.getInstance().getFacedTesting()));

    }

    private static HttpClientConnectionConfig getClientConnectionConfig(URL url) {
        return new HttpClientConnectionConfig()
                .scheme(url.getProtocol())
                .host(url.getHost())
                .port(url.getPort());
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

    public MetadataSteps onMetadataSteps() {
        return createStepsWithCommonSettings(MetadataSteps.class, httpFacedConfig);
    }

    public WebVisorMetadataSteps onWebVisorMetadataSteps() {
        return createStepsWithCommonSettings(WebVisorMetadataSteps.class);
    }

    public UserCentricMetadataSteps onUserCentricMetadataSteps() {
        return createStepsWithCommonSettings(UserCentricMetadataSteps.class);
    }

    public WebVisorSteps onWebVisorSteps() {
        return createStepsWithCommonSettings(WebVisorSteps.class);
    }

    public ResultSteps onResultSteps() {
        return createStepsWithHttpConfigOnly(ResultSteps.class);
    }

    public ReportSteps onReportSteps() {
        return createStepsWithCommonSettings(ReportSteps.class);
    }

    // Нужно сходить в faced чтобы получить список урлов, для которых строить inpage отчеты
    public ReportSteps onReportFacedSteps() {
        return createStepsWithCommonSettings(ReportSteps.class, httpFacedConfig);
    }


    public InternalSteps onInternalSteps() {
        return createStepsWithCommonSettings(InternalSteps.class);
    }

    public InpageSteps onInpageSteps() {
        return createStepsWithCommonSettings(InpageSteps.class);
    }


    public UserSteps withUser(User user) {
        commonHeaders.withOAuthToken(user.get(User.OAUTH_TOKEN));
        return this;
    }

    public UserSteps withPretty(boolean isPretty) {
        commonParameters.setPretty(isPretty);
        return this;
    }

    public UserSteps withRequestSource(String requestSource) {
        commonParameters.setRequestSource(requestSource);
        return this;
    }

    public UserSteps withLang(String lang) {
        commonParameters.setLang(lang);
        return this;
    }

    public UserSteps withDefaultAccuracy() {
        if (!isBlank(MetrikaApiProperties.getInstance().getDefaultAccuracy())) {
            commonParameters.setDefaultAccuracy(MetrikaApiProperties.getInstance().getDefaultAccuracy());
        }
        return this;
    }

    public UserSteps useTesting() {
        httpStepsConfig = getHttpStepsConfig(
                getClientConnectionConfig(MetrikaApiProperties.getInstance().getApiTesting()));
        return this;
    }

    public UserSteps useReference() {
        httpStepsConfig = getHttpStepsConfig(
                getClientConnectionConfig(MetrikaApiProperties.getInstance().getApiReference()));
        return this;
    }

    private <T extends MetrikaBaseSteps> T createStepsWithCommonSettings(Class<T> stepsClass) {
        return createStepsWithCommonSettings(stepsClass, httpStepsConfig);
    }

    private <T extends MetrikaBaseSteps> T createStepsWithCommonSettings(Class<T> stepsClass, HttpStepsConfig httpStepsConfig) {
        return BackEndBaseSteps.getInstance(stepsClass, httpStepsConfig)
                .withCommonParameters(commonParameters)
                .withCommonHeaders(commonHeaders);
    }

    private <T extends BackEndBaseSteps> T createStepsWithHttpConfigOnly(Class<T> stepsClass) {
        return BackEndBaseSteps.getInstance(stepsClass, httpStepsConfig);
    }
}
