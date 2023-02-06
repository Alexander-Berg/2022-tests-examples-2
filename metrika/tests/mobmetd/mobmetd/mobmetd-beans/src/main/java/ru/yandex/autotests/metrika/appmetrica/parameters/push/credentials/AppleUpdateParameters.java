package ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonFrontParameters;

/**
 * @author dancingelf
 */
public class AppleUpdateParameters extends CommonFrontParameters {

    @FormParameter("cert_type")
    private String certType;
    @FormParameter("password")
    private String password;

    public AppleUpdateParameters(String password, String certType) {
        this.certType = certType;
        this.password = password;
    }

    public String getCertType() {
        return certType;
    }

    public String getPassword() {
        return password;
    }
}
