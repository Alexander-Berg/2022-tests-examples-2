package ru.yandex.autotests.morda.tests.afisha.cleanvars;

import org.apache.log4j.Logger;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.afisha.AfishaEvent;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.attach.AttachmentUtils;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.collection.IsCollectionWithSize.hasSize;
import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.AFISHA;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.geobase.regions.Russia.MOSCOW;

/**
 * User: asamar
 * Date: 28.12.16
 */
@Aqua.Test(title = "Genre")
@Features({MordaTestTags.CLEANVARS, MordaTestTags.AFISHA})
@RunWith(Parameterized.class)
public class AfishaGenreTest {
    private static MordaTestsProperties CONFIG = new MordaTestsProperties();
    private static final Logger LOGGER = Logger.getLogger(AfishaGenreTest.class);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        data.add(desktopMain(CONFIG.pages().getEnvironment()).region(MOSCOW).language(RU));
        data.add(touchMain(CONFIG.pages().getEnvironment()).region(MOSCOW).language(RU));

        return data;
    }

    public AfishaGenreTest(Morda<?> morda) {
        this.morda = morda;
    }

    @Rule
    public AllureLoggingRule loggingRule = new AllureLoggingRule();
    private Morda<?> morda;
    private MordaCleanvars cleanvars;

    @Before
    public void init() {
        this.cleanvars = new MordaClient().cleanvars(morda, AFISHA).read();
        AttachmentUtils.attachJson("afisha.cleanvars", cleanvars);
    }

    @Test
    public void afishaGenreTest() {
        List<AfishaEvent> withGenre = cleanvars.getAfisha().getEvents().stream()
                .filter(e -> e.getGenre() != null && !"".equals(e.getGenre()))
                .collect(toList());
        LOGGER.info("Событий с жанром " + withGenre.size());
        assertThat("Должно быть минимум 2 события с жанром", withGenre, hasSize(greaterThanOrEqualTo(2)));
    }
}
