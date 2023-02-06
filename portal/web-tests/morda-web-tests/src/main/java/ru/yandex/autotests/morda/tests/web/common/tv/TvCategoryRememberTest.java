package ru.yandex.autotests.morda.tests.web.common.tv;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuPage;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.TvBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.steps.NavigationSteps.*;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: asamar
 * Date: 22.01.16
 */
@Aqua.Test(title = "TV Category Remember")
@Features("TV")
@Stories("TV Category Remember")
@RunWith(Parameterized.class)
public class TvCategoryRememberTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<TouchRuMorda> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String useragentTouch = CONFIG.getMordaUserAgentTouchIphone();

        data.addAll(TouchRuMorda.getDefaultList(scheme, environment, useragentTouch));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private TouchRuMorda morda;
    private TouchRuPage page;

    public TvCategoryRememberTest(TouchRuMorda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
    }

    @Test
    public void rememberCategoryAfterRefresh(){
        TvBlock tvBlock = page.getTvBlock();
        tvBlock.setSecondCategory();
        tvBlock.shouldBeSelectedSecondCategory();
        refresh(driver);
        tvBlock.shouldBeSelectedSecondCategory();
    }

    @Test
    public void rememberCategoryAfterComeBack(){
        TvBlock tvBlock = page.getTvBlock();
        tvBlock.setSecondCategory();
        tvBlock.shouldBeSelectedSecondCategory();
        open(driver, "https://www.google.ru");
        returnBack(driver);
        tvBlock.shouldBeSelectedSecondCategory();
    }
}
