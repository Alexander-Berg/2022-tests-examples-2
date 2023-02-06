package ru.yandex.autotests.audience.steps;

import org.apache.http.Header;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.message.BasicHeader;
import ru.yandex.autotests.audience.core.BlackboxClient;
import ru.yandex.autotests.audience.core.TvmClient;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.data.users.Users;
import ru.yandex.autotests.audience.parameters.CommonHeaders;
import ru.yandex.autotests.audience.parameters.CommonParameters;
import ru.yandex.autotests.audience.properties.AudienceApiProperties;
import ru.yandex.autotests.audience.steps.management.AccountsSteps;
import ru.yandex.autotests.audience.steps.management.DelegatesSteps;
import ru.yandex.autotests.audience.steps.management.ExperimentGrantsSteps;
import ru.yandex.autotests.audience.steps.management.ExperimentSteps;
import ru.yandex.autotests.audience.steps.management.PixelsSteps;
import ru.yandex.autotests.audience.steps.management.SegmentGrantsSteps;
import ru.yandex.autotests.audience.steps.management.SegmentsSteps;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientTimeoutProperties;
import ru.yandex.autotests.metrika.commons.clients.http.JsonRequestBuilder;
import ru.yandex.autotests.metrika.commons.clients.http.JsonResponseParser;
import ru.yandex.autotests.metrika.commons.clients.http.logger.HttpClientLiteLogger;

import java.net.URL;

import static ru.yandex.autotests.audience.core.AudienceJson.GSON_REQUEST;
import static ru.yandex.autotests.audience.core.AudienceJson.GSON_RESPONSE;
import static ru.yandex.autotests.audience.data.users.User.OAUTH_TOKEN;
import static ru.yandex.autotests.httpclientlite.utils.client.HttpClientBuilderUtils.defaultTestConfiguration;

/**
 * Created by konkov on 23.03.2017.
 */
public class UserSteps {

    private final SegmentsSteps segmentsSteps;
    private final PixelsSteps pixelsSteps;
    private final SegmentGrantsSteps segmentGrantsSteps;
    private final DelegatesSteps delegatesSteps;
    private final AccountsSteps accountsSteps;
    private final ExperimentSteps experimentSteps;
    private final ExperimentGrantsSteps experimentGrantsSteps;

    private UserSteps(Builder builder) {
        URL baseUrl = builder.baseUrl;

        HttpClientLite client = new HttpClientLite.Builder()
                .withClient(defaultTestConfiguration()
                        .setDefaultRequestConfig(RequestConfig
                                .custom()
                                .setSocketTimeout(HttpClientTimeoutProperties.getInstance().getReadTimeout() * 1000)
                                .setConnectTimeout(HttpClientTimeoutProperties.getInstance().getConnectTimeout() * 1000)
                                .build())
                        .build())
                .withRequestBuilder(new JsonRequestBuilder(GSON_REQUEST)
                        .withCommonParameters(new CommonParameters().withLang("ru"))
                        .setHeaders(new CommonHeaders()
                                .withOAuthToken(builder.user.get(OAUTH_TOKEN))
                                .withServiceTicket(TvmClient.getInstance().getServiceTicket(TvmClient.AUDIENCE_PUBAPI_TVMID))
                                .withUserTicket(BlackboxClient.getInstance().oAuth(builder.user.get(OAUTH_TOKEN)).getTvmUserTicket().get())
                                .getParameters()
                                .stream()
                                .map(p -> new BasicHeader(p.getName(), p.getValue()))
                                .toArray(Header[]::new)))
                .withResponseParser(new JsonResponseParser(GSON_RESPONSE))
                .withLogger(new HttpClientLiteLogger())
                .build();

        segmentsSteps = new SegmentsSteps(baseUrl, client);
        pixelsSteps = new PixelsSteps(baseUrl, client);
        segmentGrantsSteps = new SegmentGrantsSteps(baseUrl, client);
        delegatesSteps = new DelegatesSteps(baseUrl, client);
        accountsSteps = new AccountsSteps(baseUrl, client);
        experimentSteps = new ExperimentSteps(baseUrl, client);
        experimentGrantsSteps= new ExperimentGrantsSteps(baseUrl, client);
    }

    public SegmentsSteps onSegmentsSteps() {
        return segmentsSteps;
    }

    public PixelsSteps onPixelsSteps() {
        return pixelsSteps;
    }

    public SegmentGrantsSteps onGrantsSteps() {
        return segmentGrantsSteps;
    }

    public DelegatesSteps onDelegatesSteps() {
        return delegatesSteps;
    }

    public AccountsSteps onAccountsSteps() {
        return accountsSteps;
    }

    public ExperimentSteps onExperimentSteps() {
        return experimentSteps;
    }

    public ExperimentGrantsSteps onExperimentGrantsSteps() {
        return experimentGrantsSteps;
    }

    public static UserSteps withDefaultUser() {
        return withUser(Users.SIMPLE_USER);
    }

    public static UserSteps withUser(User user) {
        return new Builder()
                .withUser(user)
                .withBaseUrl(AudienceApiProperties.getInstance().getApiUrl())
                .build();
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
