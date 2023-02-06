package ru.yandex.autotests.internalapid.steps;

import java.net.URL;
import java.util.Collections;

import org.apache.http.Header;
import org.apache.http.client.HttpClient;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.message.BasicHeader;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.httpclientlite.core.response.multi.MultiParserAdapter;
import ru.yandex.autotests.internalapid.beans.data.User;
import ru.yandex.autotests.internalapid.beans.data.Users;
import ru.yandex.autotests.internalapid.properties.InternalApiProperties;
import ru.yandex.autotests.internalapid.properties.TvmProperties;
import ru.yandex.autotests.metrika.commons.clients.http.CsvResponseParser;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientTimeoutProperties;
import ru.yandex.autotests.metrika.commons.clients.http.JsonRequestBuilder;
import ru.yandex.autotests.metrika.commons.clients.http.JsonResponseParser;
import ru.yandex.autotests.metrika.commons.clients.http.XlsxResponseParser;
import ru.yandex.autotests.metrika.commons.clients.http.logger.HttpClientLiteLogger;
import ru.yandex.autotests.metrika.commons.schemas.CsvResponseSchema;
import ru.yandex.autotests.metrika.commons.schemas.XlsxResponseSchema;
import ru.yandex.autotests.metrika.commons.vault.VaultClient;
import ru.yandex.inside.passport.tvm2.Tvm2;
import ru.yandex.inside.passport.tvm2.TvmClientCredentials;
import ru.yandex.library.ticket_parser2.BlackboxEnv;

import static ru.yandex.autotests.httpclientlite.utils.client.HttpClientBuilderUtils.defaultTestConfiguration;
import static ru.yandex.autotests.internalapid.steps.InternalApiJson.GSON_REQUEST;
import static ru.yandex.autotests.internalapid.steps.InternalApiJson.GSON_RESPONSE;

public class UserSteps {

    private final InternalApiSteps internalApiSteps;
    private final CrmFallbackSteps crmFallbackSteps;
    private final DirectSteps directSteps;
    private final DirectSteps directRefSteps;
    private final DirectAdsConnectorsSteps directAdsConnectorsSteps;
    private final DirectAdsConnectorsSteps directAdsConnectorsStepsSimpleUser;
    private final IdmSteps idmSteps;
    private final MarketAnalyticsSteps marketAnalyticsSteps;
    private final CountersSteps countersSteps;
    private final CdpGoalsSteps cdpGoalsSteps;
    private final GrantsSteps grantsSteps;

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

        HttpClient client = defaultTestConfiguration()
                .setDefaultRequestConfig(RequestConfig
                        .custom()
                        .setSocketTimeout(HttpClientTimeoutProperties.getInstance().getReadTimeout() * 1000)
                        .setConnectTimeout(HttpClientTimeoutProperties.getInstance().getConnectTimeout() * 1000)
                        .build())
                .build();
        MultiParserAdapter responseParser = new MultiParserAdapter()
                .registerDefault(new JsonResponseParser(GSON_RESPONSE))
                .register(CsvResponseSchema.class, new CsvResponseParser())
                .register(XlsxResponseSchema.class, new XlsxResponseParser());


        BasicHeader tvmHeader = new BasicHeader("X-Ya-Service-Ticket", ticket);
        BasicHeader superUserOauth = new BasicHeader("Authorization", "OAuth " + Users.SUPER_USER.get(User.OAUTH_TOKEN));
        BasicHeader simpleUserOauth = new BasicHeader("Authorization", "OAuth " + Users.SIMPLE_USER2.get(User.OAUTH_TOKEN));
        BasicHeader urlEncodedContent = new BasicHeader("Content-Type", "application/x-www-form-urlencoded");

        HttpClientLite clientLiteMain = getHttpClientLite(client, responseParser, new Header[] {tvmHeader});
        HttpClientLite clientLiteMainWithSuperUser = getHttpClientLite(client, responseParser, new Header[] {tvmHeader, superUserOauth});
        HttpClientLite clientLiteMainWithSimpleUser = getHttpClientLite(client, responseParser, new Header[] {tvmHeader, simpleUserOauth});
        HttpClientLite clientLiteIdm =  getHttpClientLite(client, responseParser, new Header[] {tvmHeader, urlEncodedContent});

        URL apiUrl = InternalApiProperties.getInstance().getApiUrl();
        URL apiRefUrl = InternalApiProperties.getInstance().getApiRefUrl();

        internalApiSteps = new InternalApiSteps(apiUrl, clientLiteMain);
        crmFallbackSteps = new CrmFallbackSteps(apiUrl, clientLiteMain);
        directSteps = new DirectSteps(apiUrl, clientLiteMain);
        directRefSteps = new DirectSteps(apiRefUrl, clientLiteMain);
        directAdsConnectorsSteps = new DirectAdsConnectorsSteps(apiUrl, clientLiteMainWithSuperUser);
        directAdsConnectorsStepsSimpleUser = new DirectAdsConnectorsSteps(apiUrl, clientLiteMainWithSimpleUser);
        idmSteps = new IdmSteps(apiUrl, clientLiteIdm);
        marketAnalyticsSteps = new MarketAnalyticsSteps(this);
        countersSteps = new CountersSteps(apiUrl, clientLiteIdm);
        cdpGoalsSteps = new CdpGoalsSteps(apiUrl, clientLiteIdm, this);
        grantsSteps = new GrantsSteps(apiUrl, clientLiteMain);
    }

    private HttpClientLite getHttpClientLite(HttpClient client, MultiParserAdapter responseParser, Header[] headers) {
        return new HttpClientLite.Builder()
                .withClient(client)
                .withRequestBuilder(new JsonRequestBuilder(GSON_REQUEST)
                        .setHeaders(headers)).withResponseParser(responseParser)
                .withLogger(new HttpClientLiteLogger())
                .build();
    }

    public InternalApiSteps onInternalApidSteps() {
        return internalApiSteps;
    }

    public CrmFallbackSteps onCRMFallbackSteps() {
        return crmFallbackSteps;
    }

    public DirectSteps onDirectSteps() {
        return directSteps;
    }

    public DirectSteps onDirectRefSteps() {
        return directRefSteps;
    }

    public DirectAdsConnectorsSteps onDirectAdsConnectorsSteps() {
        return directAdsConnectorsSteps;
    }

    public DirectAdsConnectorsSteps onDirectAdsConnectorsStepsSimpleUser() {
        return directAdsConnectorsStepsSimpleUser;
    }

    public IdmSteps onIdmSteps() {
        return idmSteps;
    }

    public MarketAnalyticsSteps onMarketAnalyticsSteps() {
        return marketAnalyticsSteps;
    }

    public CountersSteps onCountersSteps() {
        return countersSteps;
    }

    public CdpGoalsSteps onCdpGoalsSteps() {
        return cdpGoalsSteps;
    }

    public GrantsSteps onGrantsSteps() {
        return grantsSteps;
    }
}
