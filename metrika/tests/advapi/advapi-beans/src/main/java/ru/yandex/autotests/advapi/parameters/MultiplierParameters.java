package ru.yandex.autotests.advapi.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class MultiplierParameters extends AbstractFormParameters {

    @FormParameter("multiplier")
    private double multiplier;

    public MultiplierParameters(double multiplier) {
        this.multiplier = multiplier;
    }

    public double getMultiplier() {
        return multiplier;
    }

    public void setMultiplier(double multiplier) {
        this.multiplier = multiplier;
    }
}
