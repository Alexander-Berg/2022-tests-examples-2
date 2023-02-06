package ru.yandex.autotests.morda.restassured.requests;

import java.net.InetAddress;
import java.net.URI;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

import javax.ws.rs.core.MultivaluedHashMap;
import javax.ws.rs.core.MultivaluedMap;
import javax.ws.rs.core.UriBuilder;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.MapperFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.module.jaxb.JaxbAnnotationModule;
import com.jayway.restassured.config.HttpClientConfig;
import com.jayway.restassured.config.RedirectConfig;
import com.jayway.restassured.config.RestAssuredConfig;
import com.jayway.restassured.config.SSLConfig;
import com.jayway.restassured.http.ContentType;
import com.jayway.restassured.specification.RequestSpecification;
import org.apache.http.client.HttpClient;
import org.apache.http.conn.DnsResolver;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.impl.conn.PoolingClientConnectionManager;
import org.apache.http.impl.conn.SchemeRegistryFactory;
import org.apache.http.impl.conn.SystemDefaultDnsResolver;
import org.apache.log4j.Logger;

import ru.yandex.autotests.morda.RestAssuredProperties;
import ru.yandex.autotests.morda.restassured.filters.AllureRestAssuredRequestFilter;
import ru.yandex.autotests.morda.restassured.filters.RestAssuredCookieStorageFilter;
import ru.yandex.autotests.morda.restassured.filters.RestAssuredLoggingFilter;

import static com.jayway.restassured.RestAssured.given;
import static com.jayway.restassured.config.ObjectMapperConfig.objectMapperConfig;
import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/03/16
 */
