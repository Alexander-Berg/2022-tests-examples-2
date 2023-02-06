package ru.yandex.autotests.metrika.data.parameters.internal;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class CheckBigParameters extends AbstractFormParameters {

    @FormParameter("ids")
    private Long counterId;

    public void setCounterId(Long counterId) {
        this.counterId = counterId;
    }

    public Long getCounterId() {
        return counterId;
    }

    public CheckBigParameters withCounterId(Long counterId) {
        this.counterId = counterId;
        return this;
    }

}
