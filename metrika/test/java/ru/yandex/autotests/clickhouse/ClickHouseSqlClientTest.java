package ru.yandex.autotests.clickhouse;

import com.github.tomakehurst.wiremock.core.Options;
import com.github.tomakehurst.wiremock.junit.WireMockRule;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.hamcrest.Matchers;
import org.hamcrest.core.IsEqual;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import ru.yandex.autotests.clickhouse.client.ClickHouseSqlClient;
import ru.yandex.autotests.clickhouse.client.QueryResult;

import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static java.lang.String.format;
import static java.util.Collections.singletonList;
import static java.util.Collections.singletonMap;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;

/**
 * Created by konkov on 01.02.2016.
 */
public class ClickHouseSqlClientTest {

    private static final Gson GSON = new GsonBuilder().create();

    @Rule
    public WireMockRule wireMockRule = new WireMockRule(Options.DYNAMIC_PORT);

    @Before
    public void setup() {
        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(equalTo("SELECT 1 FORMAT JSON"))
                .atPriority(0)
                .willReturn(aResponse()
                        .withStatus(200)
                        .withBody(GSON.toJson(new QueryResult()
                                .withMeta(singletonList(getMeta("1", "UInt8")))
                                .withData(singletonList(singletonMap("1", 1)))
                                .withRows(1L)))));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^CREATE.*$"))
                .willReturn(aResponse()
                        .withStatus(200)));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^SELECT.*JSON$"))
                .atPriority(1)
                .willReturn(aResponse()
                        .withStatus(200)
                        .withBody(GSON.toJson(getQueryResultForSystemOne()))));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^SELECT.*TabSeparated$"))
                .willReturn(aResponse()
                        .withStatus(200)
                        .withBody(getRawQueryResultForSystemOne())));
    }

    @Test
    public void ping() {
        getClient().ping();

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void isPing() {
        assertTrue(getClient().isPing());

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void executeNonQuery() {
        String query = "CREATE TABLE table_001 (Serial UInt8) ENGINE = Memory";

        getClient().executeNonQuery(query);

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void executeMultiQuery() {
        String queries = "CREATE TABLE table_001 (Serial UInt8) ENGINE = Memory;" +
                "CREATE TABLE table_002 (Serial UInt8) ENGINE = Memory;";

        getClient().executeMultiQuery(queries);

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void executeScalar() {
        String query = "SELECT dummy FROM system.one";

        Object result = getClient().executeScalar(query);

        assertThat(result, Matchers.equalTo(0d));

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void executeQuery() {
        String query = "SELECT dummy FROM system.one";

        QueryResult actualResult = getClient().executeQuery(query);

        assertThat(actualResult, beanEquivalent(getQueryResultForSystemOne()));

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void executeQueryRaw() {
        String query = "SELECT dummy FROM system.one";

        byte[] actualResult = getClient().executeQueryRaw(query);

        assertThat(actualResult, IsEqual.equalTo(getRawQueryResultForSystemOne()));

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    private String getClickHouseEndpoint() {
        return format("http://localhost:%d/", wireMockRule.port());
    }

    private ClickHouseSqlClient getClient() {
        return new ClickHouseSqlClient(getClickHouseEndpoint());
    }

    private static Map<String, String> getMeta(String name, String type) {
        Map<String, String> meta = new HashMap<>();
        meta.put("name", name);
        meta.put("type", type);
        return meta;
    }

    private static QueryResult getQueryResultForSystemOne() {
        return new QueryResult()
                .withMeta(singletonList(getMeta("dummy", "UInt8")))
                .withData(singletonList(singletonMap("dummy", 0d)))
                .withRows(1L);
    }

    private static byte[] getRawQueryResultForSystemOne() {
        return "0\n".getBytes(StandardCharsets.UTF_8);
    }

}
