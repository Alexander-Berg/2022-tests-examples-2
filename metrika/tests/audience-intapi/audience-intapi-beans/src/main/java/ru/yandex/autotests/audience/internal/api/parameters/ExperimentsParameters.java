package ru.yandex.autotests.audience.internal.api.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ExperimentsParameters extends AbstractFormParameters {

    @FormParameter("counterId")
    private long counterId;

    public ExperimentsParameters withCounterId(long counterId) {
        this.counterId = counterId;
        return this;
    }

    public static ExperimentsParameters counterId(long counterId) {
        return new ExperimentsParameters().withCounterId(counterId);
    }

    public long getCounterId() {
        return counterId;
    }

    public void setCounterId(long counterId) {
        this.counterId = counterId;
    }
}
