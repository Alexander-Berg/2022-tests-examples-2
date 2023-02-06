package ru.yandex.autotests.mainmorda.utils;

import org.hamcrest.Matcher;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.language.Language;

import java.text.Collator;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.04.13
 */
public class Rubric {
    private static final Properties CONFIG = new Properties();

    protected static final Map<Language, Collator> COLLATORS = new HashMap<Language, Collator>() {{
        put(Language.RU, Collator.getInstance(new Locale("ru", "RU")));
        put(Language.UK, Collator.getInstance(new Locale("uk", "UA")));
        put(Language.KK, Collator.getInstance(new Locale("kk", "KZ")));
        put(Language.BE, Collator.getInstance(new Locale("be", "BY")));
        put(Language.TT, null);
    }};

    private static final Collator COLLATOR = COLLATORS.get(CONFIG.getLang());
    public Matcher<String> name;
    public LinkInfo linkInfo;
    public List<Service> services;
    public List<Service> sortedServices;

    private static final Comparator<Service> SERVICE_ORDER = new Comparator<Service>() {
        @Override
        public int compare(Service o1, Service o2) {
            String name1 = o1.serviceName.replaceAll("[\\.«»]", " ");
            String name2 = o2.serviceName.replaceAll("[\\.«»]", " ");
            if (COLLATOR == null) {
                return -1;
            }
            return COLLATOR.compare(name1, name2);
        }
    };

    public Rubric(List<Service> services) {
        this.services = services;
        this.sortedServices = new ArrayList<Service>(services);
        Collections.sort(sortedServices,SERVICE_ORDER);
        if (sortedServices.get(0).serviceName.equals("XML")) {
            Service xml = sortedServices.get(0);
            sortedServices.remove(0);
            sortedServices.add(xml);
        }
        System.out.println(sortedServices);
    }
}
