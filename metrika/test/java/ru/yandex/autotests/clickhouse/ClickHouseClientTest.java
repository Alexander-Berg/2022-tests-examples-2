package ru.yandex.autotests.clickhouse;

import com.github.tomakehurst.wiremock.core.Options;
import com.github.tomakehurst.wiremock.junit.WireMockRule;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import ru.yandex.autotests.clickhouse.client.ClickHouseClient;
import ru.yandex.autotests.clickhouse.client.QueryResult;

import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static java.lang.String.format;
import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static java.util.Collections.singletonMap;
import static java.util.stream.Collectors.toList;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;

/**
 * Created by konkov on 01.02.2016.
 */
public class ClickHouseClientTest {

    private static final Gson GSON = new GsonBuilder().create();

    @Rule
    public WireMockRule wireMockRule = new WireMockRule(Options.DYNAMIC_PORT);

    @Before
    public void setup() {

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^SHOW TABLES.*$"))
                .willReturn(aResponse()
                        .withStatus(200)
                        .withBody(GSON.toJson(getQueryResultForSystemTables()))));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^SHOW CREATE TABLE.*$"))
                .willReturn(aResponse()
                        .withStatus(200)
                        .withBody(GSON.toJson(getQueryResultForCreateTable()))));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^SELECT sipHash64.*$"))
                .atPriority(0)
                .willReturn(aResponse()
                        .withStatus(200)
                        .withBody(GSON.toJson(getQueryResultForSipHash64()))));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^SELECT.*$"))
                .atPriority(1)
                .willReturn(aResponse()
                        .withStatus(200)
                        .withBody(getExpectedBeansAsBytes())));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^CREATE TABLE.*$"))
                .willReturn(aResponse()
                        .withStatus(200)));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^CREATE DATABASE.*$"))
                .willReturn(aResponse()
                        .withStatus(200)));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^DROP DATABASE.*$"))
                .willReturn(aResponse()
                        .withStatus(200)));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^DROP TABLE.*$"))
                .willReturn(aResponse()
                        .withStatus(200)));

        stubFor(post(urlPathEqualTo("/"))
                .withRequestBody(matching("^INSERT.*$"))
                .willReturn(aResponse()
                        .withStatus(200)));
    }

    @Test
    public void createDatabase() {
        getClient().createDatabase("database_001");

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void createTable() {
        getClient().createTable(TestBean.class, "database_TestBean", "table_TestBean");

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void createTableWithEngine() {
        getClient().createTable(TestBean.class, "database_TestBean", "table_TestBean", "Memory");

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void dropDatabase() {
        getClient().dropDatabase("database_TestBean");

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void dropTable() {
        getClient().dropTable("database_TestBean", "table_TestBean");

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void truncateTable() {
        getClient().truncateTable("database_01", "table_001");

        verify(3, postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void getSipHash64() {
        String sipHash64 = getClient().getSipHash64("xyz");

        assertThat(sipHash64, Matchers.equalTo("1111"));

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void insert() {
        getClient().insert(getExpectedBeans(), TestBean.class, "database_01", "table_001");

        verify(postRequestedFor(urlPathEqualTo("/")).withRequestBody(containing(new String(getExpectedBeansAsBytes()))));
    }

    @Test
    public void select() {
        List<TestBean> select = getClient().select(TestBean.class, "database_01", "table_001");

        assertThat(select, beanEquivalent(getExpectedBeans()));

        verify(postRequestedFor(urlPathEqualTo("/")));
    }

    @Test
    public void listTables() {
        List<String> system = getClient().listTables("system");

        assertThat(system, Matchers.equalTo(getSystemTables()));
    }

    private static List<String> getSystemTables() {
        return asList("one", "numbers", "tables");
    }

    private static QueryResult getQueryResultForSystemTables() {
        return new QueryResult()
                .withMeta(singletonList(getMeta("name", "String")))
                .withData(getSystemTables()
                        .stream()
                        .map(name -> singletonMap("name", (Object) name))
                        .collect(toList()))
                .withRows((long) getSystemTables().size());
    }

    private static QueryResult getQueryResultForSipHash64() {
        return new QueryResult()
                .withMeta(singletonList(getMeta("hash", "UInt64")))
                .withData(singletonList(singletonMap("hash", "1111")))
                .withRows(1L);
    }

    private static QueryResult getQueryResultForCreateTable() {
        return new QueryResult()
                .withMeta(singletonList(getMeta("statement", "String")))
                .withData(singletonList(singletonMap("statement", "CREATE TABLE table_001 (Serial UInt8) ENGINE = Log")))
                .withRows(1L);
    }

    private static List<TestBean> getExpectedBeans() {
        return singletonList(getTestBean());

    }

    private static TestBean getTestBean() {
        return new TestBean()
                .withEventID(1L)
                .withURL("http://www.ya.ru")
                .withParsedParams_Key1(new String[]{"test_1", "test_2"})
                .withParsedParams_Key2(new Long[]{1L, 2L});
    }

    private static byte[] getExpectedBeansAsBytes() {
        return "1\thttp://www.ya.ru\t['test_1','test_2']\t[1,2]\n".getBytes(StandardCharsets.UTF_8);
    }

    private String getClickHouseEndpoint() {
        return format("http://localhost:%d/", wireMockRule.port());
    }

    private ClickHouseClient getClient() {
        return new ClickHouseClient(getClickHouseEndpoint());
    }

    private static Map<String, String> getMeta(String name, String type) {
        Map<String, String> meta = new HashMap<>();
        meta.put("name", name);
        meta.put("type", type);
        return meta;
    }

}
