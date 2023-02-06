package ru.yandex.autotests.audience.parameters;

import ru.yandex.audience.segmentab.ExperimentSource;
import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by ava1on on 14.06.17.
 */
public class ExperimentSourceParameters extends AbstractFormParameters {
    @FormParameter("source")
    private String source;

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public ExperimentSourceParameters withSource(final String source) {
        this.source = source;
        return this;
    }

    public static ExperimentSourceParameters source(String source) {
        return new ExperimentSourceParameters().withSource(source);
    }

    public static ExperimentSourceParameters source(ExperimentSource source) {
        return source(source.toString());
    }
}