public abstract class RestAssuredRequest<REQ extends RestAssuredRequest<REQ>>
        implements Request<REQ> {
    private static final RestAssuredProperties CONFIG = new RestAssuredProperties();
    protected final Logger LOGGER = Logger.getLogger(this.getClass());
    protected RestAssuredCookieStorageFilter cookieStorage;
    protected String accept = ContentType.ANY.toString();
    protected String contentType = ContentType.ANY.toString();
    protected Map<String, String> cookies = new HashMap<>();
    protected Map<String, String> headers = new HashMap<>();
    protected MultivaluedMap<String, String> queryParams = new MultivaluedHashMap<>();
    protected Map<String, Supplier<?>> queryParamsProviders = new HashMap<>();
    protected List<RequestAction> beforeRequestActions = new ArrayList<>();
    protected List<RequestAction> afterRequestActions = new ArrayList<>();
    protected SimpleModule deserializers = new SimpleModule();
    protected boolean silent = false;
    protected String stepName;
    protected UriBuilder uri;
    protected boolean followRedirects = true;
    protected boolean urlEncodingEnabled = true;

    public RestAssuredRequest(String host) {
        this(URI.create(host));
    }

    public RestAssuredRequest(URI host) {
        this.uri = UriBuilder.fromUri(host);
        String query = host.getRawQuery();
        if (query != null && !query.isEmpty()) {
            Arrays.stream(host.getRawQuery().split("&"))
                    .filter(e -> e != null)
                    .forEach(e -> {
                        String[] value = e.split("=", 2);
                        if (value.length != 2) {
                            return;
                        }
                        queryParams.add(value[0], value[1]);
                    });
        }
//        queryParamsProviders.put("t_from_morda", () -> RandomStringUtils.random(30, true, false));
    }

    @Override
    public REQ followRedirects(boolean follow) {
        this.followRedirects = follow;
        return me();
    }

    @Override
    public REQ path(String path) {
        this.uri.path(path);
        return me();
    }

    @Override
    public REQ urlEncoding(boolean urlEncoding) {
        this.urlEncodingEnabled = urlEncoding;
        return me();
    }

    @Override
    public REQ queryParam(String name, Object value) {
        queryParams.add(name, String.valueOf(value));
        return me();
    }

    public REQ queryParam(String name, Supplier<?> provider) {
        this.queryParamsProviders.put(name, provider);
        return me();
    }

    @Override
    public REQ cookie(String name, String value) {
        this.cookies.put(name, value);
        return me();
    }

    @Override
    public REQ header(String name, String value) {
        this.headers.put(name, value);
        return me();
    }

    @Override
    public REQ accept(String contentType) {
        this.accept = contentType;
        return me();
    }

    @Override
    public REQ contentType(String contentType) {
        this.contentType = contentType;
        return me();
    }

    public <K> REQ addDeserializer(Class<K> clazz, JsonDeserializer<? extends K> deserializer) {
        deserializers.addDeserializer(clazz, deserializer);
        return me();
    }

    @Override
    public List<String> getQueryParam(String name) {
        return queryParams.getOrDefault(name, new ArrayList<>());
    }

    @Override
    public void removeQueryParam(String param) {
        queryParams.remove(param);
        queryParamsProviders.remove(param);
    }

    private MultivaluedMap<String, String> buildQueryParams() {
        queryParamsProviders
                .forEach((k, v) -> queryParams.add(k, String.valueOf(v.get())));
        return queryParams;
    }

    public REQ cookieStorage(RestAssuredCookieStorageFilter cookieStorage) {
        this.cookieStorage = cookieStorage;
        return me();
    }

    @Override
    public RequestSpecification createRequestSpecification() {
        try {
            buildQueryParams();
            RequestSpecification request = given()
                    .config(getConfig())
                    .accept(accept)
                    .contentType(contentType);
            if (cookieStorage != null) {
                request.filter(cookieStorage);
            }
            request.filter(new AllureRestAssuredRequestFilter(silent))
                    .filter(new RestAssuredLoggingFilter(silent))
                    .baseUri(uri.build().toString())
//                    .queryParams(queryParams)
                    .headers(headers)
                    .urlEncodingEnabled(urlEncodingEnabled)
                    .cookies(cookies);

            queryParams.forEach((name, values) ->
                    values.forEach(value ->
                            request.queryParam(name, value)));

            return request;
        } catch (Exception e) {
            throw new RuntimeException("Failed to create request", e);
        }
    }

    @Override
    public REQ afterRequest(List<RequestAction<REQ>> actions) {
        actions.forEach(a -> a.setRequest(me()));
        afterRequestActions.addAll(actions);
        return me();
    }

    @Override
    public REQ beforeRequest(List<RequestAction<REQ>> actions) {
        actions.forEach(a -> a.setRequest(me()));
        beforeRequestActions.addAll(actions);
        return me();
    }

    @Override
    public List<RequestAction> getAfterRequestActions() {
        return afterRequestActions;
    }

    @Override
    public String getStepName() {
        return stepName;
    }

    @Override
    public REQ step(String stepName) {
        this.stepName = stepName;
        return me();
    }

    @Override
    public REQ silent() {
        silent = true;
        return me();
    }

    @Override
    public boolean isSilent() {
        return silent;
    }

    @Override
    public List<RequestAction> getBeforeRequestActions() {
        return beforeRequestActions;
    }

    @Override
    public URI getUri() {
        return uri.build();
    }

    protected RestAssuredConfig getConfig() {
        HttpClientConfig httpClientConfig = new HttpClientConfig();
        HttpClientConfig.HttpClientFactory factory = new HttpClientConfig.HttpClientFactory() {
            @Override
            public HttpClient createHttpClient() {
                DnsResolver dnsResolver = new SystemDefaultDnsResolver() {
                    @Override
                    public InetAddress[] resolve(final String host) throws UnknownHostException {
                        // load.wfront.yandex.net

                        List<String> ua = asList("yandex.ua", "www.yandex.ua", "tel.yandex.ua", "m.yandex.ua");
                        if (ua.contains(host)) {
                            LOGGER.info("Overriding dns for host " + host + " to 5.255.255.5");
                            return InetAddress.getAllByName("5.255.255.5");
                        } else if (CONFIG.getDnsOverride().equals("load")
                                && host.matches("((hw|firefox|www)\\.)?(ya|yandex)\\.(ru|ua|com\\.tr|com)")) {
                            LOGGER.info("Overriding dns for host " + host + " to 130.193.43.220");
                            return InetAddress.getAllByName("130.193.43.220");
                        } else {
                            return super.resolve(host);
                        }
                    }
                };
                HttpClient client = new DefaultHttpClient(new PoolingClientConnectionManager(SchemeRegistryFactory.createSystemDefault(), dnsResolver));
                return client;
            }
        };
        httpClientConfig = httpClientConfig.httpClientFactory(factory);
        return new RestAssuredConfig().objectMapperConfig(
                objectMapperConfig().jackson2ObjectMapperFactory(
                        (cls, charset) -> {
                            ObjectMapper objectMapper = new ObjectMapper();
                            objectMapper.registerModule(new JaxbAnnotationModule());
                            objectMapper.registerModule(deserializers);
                            objectMapper.enable(JsonParser.Feature.ALLOW_UNQUOTED_CONTROL_CHARS);
                            objectMapper.enable(JsonParser.Feature.ALLOW_BACKSLASH_ESCAPING_ANY_CHARACTER);
                            objectMapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
                            objectMapper.enable(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES);
                            objectMapper.enable(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY);
                            objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
                            return objectMapper;
                        }
                ))
                .sslConfig(new SSLConfig().allowAllHostnames())
                .httpClient(httpClientConfig)
                .redirect(new RedirectConfig().followRedirects(followRedirects))

                ;
    }

    public RestAssuredCookieStorageFilter getCookieStorage() {
        return cookieStorage;
    }
}
