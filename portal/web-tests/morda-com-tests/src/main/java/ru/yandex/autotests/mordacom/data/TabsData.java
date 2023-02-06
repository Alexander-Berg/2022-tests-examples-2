package ru.yandex.autotests.mordacom.data;

import ch.lambdaj.function.convert.Converter;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.utils.TabInfo;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesTabsEntry;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;

import java.util.List;

import static ch.lambdaj.Lambda.convert;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mordacom.data.SearchData.ENCODED_REQUEST;
import static ru.yandex.autotests.mordacom.utils.TabInfo.TabsInfoBuilder.tabInfo;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_TABS;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.ServicesV122EntryMatcher.with;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: leonsabr
 * Date: 18.08.2010
 */
public class TabsData {
    private static final Properties CONFIG = new Properties();

    public static List<TabInfo> getAllTabs(final Language language) {
        return convert(exports(SERVICES_TABS, domain(CONFIG.getBaseDomain()),
                        having(on(ServicesTabsEntry.class).getContent(), equalTo("com")),
                        having(on(ServicesTabsEntry.class).getTabs(), not(isEmptyOrNullString()))),
                new Converter<ServicesTabsEntry, TabInfo>() {
                    @Override
                    public TabInfo convert(ServicesTabsEntry from) {
                        if (from.getId().equals("mail")) {
                            return tabInfo(from, ENCODED_REQUEST, language)
                                    .withRequest("https://mail.yandex.com/")
                                    .withUrl("https://mail.yandex.com/")
                                    .build();
                        } else {
                            return tabInfo(from, ENCODED_REQUEST, language).build();
                        }
                    }
                }
        );
    }

    public static final List<LinkInfo> TABS_PAGE_404 = convert(exports(SERVICES_V12_2, domain(CONFIG.getBaseDomain()),
                    with().tabs(greaterThan(0)), with().tabsMore(0)), new Converter<ServicesV122Entry, LinkInfo>() {
                @Override
                public LinkInfo convert(ServicesV122Entry from) {
                    return new LinkInfo(
                            equalTo(getTranslation("home", "tabs", from.getId(), Language.EN).trim()),
                            startsWith(normalizeUrl((from.getHref()))));
                }
            }
    );

    public static String normalizeUrl(String url) {
        if (url.startsWith("//")) {
            url = CONFIG.getProtocol() + ":" + url;
        }
        return url;
    }
}
