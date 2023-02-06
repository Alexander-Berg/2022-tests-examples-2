package ru.yandex.autotests.clickhouse;

import com.github.tomakehurst.wiremock.core.Options;
import com.github.tomakehurst.wiremock.junit.WireMockRule;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;

import ru.yandex.autotests.clickhouse.client.ClickHouseHttpClient;

import java.io.UnsupportedEncodingException;
import java.nio.charset.StandardCharsets;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static java.lang.String.format;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyString;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;

/**
 * Created by konkov on 01.02.2016.
 */
public class ClickHouseHttpClientTest {

    @Rule
    public WireMockRule wireMockRule = new WireMockRule(Options.DYNAMIC_PORT);

    @Before
    public void setup() {
        stubFor(post(urlPathEqualTo("/"))
                .willReturn(aResponse()
                        .withStatus(200)
                        .withBody("Ok.")));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^CREATE.*$"))
                .willReturn(aResponse()
                        .withStatus(200)));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^SELECT Serial FROM table_001$"))
                .willReturn(aResponse()
                        .withStatus(200)));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^INSERT.*$"))
                .willReturn(aResponse()
                        .withStatus(200)));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^SELECT Serial FROM table_002$"))
                .willReturn(aResponse()
                        .withStatus(500)
                        .withBody("Code: 473, e.displayText() = DB::Exception: Possible deadlock avoided. Client should retry. (version 19.16.9.37 (official build))")));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^SELECT Serial FROM table_003$"))
                .willReturn(aResponse()
                        .withStatus(500)
                        .withBody("Code: 440, e.displayText() = DB::Exception: The value -10 of LIMIT expression is not representable as UInt64 (version 20.1.5.26 (official build))")));

    }

    @Test
    public void ping() {
        getClient().ping();

        verify(postRequestedFor(urlEqualTo("/")));
    }

    @Test
    public void isPing() {
        assertTrue(getClient().isPing());

        verify(postRequestedFor(urlEqualTo("/")));
    }

    @Test
    public void executeRequest() {
        String query = "CREATE TABLE table_001 (Serial UInt8) ENGINE = Memory";

        String result = getClient().executeRequest(query);

        assertThat(result, isEmptyString());

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void executeRawRequest() {
        String query = "SELECT Serial FROM table_001";

        byte[] result = getClient().executeRawRequest(query);

        assertThat(result.length, equalTo(0));

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void executeWithRetry() {
        String query = "SELECT Serial FROM table_002";

        try {
            getClient().executeRawRequest(query);
        } catch (Exception e) {

        }

        verify(4, postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void executeWithoutRetry() {
        String query = "SELECT Serial FROM table_003";

        try {
            getClient().executeRawRequest(query);
        } catch (Exception e) {

        }

        verify(1, postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void executeRequestWithBody() throws UnsupportedEncodingException {
        String query = "INSERT INTO table_001 VALUES (1),(2),(3)";

        String result = getClient().executeRequest(query.getBytes(StandardCharsets.UTF_8));

        assertThat(result, isEmptyString());

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    private ClickHouseHttpClient getClient() {
        return new ClickHouseHttpClient(getClickHouseEndpoint());
    }

    private String getClickHouseEndpoint() {
        return format("http://localhost:%d/", wireMockRule.port());
    }

}
