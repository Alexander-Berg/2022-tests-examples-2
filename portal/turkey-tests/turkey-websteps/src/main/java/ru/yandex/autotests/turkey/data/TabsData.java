package ru.yandex.autotests.turkey.data;

import ch.lambdaj.function.convert.Converter;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordaexportsclient.MordaExportClient;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.utils.TabInfo;

import java.net.URI;
import java.util.List;
import java.util.stream.Collectors;

import static ch.lambdaj.Lambda.convert;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_TABS;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.ServicesV122EntryMatcher.with;
import static ru.yandex.autotests.turkey.data.SearchData.ENCODED_REQUEST;
import static ru.yandex.autotests.turkey.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.turkey.utils.TabInfo.TabsInfoBuilder.tabInfo;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: ivannik
 * Date: 14.09.2014
 */
public class TabsData {
    public static final Properties CONFIG = new Properties();

    public static final List<TabInfo> ALL_TABS = exports(SERVICES_TABS).stream()
            .filter(e -> e.getDomain().equals("com.tr") && e.getContent().equals("comtr"))
            .map(e -> tabInfo(e, ENCODED_REQUEST).build())
            .collect(Collectors.toList());

    public static final List<LinkInfo> TABS_PAGE_404 = convert(exports(SERVICES_V12_2, domain(CONFIG.getBaseDomain()),
                    with().tabs(greaterThan(0)), with().tabsMore(0)), new Converter<ServicesV122Entry, LinkInfo>() {
                @Override
                public LinkInfo convert(ServicesV122Entry from) {
                    if (from.getId().equals("maps")) {
                        return new LinkInfo(
                                equalTo(getTranslation("home", "tabs", from.getId(), CONFIG.getLang())),
                                startsWith("http://harita.yandex.com.tr/"),
                                hasAttribute(HtmlAttribute.HREF,
                                        startsWith(normalizeUrl(from.getHref(), CONFIG.getProtocol()))));
                    } else {
                        return new LinkInfo(
                                equalTo(getTranslation("home", "tabs", from.getId(), CONFIG.getLang())),
                                startsWith(normalizeUrl(
                                        from.getHref().replace("clid=691", "clid=505"), CONFIG.getProtocol())));
                    }
                }
            }
    );
}
