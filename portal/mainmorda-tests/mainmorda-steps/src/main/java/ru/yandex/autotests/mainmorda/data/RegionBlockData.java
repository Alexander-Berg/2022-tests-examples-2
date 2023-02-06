package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordacommonsteps.annotations.DomainDependent;
import ru.yandex.autotests.mordacommonsteps.loader.DataLoader;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.RegBlock.REGBLOCK_RESTORE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.*;

/**
 * User: eoff
 * Date: 29.11.12
 */
public class RegionBlockData {
    private static final Properties CONFIG = new Properties();

    static {
        DataLoader.populate(RegionBlockData.class, CONFIG.getBaseDomain());
    }

    private static final List<Region> RU = Arrays.asList(SANKT_PETERBURG, PETROZAVODSK, KAZAN);
    private static final List<Region> UA = Arrays.asList(KIEV, DONECK, ODESSA);
    private static final List<Region> BY = Arrays.asList(MINSK, VITEBSK, GRODNO);
    private static final List<Region> KZ = Arrays.asList(ASTANA, ALMATY, KARAGANDA);
    private static final Matcher<String> LINK_HREF_PATTERN = matches(CONFIG.getBaseURL() + "/[?]add=[0-9]*[&]from=.*");
    private static final Matcher<String> ALL_LINK_COUNTRY_HREF_PATTERN =
            matches(String.format("http://widgets.yandex%s/[?]region=[0-9]*[&]from=.*", CONFIG.getBaseDomain()));

    @DomainDependent(pattern = "http://yaca.yandex%s/yca/geo/", kz = Domain.RU)
    public static String ALL_LINK_REGION_HREF_BASE_PATTERN;
    private static final Matcher<String> ALL_LINK_REGION_HREF_PATTERN = startsWith(ALL_LINK_REGION_HREF_BASE_PATTERN);


    private static final Map<Domain, List<Region>> TEST_CASES_MAP = new HashMap<Domain, List<Region>>() {{
        put(Domain.RU, RU);
        put(Domain.UA, UA);
        put(Domain.KZ, KZ);
        put(Domain.BY, BY);
    }};

    public static final List<Region> TEST_CASES = TEST_CASES_MAP.get(CONFIG.getBaseDomain());

    public static final LinkInfo LINK = new LinkInfo(
            not(isEmptyOrNullString()),
            equalTo(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.HREF, LINK_HREF_PATTERN)
    );

    public static final LinkInfo ALL_LINK_COUNTRY = new LinkInfo(
            not(isEmptyOrNullString()),
            equalTo(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.HREF, ALL_LINK_COUNTRY_HREF_PATTERN)
    );

    public static final LinkInfo ALL_LINK_REGION = new LinkInfo(
            not(isEmptyOrNullString()),
            equalTo(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.HREF, ALL_LINK_REGION_HREF_PATTERN)
    );


    public static final Matcher<String> RESTORE_TEXT = equalTo(getTranslation(REGBLOCK_RESTORE, CONFIG.getLang()));
}
