package ru.yandex.autotests.metrika.appmetrica.info.push.credentials;

import org.apache.commons.lang3.builder.ToStringBuilder;

import java.io.File;

import static org.apache.commons.lang3.builder.ToStringStyle.SHORT_PREFIX_STYLE;

/**
 * @author dancingelf
 */
public class AppleCredentialsInfo {

    private final File certFile;
    private final String password;
    private final String certType;

    public AppleCredentialsInfo(File cert, String password, String certType) {
        this.certFile = cert;
        this.password = password;
        this.certType = certType;
    }

    public File getCertFile() {
        return certFile;
    }

    public String getCertType() {
        return certType;
    }

    public String getPassword() {
        return password;
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this, SHORT_PREFIX_STYLE);
    }
}
