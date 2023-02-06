package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

import java.util.List;
import java.util.stream.Collectors;

public class ActivityParameters extends CommonFrontParameters {

    @FormParameter("ids")
    private String ids;

    public String getIds() {
        return ids;
    }

    public ActivityParameters withIds(List<Long> ids) {
        this.ids = ids.stream().map(Object::toString).collect(Collectors.joining(","));
        return this;
    }
}
