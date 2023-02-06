package ru.yandex.autotests.morda.client.requests;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.Invocation;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.Cookie;
import javax.ws.rs.core.MultivaluedHashMap;
import javax.ws.rs.core.MultivaluedMap;
import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public abstract class RequestBuilder<C extends RequestBuilder<C>> {
    protected final Map<String, Object> queryParams;
    protected final Map<String, String> cookies;
    protected final MultivaluedMap<String, Object> headers;
    protected Client client;
    protected UriBuilder uriBuilder;

    public RequestBuilder(URI uri) {
        uriBuilder = UriBuilder.fromUri(uri);
        queryParams = new HashMap<>();
        cookies = new HashMap<>();
        headers = new MultivaluedHashMap<>();
    }

    protected abstract C me();

    protected abstract Invocation getInvocation();

    public abstract Request build();

    public String description() {
        StringBuilder builder = new StringBuilder();

        List<Map.Entry<String, String>> filteredCookies = cookies.entrySet().stream()
                .filter(e -> e.getValue() != null)
                .collect(Collectors.toList());

        if (!filteredCookies.isEmpty()) {
            builder.append("Cookies: ");
            filteredCookies.forEach(c ->
                            builder.append(c.getKey()).append("=").append(c.getValue()).append("; ")
            );
        }

        return builder.toString();
    }

    protected URI getURI() {
        UriBuilder uriBuilder = this.uriBuilder.clone();

        for (Map.Entry<String, Object> queryParam : queryParams.entrySet()) {
            uriBuilder = uriBuilder.queryParam(queryParam.getKey(), queryParam.getValue());
        }
        return uriBuilder.build();
    }

    public C client(Client client) {
        this.client = client;
        return me();
    }

    public C path(String path) {
        uriBuilder.path(path);
        return me();
    }

    public C queryParam(String name, Object value) {
        queryParams.put(name, value);
        return me();
    }

    public C cookie(String name, String value) {
        cookies.put(name, value);
        return me();
    }

    public C header(String name, String value) {
        headers.addAll(name, value);
        return me();
    }

    public Request build(Client client) {
        this.client = client;
        return build();
    }

    protected Invocation.Builder builder() {
        if (client == null) {
            throw new IllegalStateException("Client must not be null");
        }

        WebTarget webTarget = client.target(uriBuilder);

        Invocation.Builder builder = addQueryParams(webTarget).request();

        cookies.entrySet().stream()
                .filter(e -> e.getValue() != null)
                .forEach(e -> builder.cookie(new Cookie(e.getKey(), e.getValue(), "/", null)));

        headers.entrySet().forEach(e -> builder.header(e.getKey(), e.getValue()));

        return builder;
    }

    private WebTarget addQueryParams(WebTarget target) {
        for (Map.Entry<String, Object> queryParam : queryParams.entrySet()) {
            target = target.queryParam(queryParam.getKey(), queryParam.getValue());
        }
        return target;
    }

    public Map<String, String> getCookies() {
        return cookies;
    }

    public MultivaluedMap<String, Object> getHeaders() {
        return headers;
    }

    public Map<String, Object> getQueryParams() {
        return queryParams;
    }

    public UriBuilder getUriBuilder() {
        return uriBuilder;
    }
}
