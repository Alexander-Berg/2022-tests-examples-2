package ru.yandex.metrika.util;

import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import org.apache.http.HttpHost;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.conn.routing.HttpRoute;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.apache.http.util.EntityUtils;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.mockserver.integration.ClientAndServer;
import org.mockserver.model.HttpRequest;
import org.mockserver.model.HttpResponse;
import org.springframework.util.SocketUtils;

import ru.yandex.metrika.util.collections.Try;
import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static org.mockserver.integration.ClientAndServer.startClientAndServer;

public class HttpClientUtilsTest {


    private static ClientAndServer clientAndServer;
    private static int port;

    private static final HttpResponse fail = HttpResponse.response().withStatusCode(500).withBody("\"fail\"");
    private static final HttpResponse success = HttpResponse.response().withStatusCode(200).withBody("\"success\"");

    @BeforeClass
    public static void beforeClass() throws Exception {
        port = SocketUtils.findAvailableTcpPort();
        clientAndServer = startClientAndServer(port);
    }

    @Test
    public void testReleaseConnectionAfterFailureOnGet() {

        CloseableHttpClient httpClient = buildClientWithSmallPool();

        var path = "/test";
        var request = HttpRequest.request().withMethod("GET").withPath(path);

        clientAndServer.when(request).respond(fail);
        var aTry = tryGet(httpClient, path);
        Assert.assertTrue(aTry.isFailure());

        clientAndServer.clear(request).when(request).respond(success);
        var aTry2 = tryGet(httpClient, path);
        Assert.assertTrue(aTry2.isSuccess());
        Assert.assertEquals("success", aTry2.get());
    }

    @Test
    public void testReleaseConnectionAfterFailureOnPost() {

        CloseableHttpClient httpClient = buildClientWithSmallPool();

        var path = "/test";
        var request = HttpRequest.request().withMethod("POST").withPath(path);

        clientAndServer.when(request).respond(fail);
        var aTry = tryPost(httpClient, path);
        Assert.assertTrue(aTry.isFailure());

        clientAndServer.clear(request).when(request).respond(success);
        var aTry2 = tryPost(httpClient, path);
        aTry2.consumeErr(e -> Assert.fail(e.getMessage()));
        Assert.assertEquals("success", aTry2.get());
    }

    private CloseableHttpClient buildClientWithSmallPool() {
        // создаём httpClient с пулом размера 1
        var poolingHttpClientConnectionManager = new PoolingHttpClientConnectionManager();
        poolingHttpClientConnectionManager.setMaxPerRoute(new HttpRoute(new HttpHost("localhost", port)), 1);
        RequestConfig config = RequestConfig.custom().setConnectTimeout(3_000).setConnectionRequestTimeout(3_000).build();
        return HttpClientBuilder.create().setConnectionManager(poolingHttpClientConnectionManager).setDefaultRequestConfig(config).build();
    }

    private Try<String> tryGet(CloseableHttpClient httpClient, String path) {
        return Try.of(() -> HttpClientUtils.getJsonFromUrl(httpClient, "http://localhost:" + port + path, new TypeReference<>() {}, Map.of()));
    }

    private Try<String> tryPost(CloseableHttpClient httpClient, String path) {
        return Try.of(() -> HttpClientUtils.httpPost(httpClient, "http://localhost:" + port + path, new StringEntity(""), "", Map.of(), 200))
                .flatMap(e -> Try.of(() -> EntityUtils.toString(e)))
                .flatMap(s -> Try.of(() -> ObjectMappersFactory.getDefaultMapper().readValue(s, new TypeReference<>() {})));
    }

    @After
    public void tearDown() throws Exception {
        clientAndServer.reset();
    }

    @AfterClass
    public static void afterClass() {
        clientAndServer.stop();
    }
}
