package ru.yandex.autotests.metrika.data.b2b;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;

/**
 * Created by konkov on 06.10.2015.
 *
 * Информация об одном тестовом вызове API в b2b тестах.
 */
public class B2bSample {
    private String title;
    private RequestType<?> requestType;
    private FreeFormParameters parameters;

    @Override
    public String toString() {
        return title;
    }

    public String getTitle() {
        return title;
    }

    public RequestType<?> getRequestType() {
        return requestType;
    }

    public IFormParameters getParameters() {
        return parameters;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public void setRequestType(RequestType<?> requestType) {
        this.requestType = requestType;
    }

    public void setParameters(IFormParameters parameters) {
        this.parameters = new FreeFormParameters().append(parameters);
    }

    public B2bSample withTitle(final String title) {
        this.title = title;
        return this;
    }

    public B2bSample withRequestType(final RequestType<?> requestType) {
        this.requestType = requestType;
        return this;
    }

    public B2bSample withParameters(final IFormParameters parameters) {
        setParameters(parameters);
        return this;
    }

    public B2bSample withParameters(final IFormParameters... params) {
        this.parameters = new FreeFormParameters().append(params);
        return this;
    }

}
