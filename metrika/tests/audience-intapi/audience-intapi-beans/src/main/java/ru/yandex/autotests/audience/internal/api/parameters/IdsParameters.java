package ru.yandex.autotests.audience.internal.api.parameters;

import java.util.List;

import org.apache.commons.lang3.ArrayUtils;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;

public class IdsParameters extends AbstractFormParameters {
    @FormParameter("ids")
    private String ids;

    public String getIds() {
        return ids;
    }

    public void setIds(long... ids) {
        this.ids = JsonUtils.toString(ids, true);
    }

    public IdsParameters withIds(long... ids) {
        setIds(ids);
        return this;
    }

    public static IdsParameters ids(long... ids) {
        return new IdsParameters().withIds(ids);
    }
    public static IdsParameters ids(List<Long> ids) {
        return new IdsParameters().withIds(ids.stream().mapToLong(x -> x).toArray());
    }
}
