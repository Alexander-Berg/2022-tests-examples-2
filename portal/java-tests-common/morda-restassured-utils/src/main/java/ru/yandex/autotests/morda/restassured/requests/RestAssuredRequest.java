package ru.yandex.autotests.morda.restassured.requests;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.module.jaxb.JaxbAnnotationModule;
import com.jayway.restassured.config.RestAssuredConfig;
import com.jayway.restassured.specification.RequestSpecification;
import ru.yandex.autotests.morda.restassured.filters.AllureRestAssuredRequestFilter;
import ru.yandex.autotests.morda.restassured.filters.AllureRestAssuredResponseFilter;
import ru.yandex.autotests.morda.restassured.filters.RestAssuredLoggingFilter;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

import static com.jayway.restassured.RestAssured.given;
import static com.jayway.restassured.config.ObjectMapperConfig.objectMapperConfig;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/03/16
 */
public abstract class RestAssuredRequest<T extends RestAssuredRequest<T>> implements Request<T> {
    protected String stepName;
    protected UriBuilder uri;
    protected Map<String, String> queryParams = new HashMap<>();
    protected Map<String, Supplier<?>> queryParamsProviders = new HashMap<>();
    protected List<RequestAction> beforeRequestActions = new ArrayList<>();
    protected List<RequestAction> afterRequestActions = new ArrayList<>();

    public RestAssuredRequest(String host) {
        this(URI.create(host));
    }

    public RestAssuredRequest(URI host) {
        this.uri = UriBuilder.fromUri(host);
        String query = host.getQuery();
        if (query != null && !query.isEmpty()) {
            Arrays.stream(host.getQuery().split("&"))
                    .filter(e -> e != null)
                    .forEach(e -> {
                        String[] value = e.split("=", 2);
                        if (value.length != 2) {
                            return;
                        }
                        queryParams.put(value[0], value[1]);
                    });
        }
    }

    @Override
    public T path(String path) {
        this.uri.path(path);
        return me();
    }

    @Override
    public T queryParam(String name, Object value) {
        this.queryParams.put(name, String.valueOf(value));
        return me();
    }

    public T queryParam(String name, Supplier<?> provider) {
        this.queryParamsProviders.put(name, provider);
        return me();
    }

    @Override
    public String getQueryParam(String name) {
        return queryParams.get(name);
    }

    private Map<String, String> buildQueryParams() {
        queryParamsProviders.forEach((k, v) -> queryParams.put(k, String.valueOf(v.get())));
        return queryParams;
    }

    @Override
    public RequestSpecification createRequestSpecification() {
        try {
            buildQueryParams();
            return given()
                    .config(getConfig())
                    .accept("application/json; charset=UTF-8")
                    .contentType("application/json")
                    .filter(new AllureRestAssuredRequestFilter())
                    .filter(new AllureRestAssuredResponseFilter())
                    .filter(new RestAssuredLoggingFilter())
                    .baseUri(uri.build().toString())
                    .queryParams(queryParams);
        } catch (Exception e) {
            throw new RuntimeException("Failed to create request", e);
        }
    }

    @Override
    public T afterRequest(List<RequestAction<T>> actions) {
        actions.forEach(a -> a.setRequest(me()));
        afterRequestActions.addAll(actions);
        return me();
    }

    @Override
    public T beforeRequest(List<RequestAction<T>> actions) {
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
    public T step(String stepName) {
        this.stepName = stepName;
        return me();
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
        return new RestAssuredConfig().objectMapperConfig(
                objectMapperConfig().jackson2ObjectMapperFactory(
                        (cls, charset) -> {
                            ObjectMapper objectMapper = new ObjectMapper();
                            objectMapper.registerModule(new JaxbAnnotationModule());
                            objectMapper.enable(JsonParser.Feature.ALLOW_UNQUOTED_CONTROL_CHARS);
                            objectMapper.enable(JsonParser.Feature.ALLOW_BACKSLASH_ESCAPING_ANY_CHARACTER);
                            objectMapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
                            objectMapper.enable(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY);
                            return objectMapper;
                        }
                )
        );
    }
}
