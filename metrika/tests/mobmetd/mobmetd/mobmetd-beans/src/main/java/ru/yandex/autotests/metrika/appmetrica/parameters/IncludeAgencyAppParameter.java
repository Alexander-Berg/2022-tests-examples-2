package ru.yandex.autotests.metrika.appmetrica.parameters;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;

import java.util.Collections;
import java.util.List;

/**
 * Created by graev on 18/01/2017.
 */
public enum IncludeAgencyAppParameter implements IFormParameters {
    INCLUDE_AGENCY {
        @Override
        public List<NameValuePair> getParameters() {
            return Collections.singletonList(new BasicNameValuePair("include_agency_apps", "true"));
        }
    };
}
