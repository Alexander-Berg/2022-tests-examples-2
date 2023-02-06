package ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * @author dancingelf
 */
public class AppleDeleteParameters extends AbstractFormParameters {

    @FormParameter("cert_type")
    private final String certType;

    public AppleDeleteParameters(String certType) {
        this.certType = certType;
    }

    public String getCertType() {
        return certType;
    }
}
