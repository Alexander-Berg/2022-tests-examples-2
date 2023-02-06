package ru.yandex.autotests.mordamobile.utils;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.mordamobile.Properties;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.autotests.utils.morda.language.TankerManager.TRIM;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 05.02.2015.
 */
public class Service {
    private static final Properties CONFIG = new Properties();

    private static final String HOME = "home";
    private static final String ALL_SERVICES = "allServices";
    private static final String SERVICES = "services";

    public String id;
    public String serviceName;
    public Matcher<String> name;
    public Matcher<String> allGroup;
    public Matcher<String> description;
    public Matcher<String> href;

    public Service(ServicesV122Entry service, boolean withDescription) {
        this.id = service.getId();
        this.serviceName = getTranslation(TRIM, HOME, SERVICES,
                SERVICES + "." + service.getId() + ".title_mobile", CONFIG.getLang());
        this.name = equalTo(serviceName);
        this.allGroup = equalTo(serviceName.substring(0, 1));
        if (withDescription) {
            this.description = equalTo(getTranslationSafely(TRIM, HOME, ALL_SERVICES,
                    service.getAllGroup() + "." + service.getId() + ".desc", CONFIG.getLang()).replace("&nbsp", " "));
        }
        this.href = service.getTouch() != null
                ? startsWith(normalizeUrl(service.getTouch(), CONFIG.getProtocol()))
                : service.getPda() != null
                    ? startsWith(normalizeUrl(service.getPda(), CONFIG.getProtocol()))
                    : startsWith(normalizeUrl(service.getHref(), CONFIG.getProtocol()));

    }

    public String getServiceName() {
        return serviceName;
    }

    @Override
    public String toString() {
        return serviceName;
    }

    public static String normalizeUrl(String url, String protocol) {
        return url.startsWith("//")
                ? protocol + ":" + url
                : url;
    }
}