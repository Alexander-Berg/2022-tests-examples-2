package ru.yandex.autotests.metrika.appmetrica.steps;

import com.google.gson.Gson;
import com.google.gson.TypeAdapterFactory;
import net.sf.cglib.proxy.Enhancer;
import org.apache.http.client.config.RequestConfig;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.httpclientlite.core.response.multi.MultiParserAdapter;
import ru.yandex.autotests.metrika.appmetrica.body.CustomEntityBody;
import ru.yandex.autotests.metrika.appmetrica.core.*;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonHeaders;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonParameters;
import ru.yandex.autotests.metrika.appmetrica.properties.HttpClientProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelismControl;

import java.net.URL;

import static ru.yandex.autotests.httpclientlite.utils.client.HttpClientBuilderUtils.defaultTestConfiguration;
import static ru.yandex.autotests.metrika.appmetrica.data.User.OAUTH_TOKEN;
import static ru.yandex.autotests.metrika.appmetrica.data.User.UID;

public class BaseUserSteps {

    private final URL baseUrl;
    private final HttpClientLite httpClient;

    protected BaseUserSteps(BaseBuilder builder) {
        this.baseUrl = builder.getBaseUrl();
        this.httpClient = createHttpClient(builder);
    }

    public URL getBaseUrl() {
        return baseUrl;
    }

    public HttpClientLite getHttpClient() {
        return httpClient;
    }

    public static HttpClientLite createHttpClient(BaseBuilder builder) {
        Gson requestGson = AppMetricaJson.createGsonRequest(builder.typeAdapterFactory);
        Gson responseGson = AppMetricaJson.createGsonResponse(builder.typeAdapterFactory);

        return new HttpClientLite.Builder()
                .withClient(defaultTestConfiguration()
                        .setDefaultRequestConfig(RequestConfig
                                .custom()
                                .setSocketTimeout(HttpClientProperties.getInstance().getReadTimeout() * 1000)
                                .setConnectTimeout(HttpClientProperties.getInstance().getConnectTimeout() * 1000)
                                .build())
                        .build())
                .withRequestBuilder(new AppMetricaRequestBuilder(requestGson)
                        .withCommonParameters(new CommonParameters().withUidReal(builder.uidReal))
                        .withCommonHeaders(new CommonHeaders().withOAuthToken(builder.oauthToken)))
                .withResponseParser(new MultiParserAdapter()
                        .register(AppMetricaCsvRawResponse.class, new AppMetricaCsvRawResponseParser())
                        .register(CustomEntityBody.class, new CustomEntityResponseParser())
                        .registerDefault(new AppMetricaJsonResponseParser(responseGson)))
                .withLogger(new HttpClientLiteLogger())
                .build();
    }

    /**
     * Оборачиваем класс степов в прокси, который будет контролировать параллельный запуск тяжелых степов.
     * Это необходимо с тех пор, как тесты запускаются на продовом КХ.
     */
    @SuppressWarnings("unchecked")
    public static <T extends AppMetricaBaseSteps> T createWithParallelismControl(Class<T> clazz, URL url, HttpClientLite client) {
        final Enhancer enhancer = new Enhancer();
        final AppMetricaBaseSteps steps = createRealStepsInstance(clazz, url, client);
        enhancer.setSuperclass(clazz);
        enhancer.setCallback(new ParallelismControl(steps));
        // Здесь над реальным объектом step-ов будет прокси, который умеет делать вызов под семафором
        return (T) enhancer.create(new Class[]{URL.class, HttpClientLite.class}, new Object[]{null, null});
    }

    /**
     * Вспомогательный метод создания экземпляров степов.
     * Предпологаем, что нужный конструктор есть.
     */
    public static <T extends AppMetricaBaseSteps> T createRealStepsInstance(Class<T> clazz, URL url, HttpClientLite client) {
        try {
            return clazz.getConstructor(URL.class, HttpClientLite.class).newInstance(url, client);
        } catch (Exception e) {
            throw new IllegalStateException("Please make sure the steps class contains required constructor", e);
        }
    }

    public static class BaseBuilder {

        private URL baseUrl;

        private String oauthToken;

        private String uidReal;

        private TypeAdapterFactory typeAdapterFactory;

        public URL getBaseUrl() {
            return baseUrl;
        }

        public BaseBuilder withBaseUrl(final URL baseUrl) {
            this.baseUrl = baseUrl;
            return this;
        }

        public BaseBuilder withUser(final User user) {
            return withOauthToken(user);
        }

        public BaseBuilder withOauthToken(final User user) {
            this.oauthToken = user.get(OAUTH_TOKEN);
            return this;
        }

        public BaseBuilder withUidReal(final User user) {
            this.uidReal = user.get(UID);
            return this;
        }

        public BaseBuilder withTypeAdapterFactory(TypeAdapterFactory typeAdapterFactory) {
            this.typeAdapterFactory = typeAdapterFactory;
            return this;
        }

        public BaseUserSteps build() {
            return new BaseUserSteps(this);
        }
    }
}
