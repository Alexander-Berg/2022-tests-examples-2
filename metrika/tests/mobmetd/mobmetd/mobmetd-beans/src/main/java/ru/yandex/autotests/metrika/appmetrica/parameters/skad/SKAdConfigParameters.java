package ru.yandex.autotests.metrika.appmetrica.parameters.skad;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class SKAdConfigParameters  extends AbstractFormParameters {

    @FormParameter("force_bundles")
    private boolean forceBundles;

    public boolean isForceBundles() {
        return forceBundles;
    }

    public void setForceBundles(boolean forceBundles) {
        this.forceBundles = forceBundles;
    }

    public SKAdConfigParameters forceBundles() {
        this.forceBundles = true;
        return this;
    }
}
