package ru.yandex.autotests.mordabackend.example;

import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static ru.yandex.autotests.utils.morda.language.Language.*;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.region.Region.*;
import static ru.yandex.autotests.utils.morda.region.Region.MERSIN;

/**
 * User: ivannik
 * Date: 05.08.2014
 */
public class SearchExampleUtils {

    public static final List<Region> EXAMPLE_REGIONS_MAIN = Arrays.asList(
            MOSCOW, KIEV, SANKT_PETERBURG, MINSK, EKATERINBURG, PERM,
            SAMARA, CHELYABINSK, NOVOSIBIRSK, DUBNA, ASTANA, ALMATY,
            VLADIVOSTOK, UFA, YAROSLAVL, HARKOV, DNEPROPETROVSK, KAZAN
    );

    public static final List<Region> EXAMPLE_REGIONS_TR = Arrays.asList(
            ISTANBUL, BURSA, ALANYA, ANTALYA, IZMIR, ADANA, GAZIANTEP, MERSIN
    );

    public static final List<Region> EXAMPLE_REGIONS_ALL = new ArrayList<>();
    static {
        EXAMPLE_REGIONS_ALL.addAll(EXAMPLE_REGIONS_MAIN);
        EXAMPLE_REGIONS_ALL.addAll(EXAMPLE_REGIONS_TR);
    }

    public static final List<Language> LANGUAGES = Arrays.asList(RU, UK, BE, KK, TT);

    public static final List<String> EXAMPLES_SOURCE_EXPORTS = Arrays.asList("examples", "examples_interests");
}
