package ru.yandex.autotests.audience.internal.api.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ExperimentParameters extends AbstractFormParameters {

    @FormParameter("id")
    private long id;

    public ExperimentParameters withId(int id) {
        this.id = id;
        return this;
    }

    public static ExperimentParameters id(int id) {
        return new ExperimentParameters().withId(id);
    }

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }
}
