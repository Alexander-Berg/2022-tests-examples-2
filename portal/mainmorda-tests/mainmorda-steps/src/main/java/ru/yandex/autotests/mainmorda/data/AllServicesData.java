package ru.yandex.autotests.mainmorda.data;

import ch.lambdaj.function.convert.Converter;
import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.utils.Service;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesAllEntry;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;

import java.text.Collator;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import static ch.lambdaj.Lambda.convert;
import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.isIn;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_ALL;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.COMPANY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.HELP;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.language.TankerManager.HOME;

public class AllServicesData {
    private static final Properties CONFIG = new Properties();

    public static final List<String> ALL_BIG_SERVICES = extract(
            exports(SERVICES_V12_2,
                    domain(CONFIG.getBaseDomain()),
                    having(on(ServicesV122Entry.class).getAllBig(), greaterThan(0)),
                    having(on(ServicesV122Entry.class).getAllBig(), not(equalTo(101)))
            ),
            on(ServicesV122Entry.class).getId()
    );

    public static final List<String> TOP_BIG_SERVICES = extract(
            exports(SERVICES_ALL,
                    domain(CONFIG.getBaseDomain()),
                    having(on(ServicesAllEntry.class).getContent(), equalTo("big")),
                    having(on(ServicesAllEntry.class).getGroup(), equalTo("top")),
                    having(on(ServicesAllEntry.class).getId(), isIn(ALL_BIG_SERVICES))
            ),
            on(ServicesAllEntry.class).getId()
    );

    public static final List<String> BOTTOM_BIG_SERVICES = extract(
            exports(SERVICES_ALL,
                    domain(CONFIG.getBaseDomain()),
                    having(on(ServicesAllEntry.class).getContent(), equalTo("big")),
                    having(on(ServicesAllEntry.class).getGroup(), equalTo("bottom")),
                    having(on(ServicesAllEntry.class).getId(), isIn(ALL_BIG_SERVICES))
            ),
            on(ServicesAllEntry.class).getId()
    );

    public static final List<String> SPECIAL_BIG_SERVICES = extract(
            exports(SERVICES_ALL,
                    domain(CONFIG.getBaseDomain()),
                    having(on(ServicesAllEntry.class).getContent(), equalTo("big")),
                    having(on(ServicesAllEntry.class).getGroup(), equalTo("special"))
            ),
            on(ServicesAllEntry.class).getId()
    );

    public static List<Service> getAllServicesList() {
        return convert(ALL_BIG_SERVICES,
                new Converter<String, Service>() {
                    @Override
                    public Service convert(String id) {
                        ServicesV122Entry entry = export(SERVICES_V12_2,
                                domain(CONFIG.getBaseDomain()),
                                having(on(ServicesV122Entry.class).getId(), equalTo(id))

                        );
                        return new Service(entry);
                    }
                }
        );
    }

    public static List<Service> getTopServicesList() {
        return convert(TOP_BIG_SERVICES,
                new Converter<String, Service>() {

                    @Override
                    public Service convert(String id) {
                        ServicesV122Entry entry = export(SERVICES_V12_2,
                                domain(CONFIG.getBaseDomain()),
                                having(on(ServicesV122Entry.class).getId(), equalTo(id))
                        );
                        return new Service(entry);
                    }
                }
        );
    }

    public static List<Service> getSpecialServicesList() {
        SPECIAL_BIG_SERVICES.remove("large");
        return convert(SPECIAL_BIG_SERVICES,
                new Converter<String, Service>() {

                    @Override
                    public Service convert(String id) {
                        ServicesV122Entry entry = export(SERVICES_V12_2,
                                domain(CONFIG.getBaseDomain()),
                                having(on(ServicesV122Entry.class).getId(), equalTo(id))
                        );
                        return new Service(entry);
                    }
                }
        );
    }

    public static List<Service> getBottomServicesList() {
        return convert(BOTTOM_BIG_SERVICES,
                new Converter<String, Service>() {

                    @Override
                    public Service convert(String id) {
                        ServicesV122Entry entry = export(SERVICES_V12_2,
                                domain(CONFIG.getBaseDomain()),
                                having(on(ServicesV122Entry.class).getId(), equalTo(id))
                        );
                        return new Service(entry);
                    }
                }
        );
    }

    public static final LinkInfo LOGO_LINK = new LinkInfo(
            isEmptyOrNullString(),
            equalTo(CONFIG.getBaseURL() + "/")
    );

    public static final LinkInfo MOBILE_APPS_LINK = new LinkInfo(
            equalTo(getTranslation(HOME, "home", "everything", "tabs.mobile", CONFIG.getLang())),
            equalTo(CONFIG.getProtocol() + "://mobile.yandex.ru/")
    );

    public static final Matcher<String> PC_PROGRAMS_TEXT_MATCHER =
            equalTo(getTranslation(HOME, "home", "everything", "tabs.pc", CONFIG.getLang()));

    public static final LinkInfo HELP_LINK = new LinkInfo(
            equalTo(getTranslation(HOME, HELP, CONFIG.getLang())),
            equalTo(CONFIG.getProtocol() + "://yandex.ru/support/")
    );

    public static final LinkInfo COMPANY_LINK = new LinkInfo(
            equalTo(getTranslation(HOME, COMPANY, CONFIG.getLang())),
            equalTo(CONFIG.getProtocol() + "://yandex.ru/company")
    );

    public static final LinkInfo YANDEX_LINK = new LinkInfo(
            equalTo(getTranslation(HOME, "home", "everything", "ogmeta.name", CONFIG.getLang())),
            equalTo(CONFIG.getProtocol() + "://www.yandex" + CONFIG.getBaseDomain() + "/")
    );

    private static final Map<Language, Locale> LOCALES = new HashMap<Language, Locale>() {{
        put(RU, new Locale("ru", "RU"));
        put(UK, new Locale("uk", "UA"));
        put(KK, new Locale("kk", "KZ"));
        put(BE, new Locale("be", "BY"));
        put(TT, new Locale("ru", "RU"));
    }};

    private static final Collator COLLATOR = Collator.getInstance(LOCALES.get(CONFIG.getLang()));

    private static final Comparator<String> SERVICE_ORDER = new Comparator<String>() {
        @Override
        public int compare(String name1, String name2) {
            name1 = name1.replaceAll("\\.", " ");
            name2 = name2.replaceAll("\\.", " ");
            return COLLATOR.compare(name1, name2);
        }
    };

    public static List<String> getExpectedAllOrder() {
        List<String> sorted = extract(getAllServicesList(), on(Service.class).getServiceName());
        Collections.sort(sorted, SERVICE_ORDER);
        return sorted;
    }
}