package ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;

import java.util.Collections;
import java.util.List;

public enum PushCampaignParameter implements IFormParameters {
    FORCE {
        @Override
        public List<NameValuePair> getParameters() {
            return Collections.singletonList(new BasicNameValuePair("force", "true"));
        }
    };
}
