package ru.yandex.taxi.ququmber;

import java.util.concurrent.CompletableFuture;

import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Bean;
import org.springframework.retry.annotation.EnableRetry;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.consumer.BatchingStreamConsumer;
import ru.yandex.market.checkout.checkouter.client.CheckouterAPI;
import ru.yandex.passport.tvmauth.TvmClient;
import ru.yandex.startrek.client.auth.AuthenticationInterceptor;
import ru.yandex.taxi.ququmber.clients.saas.SaasIndexingClient;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@org.springframework.boot.test.context.TestConfiguration
@EnableRetry
public class TestConfiguration {

    @MockBean
    private TvmClient tvmClient;

    @Bean
    public LogbrokerClientAsyncFactory mockLogbrokerClientAsyncFactory() {
        LogbrokerClientAsyncFactory factory = mock(LogbrokerClientAsyncFactory.class);
        BatchingStreamConsumer batchingStreamConsumer = mock(BatchingStreamConsumer.class);
        when(factory.batchingStreamConsumer(any())).thenReturn(CompletableFuture.completedFuture(batchingStreamConsumer));
        return factory;
    }

    @MockBean
    private CheckouterAPI checkouterAPI;

    @MockBean
    private AuthenticationInterceptor startrackAuthenticationInterceptor;

    @Bean
    SaasIndexingClient saasIndexingClient() {
        return mock(SaasIndexingClient.class);
    };
}
