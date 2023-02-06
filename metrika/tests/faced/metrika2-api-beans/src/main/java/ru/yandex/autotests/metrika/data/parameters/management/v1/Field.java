package ru.yandex.autotests.metrika.data.parameters.management.v1;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;

import java.util.Arrays;
import java.util.List;

/**
 * Created by konkov on 29.01.2015.
 */
public enum Field implements IFormParameters {
    GOALS,
    MIRRORS,
    GRANTS,
    FILTERS,
    OPERATIONS,
    OFFLINE_OPTIONS,
    PUBLISHER_OPTIONS;

    public static final String PARAMETER_NAME = "field";

    @Override
    public List<NameValuePair> getParameters() {
        return Arrays.<NameValuePair>asList(new BasicNameValuePair(PARAMETER_NAME, this.name().toLowerCase()));
    }
}
