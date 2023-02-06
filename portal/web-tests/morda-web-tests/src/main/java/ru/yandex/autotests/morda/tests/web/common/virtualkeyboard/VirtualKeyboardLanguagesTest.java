package ru.yandex.autotests.morda.tests.web.common.virtualkeyboard;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.common.blocks.VirtualKeyboardBlock;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.com404.Com404Morda;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithVirtualKeyboard;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;

/**
 * User: eoff
 * Date: 11.03.13
 */
@Aqua.Test(title = "Virtual Keyboard Language Switching")
@RunWith(Parameterized.class)
@Features("Virtual Keyboard")
@Stories("Languages")
public class VirtualKeyboardLanguagesTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;

    private WebDriver driver;
    private CommonMordaSteps user;
    private VirtualKeyboardSteps userKeyboard;

    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> testData() {
        List<Morda<? extends PageWithSearchBlock<? extends BlockWithVirtualKeyboard<VirtualKeyboardBlock>>>> mordas = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        mordas.add(desktopMain(scheme, environment, Region.MOSCOW, Language.RU));
        mordas.add(desktopMain(scheme, environment, Region.KIEV, Language.UK));
//        mordas.add(desktopFirefoxRu(scheme, environment, Region.MOSCOW, Language.RU));
//        mordas.add(desktopFirefoxUa(scheme, environment, Region.KIEV, Language.UK));
//        mordas.add(desktopFirefoxComTr(scheme, environment, Region.IZMIR));
        mordas.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));
        mordas.addAll(DesktopComMorda.getDefaultList(scheme, environment));
        mordas.addAll(Com404Morda.getDefaultList(scheme,environment));
        mordas = MordaType.filter(mordas, CONFIG.getMordaPagesToTest());

        List<Object[]> data = new ArrayList<>();

        for (String lang : VirtualKeyboardData.LANGUAGE_SWITCHER.keySet()) {
            for (Morda<?> m : mordas) {
                data.add(new Object[]{m, lang});
            }
        }
        return data;
    }

    private final Morda<? extends PageWithSearchBlock<? extends BlockWithVirtualKeyboard<VirtualKeyboardBlock>>> morda;
    private final String language;
    private final PageWithSearchBlock<? extends BlockWithVirtualKeyboard<VirtualKeyboardBlock>> page;

    public VirtualKeyboardLanguagesTest(
            Morda<? extends PageWithSearchBlock<? extends BlockWithVirtualKeyboard<VirtualKeyboardBlock>>> morda,
            String language)
    {
        this.language = language;
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.page = morda.getPage(driver);
        this.user = new CommonMordaSteps(driver);
        this.userKeyboard = new VirtualKeyboardSteps(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
    }

    @Test
    public void allLanguages() {
        user.shouldSeeElement(page.getSearchBlock());
        user.shouldSeeElement(page.getSearchBlock().getVirtualKeyboardButton());
        user.clicksOn(page.getSearchBlock().getVirtualKeyboardButton());

        VirtualKeyboardBlock keyboard = page.getSearchBlock().getVirtualKeyboardBlock();

        user.shouldSeeElement(keyboard);
        user.shouldSeeElement(keyboard.switcher);
        user.clicksOn(keyboard.switcher);
        user.shouldSeeElement(keyboard.allLanguagesPopup);
        userKeyboard.setKeyboardLanguage(keyboard, language);
        userKeyboard.shouldSeeKeyboardLanguage(keyboard, language);
    }
}
