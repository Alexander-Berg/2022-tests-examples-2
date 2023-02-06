package ru.yandex.autotests.metrika.appmetrica.parameters;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;

import java.util.Collections;
import java.util.List;

public enum AppListV2SortParameter implements IFormParameters {

    name("name"),
    permission_date("permission_date");

    private String value;

    AppListV2SortParameter(String value) {
        this.value = value;
    }

    @Override
    public List<NameValuePair> getParameters() {
        return Collections.singletonList(new BasicNameValuePair("sort", value));
    }
}
