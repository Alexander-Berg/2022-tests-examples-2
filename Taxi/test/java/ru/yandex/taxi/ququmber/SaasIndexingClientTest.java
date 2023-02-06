package ru.yandex.taxi.ququmber;

import java.io.IOException;
import java.util.concurrent.atomic.AtomicInteger;

import okhttp3.Call;
import okhttp3.OkHttpClient;
import okhttp3.Protocol;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.internal.http.RealResponseBody;
import okio.Buffer;
import org.json.JSONObject;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Bean;
import org.springframework.retry.RetryListener;

import ru.yandex.market.javaframework.main.config.SpringApplicationConfig;
import ru.yandex.taxi.ququmber.clients.saas.SaasIndexingClient;
import ru.yandex.taxi.ququmber.search.OrderIndex;
import ru.yandex.taxi.ququmber.search.OrderToSaasRequestConverter;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@SpringBootTest(
        classes = {SpringApplicationConfig.class, TestConfiguration.class, SaasIndexingClientTest.Config.class}
)
public class SaasIndexingClientTest {

    @org.springframework.boot.test.context.TestConfiguration
    public static class Config {
        @Bean
        @Qualifier("saasOkHttpClient")
        OkHttpClient saasOkHttpClient() {
            OkHttpClient client = mock(OkHttpClient.class);
            return client;
        }

        @Bean
        SaasIndexingClient saasIndexingClient(@Qualifier("saasOkHttpClient") OkHttpClient client, OrderToSaasRequestConverter orderToSaasRequestConverter) {
            return new SaasIndexingClient("http://example.com", client, orderToSaasRequestConverter);
        }
    }

    @Autowired
    @Qualifier("saasOkHttpClient")
    OkHttpClient client;

    @Autowired
    SaasIndexingClient saasIndexingClient;

    @MockBean
    RetryListener retryListener;

    @Test
    public void testRetry() throws IOException {
        when(retryListener.open(any(), any())).thenReturn(true);
        AtomicInteger calledOnError = new AtomicInteger();
        doAnswer(inv -> calledOnError.incrementAndGet()).when(retryListener).onError(any(), any(), any());

        Call call = mock(Call.class);
        when(client.newCall(any())).thenReturn(call);

        when(call.execute())
                .thenThrow(new IOException(""))
                .thenReturn(fakeResponse(200));

        OrderIndex orderIndex = new OrderIndex();
        orderIndex.updateTimestampSeconds = 1;
        saasIndexingClient.sendToIndexing(orderIndex);

        Assertions.assertEquals(1, calledOnError.get());
    }

    @Test
    public void testNoRetryRequired() throws IOException {
        when(retryListener.open(any(), any())).thenReturn(true);

        Call call = mock(Call.class);
        when(client.newCall(any())).thenReturn(call);

        when(call.execute()).thenReturn(fakeResponse(400));

        try {
            OrderIndex orderIndex = new OrderIndex();
            orderIndex.updateTimestampSeconds = 1;
            saasIndexingClient.sendToIndexing(orderIndex);
            Assertions.fail();
        } catch (RuntimeException e) {
            Assertions.assertTrue(e.getMessage().startsWith("non recoverable"));
        }
    }

    private Response fakeResponse(int status) {
        Request request = new Request.Builder().url("http://example.com/").build();
        return new Response.Builder()
                .request(request)
                .protocol(Protocol.HTTP_1_1)
                .code(status)
                .message("")
                .body(new RealResponseBody("application/json", 0, new Buffer()))
                .build();
    }

}
