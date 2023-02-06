package ru.yandex.autotests.mordacom.utils;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesTabsEntry;
import ru.yandex.autotests.utils.morda.language.Language;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
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
                startsWith(url),
                hasAttribute(HtmlAttribute.HREF, startsWith(href))
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

        public TabsInfoBuilder(ServicesTabsEntry service, String request, Language language) {
            this.text = getTranslation("home", "spok_yes", "tabs." + service.getId(), language).trim();
            this.href = normalizeUrl(service.getUrl()).replace("clid=691", "clid=505");
            this.url = normalizeUrl(service.getUrl()).replace("clid=691", "clid=505");
            String searchUrl = service.getSearch();
            if (searchUrl == null || searchUrl.isEmpty()) {
                this.request = startsWith(normalizeUrl(service.getUrl()));
                searchUrl = normalizeUrl(service.getUrl());
            } else if (searchUrl.contains("?")) {
                searchUrl = normalizeUrl(service.getSearch());
                if (searchUrl.endsWith("=")) {
                    this.request = startsWith(searchUrl + request);
                } else {
                    this.request = startsWith(searchUrl + "&text=" + request);
                }
            } else {
                searchUrl = normalizeUrl(service.getSearch());
                this.request = startsWith(searchUrl + "?text=" + request);
            }
            this.baseSearchUrl = searchUrl.replaceFirst("\\?.*$", "");
        }

        public static TabsInfoBuilder tabInfo(ServicesTabsEntry service, String request, Language language) {
            return new TabsInfoBuilder(service, request, language);
        }

        public TabsInfoBuilder withUrl(String url) {
            if (url != null) {
                this.url = url;
            }
            return this;
        }

        public TabsInfoBuilder withRequest(String request) {
            if (request != null) {
                this.request = startsWith(request);
            }
            return this;
        }

        public TabInfo build() {
            return new TabInfo(text, href, url, request, baseSearchUrl);
        }
    }

    public static String normalizeUrl(String url) {
        if (url.startsWith("//")) {
            url = CONFIG.getProtocol() + ":" + url;
        }
        return url;
    }

    @Override
    public String toString() {
        return text.toString();
    }
}