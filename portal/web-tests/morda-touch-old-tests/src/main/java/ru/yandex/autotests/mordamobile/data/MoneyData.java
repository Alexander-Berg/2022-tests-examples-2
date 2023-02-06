package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.utils.morda.region.Region;

import java.util.ArrayList;
import java.util.Collection;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.MONEY_RUBLES;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.MONEY_RUBLES_SHORT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tabs.MONEY;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: ivannik
 * Date: 10.01.14
 * Time: 14:18
 */
public class MoneyData {
    public static final Properties CONFIG = new Properties();

    public static final Matcher<String> MONEY_TITLE = equalTo(getTranslation(MONEY, CONFIG.getLang()));

    public static final Matcher<String> MONEY_NUM =
            matches("0 \\Q" + getTranslation(MONEY_RUBLES, CONFIG.getLang()) + "\\E");

    public static final Matcher<String> MONEY_NUM_SHORT =
            matches("0\\Q" + getTranslation(MONEY_RUBLES_SHORT, CONFIG.getLang()) + "\\E\\n ");

    public static final Collection<Object[]> MONEY_BLOCK_REGIONS = new ArrayList<Object[]>() {{
        add(new Object[]{Region.DNO, MONEY_NUM_SHORT});
        add(new Object[]{Region.NIZHNIY_NOVGOROD, MONEY_NUM});
    }};

    public static final LinkInfo MONEY_LINK = new LinkInfo(
            not(""),
            startsWith("https://m.money.yandex.ru/")
    );
}
