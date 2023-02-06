package ru.yandex.autotests.mainmorda.utils;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mainmorda.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.04.13
 */
public class TabInfo extends LinkInfo {
    private static final Properties CONFIG = new Properties();
    public Matcher<String> request;
    public String baseSearchUrl;

    public TabInfo(String text, String href, String url, Matcher<String> request, String baseSearchUrl) {
        super(
                equalTo(text),
                startsWith(normalizeUrl(url, CONFIG.getProtocol())),
                hasAttribute(HtmlAttribute.HREF, startsWith(normalizeUrl(href, CONFIG.getProtocol())))
        );
        this.request = request;
        this.baseSearchUrl = baseSearchUrl;
    }

    public static class TabsInfoBuilder {
        private String text;
        private String href;
        private String url;
        private Matcher<String> request;
        private String baseSearchUrl;

        public TabsInfoBuilder(ServicesV122Entry service, String request) {
            this.text = getTranslation("home", "tabs", service.getId(), CONFIG.getLang());
            this.href = service.getHref();
            this.url = service.getHref();
            String searchUrl = service.getSearch();
            if (searchUrl == null || searchUrl.isEmpty()) {
                this.request = startsWith(normalizeUrl(service.getHref(), CONFIG.getProtocol()));
            } else if (searchUrl.contains("?")) {
                if (searchUrl.endsWith("=")) {
                    this.request = startsWith(normalizeUrl(service.getSearch() + request, CONFIG.getProtocol()));
                } else {
                    this.request = startsWith(
                            normalizeUrl(service.getSearch() + "&text=" + request, CONFIG.getProtocol()));
                }
            } else {
                this.request = startsWith(normalizeUrl(service.getSearch() + "?text=" + request, CONFIG.getProtocol()));
            }
            if (service.getSearch() != null) {
                this.baseSearchUrl = service.getSearch().replaceFirst("\\?.*$", "");
            }
        }

        public static TabsInfoBuilder tabInfo(ServicesV122Entry service, String request) {
            return new TabsInfoBuilder(service, request);
        }

        public TabsInfoBuilder withHref(String href) {
            if (href != null) {
                this.href = href;
            }
            return this;
        }

        public TabsInfoBuilder withBaseSearchUrl(String url) {
            if (url != null) {
                this.baseSearchUrl = url.replaceFirst("\\?.*$", "");
            }
            return this;
        }

        public TabsInfoBuilder withRequest(String request) {
            if (request != null) {
                this.request = startsWith(normalizeUrl(request, CONFIG.getProtocol()));
            }
            return this;
        }

        public TabInfo build() {
            return new TabInfo(text, href, url, request, baseSearchUrl);
        }
    }

    @Override
    public String toString() {
        return text.toString();
    }
}