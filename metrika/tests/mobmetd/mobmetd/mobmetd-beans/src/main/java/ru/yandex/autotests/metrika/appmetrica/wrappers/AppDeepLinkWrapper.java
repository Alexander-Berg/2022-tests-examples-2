package ru.yandex.autotests.metrika.appmetrica.wrappers;

import ru.yandex.metrika.mobmet.model.redirect.AppDeepLink;


public class AppDeepLinkWrapper {

    private AppDeepLink deepLink;

    public AppDeepLinkWrapper(AppDeepLink deepLink) {
        this.deepLink = deepLink;
    }

    public AppDeepLink getDeepLink() {
        return deepLink;
    }

    @Override
    public String toString() {
        return deepLink.getTitle();
    }
}
