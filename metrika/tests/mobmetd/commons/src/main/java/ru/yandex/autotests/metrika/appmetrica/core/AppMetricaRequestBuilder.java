package ru.yandex.autotests.metrika.appmetrica.core;

import com.google.gson.Gson;
import org.apache.http.HttpEntity;
import org.apache.http.client.methods.*;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.entity.ByteArrayEntity;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.entity.mime.HttpMultipartMode;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.apache.http.entity.mime.content.FileBody;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.core.RequestBuilder;
import ru.yandex.autotests.metrika.appmetrica.body.CustomEntityBody;
import ru.yandex.autotests.metrika.appmetrica.body.MultipartFormBody;
import ru.yandex.autotests.metrika.appmetrica.exceptions.AppMetricaException;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;

import javax.ws.rs.core.MediaType;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.charset.StandardCharsets;

import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;

public class AppMetricaRequestBuilder implements RequestBuilder {

    private final Gson gson;
    private final FreeFormParameters commonParameters;
    private final FreeFormParameters commonHeaders;

    public AppMetricaRequestBuilder(Gson gson) {
        this.gson = gson;
        this.commonParameters = makeParameters();
        this.commonHeaders = makeParameters();
    }

    public HttpUriRequest build(Method method, URI uri, FreeFormParameters headers, Object bean) {
        HttpUriRequest request = buildUriRequest(method, uri, bean);
        commonHeaders.forEach(request::addHeader);
        headers.forEach(request::setHeader);
        return request;
    }

    @Override
    public HttpUriRequest build(Method method, URI uri, Object bean) {
        HttpUriRequest request = buildUriRequest(method, uri, bean);
        commonHeaders.forEach(request::addHeader);
        return request;
    }

    private HttpUriRequest buildUriRequest(Method method, URI uri, Object bean) {
        switch (method) {
            case GET:
                return new HttpGet(getActualUri(uri));
            case POST:
                HttpPost httpPost = new HttpPost(getActualUri(uri));
                httpPost.setEntity(getEntity(bean));
                return httpPost;
            case PUT:
                HttpPut httpPut = new HttpPut(getActualUri(uri));
                httpPut.setEntity(getEntity(bean));
                return httpPut;
            case DELETE:
                return new HttpDelete(getActualUri(uri));
            default:
                throw new AppMetricaException("Make compiler happy");
        }
    }

    private URI getActualUri(URI uri) {
        try {
            return new URIBuilder(uri)
                    .addParameters(commonParameters.getParameters())
                    .build();
        } catch (URISyntaxException e) {
            throw new AppMetricaException("Ошибка при формировании URI", e);
        }
    }

    private HttpEntity getEntity(Object body) {
        if (body instanceof MultipartFormBody) {
            return buildMultipartBody((MultipartFormBody) body);
        } else if (body instanceof CustomEntityBody) {
            return buildCustomEntityBody((CustomEntityBody) body);
        } else {
            return buildJsonBody(body);
        }
    }

    private HttpEntity buildJsonBody(Object body) {
        StringEntity stringEntity = new StringEntity(gson.toJson(body), StandardCharsets.UTF_8);
        stringEntity.setContentType(MediaType.APPLICATION_JSON);
        return stringEntity;
    }

    private HttpEntity buildCustomEntityBody(CustomEntityBody body) {
        ContentType contentType = ContentType.create(body.getContentType(), StandardCharsets.UTF_8);
        return new ByteArrayEntity(body.getContent(), contentType);
    }

    private HttpEntity buildMultipartBody(MultipartFormBody body) {
        FileBody fileBody = new FileBody(body.getFile());
        MultipartEntityBuilder builder = MultipartEntityBuilder.create()
                .setMode(HttpMultipartMode.BROWSER_COMPATIBLE)
                .addPart(body.getName(), fileBody);
        return builder.build();
    }

    public AppMetricaRequestBuilder withCommonParameters(IFormParameters... parameters) {
        commonParameters.append(parameters);
        return this;
    }

    public AppMetricaRequestBuilder withCommonHeaders(IFormParameters... parameters) {
        commonHeaders.append(parameters);
        return this;
    }
}
