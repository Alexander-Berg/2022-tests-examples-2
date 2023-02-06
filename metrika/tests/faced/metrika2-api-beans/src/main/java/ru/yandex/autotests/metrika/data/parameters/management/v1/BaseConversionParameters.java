package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class BaseConversionParameters extends AbstractFormParameters {

    @FormParameter("comment")
    private String comment;

    public String getComment() {
        return comment;
    }

    public void setComment(String comment) {
        this.comment = comment;
    }

    public BaseConversionParameters withComment(String comment) {
        this.comment = comment;
        return this;
    }
}
