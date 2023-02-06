package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by konkov on 26.04.2016.
 */
public class CurrencyParameters extends AbstractFormParameters {

    @FormParameter("currency")
    private String currency;

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    public CurrencyParameters withCurrency(final String currency) {
        this.currency = currency;
        return this;
    }

    public static CurrencyParameters currency(String currency) {
        return new CurrencyParameters().withCurrency(currency);
    }

}
