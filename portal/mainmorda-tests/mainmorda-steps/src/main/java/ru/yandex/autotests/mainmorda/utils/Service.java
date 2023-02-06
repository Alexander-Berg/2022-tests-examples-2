package ru.yandex.autotests.mainmorda.utils;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.autotests.utils.morda.language.TankerManager.TRIM;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.04.13
 */
public class Service {
    private static final Properties CONFIG = new Properties();

    private static final String HOME = "home";
    private static final String ALL_SERVICES = "allServices";
    private static final String MARKET_CLID = "505";

    public String id;
    public String serviceName;
    public Matcher<String> name;
    public Matcher<String> allGroup;
    public Matcher<String> description;
    public Matcher<String> href;

    public Service(ServicesV122Entry service) {
        this.id = service.getId();
        this.serviceName = getTranslation(TRIM, HOME, ALL_SERVICES,
                service.getAllGroup() + "." + service.getId() + ".title", CONFIG.getLang());
        this.name = equalTo(serviceName);
        this.allGroup = equalTo(serviceName.substring(0, 1));
        try {
            String description = getTranslationSafely(TRIM, HOME, ALL_SERVICES,
                    service.getAllGroup() + "." + service.getId() + ".desc", CONFIG.getLang()).replace("&nbsp", " ");
            this.description = equalTo(description);
        } catch (IllegalArgumentException e) {
            this.description = equalTo("");
        }
        this.href = startsWith(normalizeUrl(service.getHref(), CONFIG.getProtocol()));
        if (this.id.equals("market")) {
            this.href = startsWith(normalizeUrl(service.getHref().replace("506",MARKET_CLID), CONFIG.getProtocol()));
        }
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
