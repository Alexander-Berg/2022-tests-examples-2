package ru.yandex.autotests.audience.internal.api.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ExperimentSegmentParameters extends AbstractFormParameters {

    @FormParameter("id")
    private long id;

    public ExperimentSegmentParameters withId(int id) {
        this.id = id;
        return this;
    }

    public static ExperimentSegmentParameters id(int id) {
        return new ExperimentSegmentParameters().withId(id);
    }

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }
}
