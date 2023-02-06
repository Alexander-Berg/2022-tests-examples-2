package ru.yandex.autotests.morda.tests.web.common.tuneapi;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.net.URI;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static ru.yandex.autotests.morda.pages.MordaType.T_RU;
import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;

/**
 * User: asamar
 * Date: 29.06.16
 */
@Aqua.Test(title = "Language Api Test")
@Features("Tune")
@Stories("Set Language Test")
@RunWith(Parameterized.class)
public class TuneLanguageApiTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private Morda<?> morda;
    private URI uri;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<?>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();
        String userAgentTouchWp = CONFIG.getMordaUserAgentTouchWp();
        String userAgentPda = CONFIG.getMordaUserAgentPda();



        data.addAll(TouchRuMorda.getDefaultList(scheme, environment, userAgentTouchIphone));
        data.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));
        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));
        data.add(touchComTr(scheme, environment, ISTANBUL, userAgentTouchIphone));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    public TuneLanguageApiTest(Morda<?> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
    }

    @Before
    public void init() {
        this.uri = morda.getUrl();
        if (morda.getMordaType() == T_RU) {
            uri = fromUri(morda.getUrl()).queryParam("mda", "0").build();
        }
        NavigationSteps.open(driver, uri);
    }

    @Test
    public void setLanguageTest() {
        TuneSteps.setLanguageNewTune(driver, uri, morda.getCookieDomain(), morda.getLanguage());
    }

}
