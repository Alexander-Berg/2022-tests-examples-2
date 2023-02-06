package ru.yandex.autotests.audience.internal.api.parameters;

import org.apache.commons.lang.StringUtils;
import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ExperimentSegmentsParameters extends AbstractFormParameters {

    @FormParameter("ids")
    private String ids;

    public ExperimentSegmentsParameters withIds(Integer[] ids) {
        this.ids = StringUtils.join(ids, ",");
        return this;
    }

    public static ExperimentSegmentsParameters ids(Integer[] ids) {
        return new ExperimentSegmentsParameters().withIds(ids);
    }

    public String getIds() {
        return ids;
    }

    public void setIds(String ids) {
        this.ids = ids;
    }
}
