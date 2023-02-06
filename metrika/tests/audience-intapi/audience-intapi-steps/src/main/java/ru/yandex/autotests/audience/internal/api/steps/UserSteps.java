package ru.yandex.autotests.audience.internal.api.steps;

import org.apache.http.Header;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.message.BasicHeader;
import ru.yandex.autotests.audience.internal.api.core.IntapiCryptaCSVResponseParser;
import ru.yandex.autotests.audience.internal.api.properties.AudienceInternalApiProperties;
import ru.yandex.autotests.audience.internal.api.properties.TvmProperties;
import ru.yandex.autotests.audience.internal.api.schema.custom.SegmentDataSchema;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.httpclientlite.core.response.multi.MultiParserAdapter;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientTimeoutProperties;
import ru.yandex.autotests.metrika.commons.clients.http.JsonRequestBuilder;
import ru.yandex.autotests.metrika.commons.clients.http.JsonResponseParser;
import ru.yandex.autotests.metrika.commons.clients.http.logger.HttpClientLiteLogger;
import ru.yandex.autotests.metrika.commons.vault.VaultClient;
import ru.yandex.inside.passport.tvm2.Tvm2;
import ru.yandex.inside.passport.tvm2.TvmClientCredentials;
import ru.yandex.library.ticket_parser2.BlackboxEnv;

import java.util.Collections;

import static ru.yandex.autotests.audience.internal.api.core.AudienceIntapiJson.GSON_REQUEST;
import static ru.yandex.autotests.audience.internal.api.core.AudienceIntapiJson.GSON_RESPONSE;
import static ru.yandex.autotests.httpclientlite.utils.client.HttpClientBuilderUtils.defaultTestConfiguration;

/**
 * Created by apuzikov on 30.06.17.
 *
 */
public class UserSteps {

    private final HttpClientLite client;

    public UserSteps() {
        String secret = VaultClient.loadLastVersion(TvmProperties.getInstance()
                .getEnvironment()).get(TvmProperties.getInstance().getKey());
        int clientId = TvmProperties.getInstance().getClientId();
        TvmClientCredentials credentials = new TvmClientCredentials(clientId, secret);
        Tvm2 tvm2 = new Tvm2(credentials);
        tvm2.setDstClientIds(Collections.singletonList(clientId));
        tvm2.setBlackboxEnv(BlackboxEnv.Test);
        tvm2.start();
        String ticket = tvm2.getServiceTicket(clientId).getOrThrow("Could not retrieve TVM ticket");

        client = new HttpClientLite.Builder()
                .withClient(defaultTestConfiguration()
                        .setDefaultRequestConfig(RequestConfig
                                .custom()
                                .setSocketTimeout(HttpClientTimeoutProperties.getInstance().getReadTimeout() * 1000)
                                .setConnectTimeout(HttpClientTimeoutProperties.getInstance().getConnectTimeout() * 1000)
                                .build())
                        .build())
                .withRequestBuilder(new JsonRequestBuilder(GSON_REQUEST)
                        .setHeaders(new Header[]{new BasicHeader("X-Ya-Service-Ticket", ticket)})
                )
                .withResponseParser(new MultiParserAdapter()
                        .register(SegmentDataSchema.class, new IntapiCryptaCSVResponseParser())
                        .registerDefault(new JsonResponseParser(GSON_RESPONSE)))
                .withLogger(new HttpClientLiteLogger())
                .build();
    }

    public DirectSteps onDirectSteps() {
        return new DirectSteps(AudienceInternalApiProperties.getInstance().getApiUrl(), client);
    }

    public CryptaSteps onCryptaSteps() {
        return new CryptaSteps(AudienceInternalApiProperties.getInstance().getApiUrl(), client);
    }

    public DisplaySteps onDisplaySteps() {
        return new DisplaySteps(AudienceInternalApiProperties.getInstance().getApiUrl(), client);
    }

    public ExperimentsSteps onExperimentsSteps() {
        return new ExperimentsSteps(AudienceInternalApiProperties.getInstance().getApiUrl(), client);
    }
}
