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
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithVirtualKeyboard;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encode;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encodeRequest;

/**
 * User: eoff
 * Date: 22.01.13
 */
@Aqua.Test(title = "Virtual Keyboard")
@Features("Virtual Keyboard")
@Stories("View")
@RunWith(Parameterized.class)
public class VirtualKeyboardTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;

    private WebDriver driver;
    private CommonMordaSteps user;
    private VirtualKeyboardSteps userKeyboard;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        List<Morda<? extends PageWithSearchBlock<? extends BlockWithVirtualKeyboard<VirtualKeyboardBlock>>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));
        data.addAll(Com404Morda.getDefaultList(scheme, environment));
//        data.add(desktopFirefoxRu(scheme, environment, Region.MOSCOW, Language.RU));
//        data.add(desktopFirefoxUa(scheme, environment, Region.KIEV, Language.UK));
//        data.add(desktopFirefoxComTr(scheme, environment, Region.IZMIR));
        data.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private final Morda<? extends PageWithSearchBlock<? extends BlockWithVirtualKeyboard<VirtualKeyboardBlock>>> morda;
    private final PageWithSearchBlock<? extends BlockWithVirtualKeyboard<VirtualKeyboardBlock>> page;

    public VirtualKeyboardTest(
            Morda<? extends PageWithSearchBlock<? extends BlockWithVirtualKeyboard<VirtualKeyboardBlock>>> morda)
    {
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
    public void keyboardAppears() {
        user.shouldSeeElement(page.getSearchBlock());
        user.shouldSeeElement(page.getSearchBlock().getVirtualKeyboardButton());
        user.clicksOn(page.getSearchBlock().getVirtualKeyboardButton());

        VirtualKeyboardBlock keyboard = page.getSearchBlock().getVirtualKeyboardBlock();

        user.shouldSeeElement(keyboard);
        user.shouldSeeElementWithText(keyboard.switcher, VirtualKeyboardData.getLanguageMatcher(morda.getLanguage()));
        user.shouldSeeElement(keyboard.close);
        user.clicksOn(keyboard.close);
        user.shouldNotSeeElement(keyboard);
    }

    @Test
    public void defaultLanguage() {
        user.shouldSeeElement(page.getSearchBlock());
        user.shouldSeeElement(page.getSearchBlock().getVirtualKeyboardButton());
        user.clicksOn(page.getSearchBlock().getVirtualKeyboardButton());

        VirtualKeyboardBlock keyboard = page.getSearchBlock().getVirtualKeyboardBlock();

        user.shouldSeeElement(keyboard);

        userKeyboard.shouldSeeKeyboardLanguage(keyboard, VirtualKeyboardData.LANGUAGES.get(morda.getLanguage()));
    }

    @Test
    public void textAppearsInInput() {
        user.shouldSeeElement(page.getSearchBlock());
        user.shouldSeeElement(page.getSearchBlock().getVirtualKeyboardButton());
        user.clicksOn(page.getSearchBlock().getVirtualKeyboardButton());

        VirtualKeyboardBlock keyboard = page.getSearchBlock().getVirtualKeyboardBlock();

        user.shouldSeeElement(keyboard);
        String text = userKeyboard.writeRandomText(page.getSearchBlock().getSearchInput(), keyboard);
        user.shouldSeeInputWithText(page.getSearchBlock().getSearchInput(), equalTo(text));
    }

    @Test
    public void requestThrownWhenEnterPressed() {
        user.shouldSeeElement(page.getSearchBlock());
        user.shouldSeeElement(page.getSearchBlock().getVirtualKeyboardButton());
        user.clicksOn(page.getSearchBlock().getVirtualKeyboardButton());

        VirtualKeyboardBlock keyboard = page.getSearchBlock().getVirtualKeyboardBlock();

        user.shouldSeeElement(keyboard);

        String text = userKeyboard.writeRandomText(page.getSearchBlock().getSearchInput(), keyboard);
        user.shouldSeeInputWithText(page.getSearchBlock().getSearchInput(), equalTo(text));

        user.shouldSeeElement(keyboard.enter);
        user.clicksOn(keyboard.enter);

        user.shouldSeePage(allOfDetailed(
                startsWith(morda.getSerpUrl().toString()),
                anyOf(
                        containsString(encodeRequest(text)),
                        containsString(encode(text))
                )
        ));
    }
}
