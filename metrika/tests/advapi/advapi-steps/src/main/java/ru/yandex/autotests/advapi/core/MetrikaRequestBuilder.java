package ru.yandex.autotests.advapi.core;

import org.apache.http.HttpEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.entity.StringEntity;
import org.apache.http.util.Asserts;
import ru.yandex.autotests.advapi.steps.report.BaseReportSteps;
import ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclient.lite.core.config.HttpClientConnectionConfig;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;

import javax.ws.rs.core.MediaType;

import static ru.yandex.autotests.advapi.core.AdvApiJson.GSON_REQUEST;

/**
 * Created by konkov on 26.09.2014.
 */
public class MetrikaRequestBuilder extends BackEndRequestBuilder {

    /**
     * Ещё заголовки устанавливаются в {@link BaseReportSteps#execute(Class, HttpUriRequest)}
     */
    public static final String CONTENT_TYPE = "Content-Type";
    public static final String APPLICATION_X_YAMETRIKA_JSON = "application/x-yametrika+json";

    private IFormParameters commonParameters = FreeFormParameters.EMPTY;

    @Override
    protected URIBuilder getBuilder() {
        Asserts.notNull(getConfig().getScheme(), "Scheme must be specified");
        Asserts.notNull(getConfig().getHost(), "Host must be specified");

        MetrikaURIBuilder builder = new MetrikaURIBuilder();
        builder.setScheme(getConfig().getScheme());
        builder.setHost(getConfig().getHost());
        builder.setPort(getConfig().getPort() == null ? -1 : getConfig().getPort());
        builder.setPath(getConfig().getPath());

        builder.setCommonParameters(commonParameters);

        return builder;
    }

    public MetrikaRequestBuilder withCommonParameters(IFormParameters commonParameters) {
        this.commonParameters = commonParameters;
        return this;
    }

    public IFormParameters getCommonParameters() {
        return commonParameters;
    }

    public void setCommonParameters(IFormParameters commonParameters) {
        this.commonParameters = commonParameters;
    }

    public MetrikaRequestBuilder(HttpClientConnectionConfig config) {
        super(config);
    }

    public <T> HttpPost post(T entity, IFormParameters... params) {
        HttpPost post = post(getEntity(entity), params);
        post.setHeader(CONTENT_TYPE, APPLICATION_X_YAMETRIKA_JSON);
        return post;
    }

    public <T> HttpPut put(T entity, IFormParameters... params) {
        HttpPut put = put(getEntity(entity), params);
        put.setHeader(CONTENT_TYPE, APPLICATION_X_YAMETRIKA_JSON);
        return put;
    }

    private <T> HttpEntity getEntity(T object) {
        StringEntity entity = new StringEntity(GSON_REQUEST.toJson(object), "UTF-8");
        entity.setContentType(MediaType.APPLICATION_JSON);
        return entity;
    }
}
