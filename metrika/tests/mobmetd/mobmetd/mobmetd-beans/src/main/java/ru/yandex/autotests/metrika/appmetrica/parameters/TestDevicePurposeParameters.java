package ru.yandex.autotests.metrika.appmetrica.parameters;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.metrika.mobmet.model.TestDevicePurpose;

import java.util.Collections;
import java.util.List;
import java.util.stream.Stream;

/**
 * Created by graev on 18/01/2017.
 */
public enum TestDevicePurposeParameters implements IFormParameters {
    REATTRIBUTION(TestDevicePurpose.REATTRIBUTION),
    PUSH(TestDevicePurpose.PUSH_NOTIFICATIONS);

    private TestDevicePurpose purpose;

    TestDevicePurposeParameters(TestDevicePurpose purpose) {
        this.purpose = purpose;
    }


    @Override
    public List<NameValuePair> getParameters() {
        return Collections.singletonList(new BasicNameValuePair("purpose", purpose.toString()));
    }

    public static TestDevicePurposeParameters param(TestDevicePurpose purpose) {
        return Stream.of(values())
                .filter(v -> v.purpose == purpose)
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Unknown TestDevicePurpose: " + purpose));
    }
}
