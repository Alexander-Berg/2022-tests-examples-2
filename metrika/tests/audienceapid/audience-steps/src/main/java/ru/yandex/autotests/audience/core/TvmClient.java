package ru.yandex.autotests.audience.core;

import com.google.common.base.Preconditions;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import org.apache.http.HttpRequestInterceptor;
import org.apache.http.impl.client.HttpClientBuilder;
import org.joda.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import ru.yandex.autotests.audience.properties.VaultProperties;
import ru.yandex.autotests.metrika.commons.vault.VaultClient;
import ru.yandex.inside.passport.tvm2.Tvm2;
import ru.yandex.inside.passport.tvm2.Tvm2ApiClient;
import ru.yandex.inside.passport.tvm2.TvmClientCredentials;
import ru.yandex.library.ticket_parser2.BlackboxEnv;
import ru.yandex.library.ticket_parser2.ServiceTicket;
import ru.yandex.library.ticket_parser2.Status;
import ru.yandex.library.ticket_parser2.UserTicket;

import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Supplier;

import static ru.yandex.autotests.audience.core.BlackboxClient.BLACKBOX_MIMINO_SERVICE_ID;
import static ru.yandex.autotests.audience.core.BlackboxClient.BLACKBOX_SERVICE_ID;

/**
 * Created by orantius on 06.07.17.
 */
public class TvmClient {

    // https://abc.yandex-team.ru/services/conv/resources/?search=tests&state=requested&state=approved&state=granted&view=consuming
    public static final int METRIKA_PUBAPI_TESTS_TVMID = 2011678;
    // https://abc.yandex-team.ru/services/audience/resources/?supplier=14&type=47&type=50&state=requested&state=approved&state=granted&view=consuming

    public static final int AUDIENCE_PUBAPI_TESTS_TVMID = 2011686;
    // ключ с tvm-секретом в секрете аудиторных тестов
    public static final String SECRET = "AUDIENCE_INTAPI_TS_TVM_SECRET"; //"AUDIENCE_PUBAPI_TVM_SECRET";

    public static final int AUDIENCE_PUBAPI_TVMID = 2000307;
    public static final int AUDIENCE_INTAPI_TVMID = 2000305;
    public static final int METRIKA_PUBAPI_TVM_ID = 2000233;
    public static final int METRIKA_INTAPI_TVMID = 2000269;

    public static final String SERVICE_HEADER = "X-Ya-Service-Ticket";
    public static final String USER_HEADER = "X-Ya-User-Ticket";


    private static final Map<String, String> SECRET_CONTENT = VaultClient.loadLastVersion(VaultProperties.getInstance().getUsersSecretId());
    private static final Logger log = LoggerFactory.getLogger(TvmClient.class);

    private static final Gson GSON = new GsonBuilder().create();
    private static final String TVM_SECRET_KEY = "tvm_secret";
    private static final String TVM_SERVICE_ID_KEY = "tvm_service_id";
    private static TvmClient instance;

    private String apiRoot = "https://tvm-api.yandex.net";

    public static TvmClient getInstance() {
        if (instance == null) {
            instance = new TvmClient();
        }
        return instance;
    }

    private Tvm2 tvm2;

    private volatile List<Integer> clientIds;

    public TvmClient() {
        Map<String, String> content = GSON.fromJson(SECRET_CONTENT.get(SECRET), new TypeToken<Map<String, String>>(){}.getType());
        final TvmClientCredentials credentials = new TvmClientCredentials(Integer.valueOf(content.get(TVM_SERVICE_ID_KEY)), content.get(TVM_SECRET_KEY));
        final Tvm2ApiClient apiClient = new Tvm2ApiClient(apiRoot);
        tvm2 = new Tvm2(apiClient, credentials, Duration.standardHours(1), Duration.standardSeconds(1));
        clientIds = Arrays.asList(
                AUDIENCE_PUBAPI_TVMID,
                AUDIENCE_PUBAPI_TESTS_TVMID,
                BLACKBOX_SERVICE_ID,
                BLACKBOX_MIMINO_SERVICE_ID
        );

        tvm2.setDstClientIds(clientIds);
        tvm2.setBlackboxEnv(BlackboxEnv.Prod);
        log.info(new Date() + " before start");
        tvm2.start();
        // await init
        log.info(new Date() + " after start");
        tvm2.getServiceContext();
        log.info(new Date() + " after getServiceContext");
    }

    public void finalize() {
        tvm2.stop();
    }

    /**
     * добавляем к http клиенту отправку tvm-тикетов с клиентской стороны.
     *
     * @param dst id сервиса-сервера, который будет аутентифицировать запросы
     */
    public Consumer<HttpClientBuilder> serviceTicketHttpClientConsumerChecked(Supplier<Integer> dst) {
        final HttpRequestInterceptor interceptor = serviceTicketInterceptorChecked(dst);
        return builder -> builder.addInterceptorFirst(interceptor);
    }

    public HttpRequestInterceptor serviceTicketInterceptorChecked(Supplier<Integer> dst) {
        Preconditions.checkNotNull(dst.get(), "tvm client id should be not null");
        return (request, context) -> {
            if (!tvm2.isInitialized()) {
                log.warn("TVM is not initialized. Working without TVM");
                return;
            }
            final int clientId = dst.get();
            final String serviceTicket = tvm2.getServiceTicket(clientId).getOrThrow("Missing service ticket for clientId=" + clientId);
            request.addHeader(SERVICE_HEADER, serviceTicket);
        };
    }

    public String getSelfServiceTicket() {
        return tvm2.getServiceTicket(AUDIENCE_PUBAPI_TESTS_TVMID).getOrThrow("no ticket");
    }

    public String getServiceTicket(int clientId) {
        return tvm2.getServiceTicket(clientId).getOrThrow("no ticket");
    }

    public String getUserTicket(int clientId) {
        return tvm2.getServiceTicket(clientId).getOrThrow("no ticket");
    }

    public String checkUserTicket2(String tvmToken) {
        return checkUserTicket(tvmToken).debugInfo();
    }

    public String checkServiceTicket2(String tvmToken) {
        return checkServiceTicket(tvmToken).debugInfo();
    }

    public UserTicket checkUserTicket(String tvmToken) {
        final UserTicket userTicket = tvm2.checkUserTicket(tvmToken);
        if (userTicket.getStatus() != Status.Ok) {
            log.warn("invalid user token: {}", userTicket.getStatus());
            throw new IllegalArgumentException("bad user token: " + userTicket.getStatus());
        }
        return userTicket;
    }

    public ServiceTicket checkServiceTicket(String tvmToken) {
        final ServiceTicket serviceTicket = tvm2.checkServiceTicket(tvmToken);
        if (serviceTicket.getStatus() != Status.Ok) {
            log.warn("invalid service token: {}", serviceTicket.getStatus());
            throw new IllegalArgumentException("bad service token: " + serviceTicket.getStatus());
        }
        return serviceTicket;
    }

}
