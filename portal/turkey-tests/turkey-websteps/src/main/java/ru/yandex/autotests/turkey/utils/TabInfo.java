package ru.yandex.autotests.turkey.utils;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesTabsEntry;
import ru.yandex.autotests.turkey.Properties;

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
    public String alternativeSearchUrl;
    public String imagesSearchUrl;

    public TabInfo(String text, String href, String url, Matcher<String> request,
                   String baseSearchUrl, String alternativeSearchUrl, String imagesSearchUrl) {
        super(
                equalTo(text),
                startsWith(url),
                hasAttribute(HtmlAttribute.HREF, startsWith(href))
        );
        this.request = request;
        this.baseSearchUrl = baseSearchUrl;
        this.alternativeSearchUrl = alternativeSearchUrl;
        this.imagesSearchUrl = imagesSearchUrl;
    }

    public static class TabsInfoBuilder {
        private String text;
        private String href;
        private String url;
        private Matcher<String> request;
        private String baseSearchUrl;
        private String alternativeSearchUrl;
        private String imagesSearchUrl;

        public TabsInfoBuilder(ServicesTabsEntry service, String request) {
            this.text = getTranslation("home", "tabs", service.getId(), CONFIG.getLang());
            this.href = normalizeUrl(service.getUrl()).replace("clid=691", "clid=505");
            this.url = normalizeUrl(service.getUrl()).replace("clid=691", "clid=505");
            String searchUrl = service.getSearch();
            if (searchUrl == null || searchUrl.isEmpty()) {
                this.request = startsWith(normalizeUrl(service.getUrl()));
                searchUrl = normalizeUrl(service.getUrl());
            } else if (searchUrl.contains("?")) {
                searchUrl = normalizeUrl(searchUrl);
                if (searchUrl.endsWith("=")) {
                    this.request = startsWith(searchUrl + request);
                } else {
                    this.request = startsWith(searchUrl + "&text=" + request);
                }
            } else {
                searchUrl = normalizeUrl(searchUrl);
                this.request = startsWith(searchUrl + "?text=" + request);
            }
            this.baseSearchUrl = searchUrl.replaceFirst("\\?.*$", "");
            this.alternativeSearchUrl = baseSearchUrl.replace("yandex","aile.yandex");
            this.imagesSearchUrl = alternativeSearchUrl.replace("gorsel","images");
        }

        public static TabsInfoBuilder tabInfo(ServicesTabsEntry service, String request) {
            return new TabsInfoBuilder(service, request);
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
            return new TabInfo(text, href, url, request, baseSearchUrl, alternativeSearchUrl,
                    imagesSearchUrl);
        }
    }

    private static String normalizeUrl(String url) {
        return LinkUtils.normalizeUrl(url, CONFIG.getProtocol());
    }

    @Override
    public String toString() {
        return text.toString();
    }
}