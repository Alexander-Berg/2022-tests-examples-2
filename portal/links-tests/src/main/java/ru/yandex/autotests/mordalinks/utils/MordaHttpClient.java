package ru.yandex.autotests.mordalinks.utils;

import org.apache.http.HttpResponse;
import org.apache.http.client.CookieStore;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.client.methods.RequestBuilder;
import org.apache.http.client.protocol.HttpClientContext;
import org.apache.http.impl.client.BasicCookieStore;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.protocol.BasicHttpContext;
import org.apache.http.protocol.HttpContext;

import java.io.IOException;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27.05.14
 */
public class MordaHttpClient {
    private CookieStore cookieStore;
    private HttpClient httpClient;
    private HttpContext httpContext;

    public MordaHttpClient() {
        cookieStore = new BasicCookieStore();
        httpContext = new BasicHttpContext();
        httpContext.setAttribute(HttpClientContext.COOKIE_STORE, cookieStore);
        httpClient = HttpClientBuilder.create()
                .setDefaultCookieStore(cookieStore)
                .build();
    }

    public MordaHttpClient(String ua) {
        cookieStore = new BasicCookieStore();
        httpContext = new BasicHttpContext();
        httpContext.setAttribute(HttpClientContext.COOKIE_STORE, cookieStore);
        httpClient = HttpClientBuilder.create()
                .setDefaultCookieStore(cookieStore)
                .setUserAgent(ua)
                .build();
    }

    public HttpClient getHttpClient() {
        return httpClient;
    }

    public void setHttpClient(HttpClient httpClient) {
        this.httpClient = httpClient;
    }

    public CookieStore getCookieStore() {
        return cookieStore;
    }

    public HttpContext getHttpContext() {
        return httpContext;
    }

    public HttpResponse executeGet(String url) throws IOException {
        HttpUriRequest get = RequestBuilder.get().addHeader("Accept", "*/*").setUri(url).build();
        return httpClient.execute(get, httpContext);
    }
}
