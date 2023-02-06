package ru.yandex.autotests.mordamobile.data;

import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.ATBASAR;
import static ru.yandex.autotests.utils.morda.region.Region.BORISPOL;
import static ru.yandex.autotests.utils.morda.region.Region.ORSHA;
import static ru.yandex.autotests.utils.morda.region.Region.VYBORG;

/**
 * User: ivannik
 * Date: 10.09.2014
 */
public class EtrainsData {
    private static final Properties CONFIG = new Properties();

    public static final List<Region> ETRAINS_REGIONS = Arrays.asList(VYBORG, BORISPOL, ORSHA, ATBASAR);

    public static LinkInfo getEtrainsTitleLink(Region region) {
        return new LinkInfo(
                equalTo(getTranslation("home", "etrain", "shortTitle", CONFIG.getLang())),
                startsWith(String.format("https://t.rasp.yandex%s/", region.getDomain().equals(Domain.UA) ? Domain.UA : Domain.RU)),
                hasAttribute(HREF, equalTo("https://t.rasp.yandex.ru/")));
    }

    public static LinkInfo getEtrainsRaspLink(Region region) {
        return new LinkInfo(
            equalTo(getTranslation("home", "etrain", "checkSchedule", CONFIG.getLang())),
            startsWith(String.format("https://t.rasp.yandex%s/thread/", region.getDomain().equals(Domain.UA) ? Domain.UA : Domain.RU)),
            hasAttribute(HREF, startsWith("https://t.rasp.yandex.ru/thread/")));
    }
}
