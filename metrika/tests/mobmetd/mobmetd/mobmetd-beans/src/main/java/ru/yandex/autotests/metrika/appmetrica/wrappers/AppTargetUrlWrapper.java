package ru.yandex.autotests.metrika.appmetrica.wrappers;

import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;


public class AppTargetUrlWrapper {

    private AppTargetUrl targetUrl;

    public AppTargetUrlWrapper(AppTargetUrl targetUrl) {
        this.targetUrl = targetUrl;
    }

    public AppTargetUrl getTargetUrl() {
        return targetUrl;
    }

    @Override
    public String toString() {
        return targetUrl.getTitle();
    }
}
