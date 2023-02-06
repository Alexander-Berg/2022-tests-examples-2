package ru.yandex.autotests.morda.tests.web.common.search;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.RemoteWebElement;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.com404.Com404Morda;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopFamilyComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopFamilyMain;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda.desktopYaru;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Search input autofocus")
@Features("Search")
@Stories("Search input autofocus")
@RunWith(Parameterized.class)
public class SearchAutofocusTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.add(desktopMain(scheme, environment, MOSCOW));
        data.add(desktopFamilyMain(scheme, environment, MOSCOW));

        data.add(desktopYaru(scheme, environment));

        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));
        data.addAll(Com404Morda.getDefaultList(scheme, environment));

//        data.add(desktopFirefoxRu(scheme, environment, MOSCOW, Language.RU));
//        data.add(desktopFirefoxUa(scheme, environment, MOSCOW, Language.RU));
//        data.add(desktopFirefoxComTr(scheme, environment, MOSCOW));
        data.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));

        data.add(desktopComTr(scheme, environment));
        data.add(desktopFamilyComTr(scheme, environment));

        data.add(desktopComTrBjk(scheme, environment));
        data.add(desktopComTrGs(scheme, environment));
        data.add(desktopFamilyComTrGs(scheme, environment));
        data.add(desktopFamilyComTrBjk(scheme, environment));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>> morda;
    private PageWithSearchBlock<? extends BlockWithSearchForm> page;

    public SearchAutofocusTest(Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Test
    public void inputIsFocused() throws InterruptedException {
        morda.initialize(driver);
        user.shouldSeeElement(page.getSearchBlock());
        user.shouldSeeElement(page.getSearchBlock().getSearchInput());
        shouldSeeInputFocused();
    }

    @Step("Should see input focused")
    private void shouldSeeInputFocused() throws InterruptedException {
        String expectedFocusedId = page.getSearchBlock().getSearchInput().getAttribute("id");
        String expectedFocusedClass = page.getSearchBlock().getSearchInput().getAttribute("class");
        RemoteWebElement actualFocusedElement = (RemoteWebElement) ((JavascriptExecutor) driver)
                .executeScript("return document.activeElement");
        assertThat("Input with id \"" + expectedFocusedId + "\" should be focused",
                actualFocusedElement.getAttribute("id"), equalTo(expectedFocusedId));
        assertThat("Input with class \"" + expectedFocusedClass + "\" should be focused",
                actualFocusedElement.getAttribute("class"), equalTo(expectedFocusedClass));
    }
}
