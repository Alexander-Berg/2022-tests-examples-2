package ru.yandex.autotests.audience.parameters;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;

import java.util.List;

import static java.util.Collections.singletonList;

/**
 * Created by konkov on 27.03.2017.
 */
public enum ModificationType implements IFormParameters {
    ADDITION,
    SUBTRACTION,
    REPLACE;

    public static final String PARAMETER_NAME = "modification_type";

    @Override
    public List<NameValuePair> getParameters() {
        return singletonList(new BasicNameValuePair(PARAMETER_NAME, this.name().toLowerCase()));
    }
}
