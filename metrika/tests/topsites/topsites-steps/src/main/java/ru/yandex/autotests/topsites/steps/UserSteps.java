package ru.yandex.autotests.topsites.steps;

import org.apache.http.client.config.RequestConfig;
import ru.yandex.autotests.httpclientlite.core.response.multi.MultiParserAdapter;
import ru.yandex.autotests.metrika.commons.clients.http.*;
import ru.yandex.autotests.metrika.commons.clients.http.logger.HttpClientLiteLogger;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.schemas.CsvResponseSchema;
import ru.yandex.autotests.metrika.commons.schemas.XlsxResponseSchema;
import ru.yandex.autotests.topsites.properties.TopSitesProperties;

import static ru.yandex.autotests.httpclientlite.utils.client.HttpClientBuilderUtils.defaultTestConfiguration;
import static ru.yandex.autotests.topsites.core.TopSitesJson.GSON_REQUEST;
import static ru.yandex.autotests.topsites.core.TopSitesJson.GSON_RESPONSE;

public class UserSteps {

    private final TopSitesSteps topSitesSteps;

    public UserSteps() {
        HttpClientLite client = new HttpClientLite.Builder()
                .withClient(defaultTestConfiguration()
                        .setDefaultRequestConfig(RequestConfig
                                .custom()
                                .setSocketTimeout(HttpClientTimeoutProperties.getInstance().getReadTimeout() * 1000)
                                .setConnectTimeout(HttpClientTimeoutProperties.getInstance().getConnectTimeout() * 1000)
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

        topSitesSteps = new TopSitesSteps(TopSitesProperties.getInstance().getApiUrl(), client);
    }

    public TopSitesSteps onTopSitesSteps() {
        return topSitesSteps;
    }
}
