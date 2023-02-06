package ru.yandex.autotests.mordatmplerr.mordatypes;

import gumi.builders.UrlBuilder;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;
import ru.yandex.autotests.mordatmplerr.rules.LogsRule;
import ru.yandex.autotests.mordatmplerr.rules.YandexUidRecorderAction;

import java.util.HashMap;
import java.util.Map;

import static ru.yandex.autotests.mordatmplerr.mordatypes.Browser.FIREFOX;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.TIZEN;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.14
 */
public abstract class Morda {
    public abstract String getUrl(String mordaEnv);

    protected String getUrl(UrlBuilder urlBuilder) {
        if (touchType != null && touchType.equals(TIZEN)) {
            parameters.put("clid", "1983172");
        }
        for (Map.Entry<String, String> entry : parameters.entrySet()) {
            urlBuilder = urlBuilder.addParameter(entry.getKey(), entry.getValue());
        }
        System.out.println(parameters);
        return urlBuilder.toString();
    }

    protected Browser browser = FIREFOX;
    protected TouchType touchType = null;
    protected Map<String, String> parameters = new HashMap<>();

    public Morda withBrowser(Browser browser) {
        this.browser = browser;
        return this;
    }

    public Morda withTouchType(TouchType touchType) {
        this.touchType = touchType;
        return this;
    }

    public Morda withParameter(String key, String value) {
        parameters.put(key, value);
        return this;
    }

    public MordaAllureBaseRule getRule() {
        if (touchType != null) {
            return getRule(browser, touchType);
        }
        return getRule(browser);
    }

    private MordaAllureBaseRule getRule(Browser browser) {
        YandexUidRecorderAction uid = new YandexUidRecorderAction();
        return new MordaAllureBaseRule(browser.getCaps())
                .withRule(new LogsRule(uid))
                .withProxyAction(uid);
    }

    public MordaAllureBaseRule getRule(Browser browser, TouchType touchType) {
        return getRule(browser)
                .replaceProxyAction(UserAgentAction.class, touchType.getUserAgent());
    }

    protected abstract String getUrlPattern();

    @Override
    public String toString() {
        if (touchType != null) {
            return touchType.name();
        } else {
            return browser.name();
        }
    }
}
