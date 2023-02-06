package ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonFrontParameters;


public class WinUpdateParameters extends CommonFrontParameters {

    @FormParameter("package_security_identifier")
    private final String packageSecurityIdentifier;
    @FormParameter("secret_key")
    private final String secretKey;

    public WinUpdateParameters(String packageSecurityIdentifier, String secretKey) {
        this.packageSecurityIdentifier = packageSecurityIdentifier;
        this.secretKey = secretKey;
    }

    public String getPackageSecurityIdentifier() {
        return packageSecurityIdentifier;
    }

    public String getSecretKey() {
        return secretKey;
    }
}
