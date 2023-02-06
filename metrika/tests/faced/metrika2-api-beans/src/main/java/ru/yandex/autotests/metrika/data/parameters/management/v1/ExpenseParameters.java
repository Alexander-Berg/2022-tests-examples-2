package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ExpenseParameters extends BaseConversionParameters {

    @FormParameter("provider")
    private String provider;

    @FormParameter("column_settings")
    private String columnSettings;

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

    public ExpenseParameters withProvider(String provider) {
        this.provider = provider;
        return this;
    }

    public String getColumnSettings() {
        return columnSettings;
    }

    public void setColumnSettings(String columnSettings) {
        this.columnSettings = columnSettings;
    }

    public ExpenseParameters withSettings(String columnSettings) {
        this.columnSettings = columnSettings;
        return this;
    }
}
