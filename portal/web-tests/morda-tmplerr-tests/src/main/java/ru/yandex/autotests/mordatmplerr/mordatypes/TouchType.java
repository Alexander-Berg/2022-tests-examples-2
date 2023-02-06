package ru.yandex.autotests.mordatmplerr.mordatypes;

import ru.yandex.autotests.mordatmplerr.Properties;

public enum TouchType {
    IPHONE_SAFARI(new Properties().getIphoneSafariUa()),
    IPHONE_CHROME(new Properties().getIphoneChromeUa()),
    WP(new Properties().getWpUa()),
    ANDROID_CHROME(new Properties().getAndroidChromeUa()),
    SHELL(new Properties().getAndroidChromeUa()),
    TIZEN(new Properties().getTizenUa()),
    TABLET(new Properties().getTabletUa()),
    PDA(new Properties().getPdaUa());

    private String userAgent;

    private TouchType(String userAgent) {
        this.userAgent = userAgent;
    }

    public String getUserAgent() {
        return userAgent;
    }
}