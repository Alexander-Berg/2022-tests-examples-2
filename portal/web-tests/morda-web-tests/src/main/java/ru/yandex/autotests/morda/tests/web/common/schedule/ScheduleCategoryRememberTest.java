package ru.yandex.autotests.morda.tests.web.common.schedule;

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
import ru.yandex.autotests.morda.pages.touch.ru.blocks.ScheduleBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.steps.NavigationSteps.*;
import static ru.yandex.autotests.morda.tests.web.utils.GeoLocation.SPB_FONTANKA;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: asamar
 * Date: 24.01.16
 */
@Aqua.Test(title = "Schedule Category Remember")
@Features("Schedule")
@Stories("Schedule Category Remember")
@RunWith(Parameterized.class)
public class ScheduleCategoryRememberTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String useragentTouch = CONFIG.getMordaUserAgentTouchIphone();

        List<TouchRuMorda> data = new ArrayList<>();

        data.add(TouchRuMorda.touchRu(scheme, environment, useragentTouch, SPB_FONTANKA.getRegion(),
                SPB_FONTANKA.getCoordinates().getLat(),
                SPB_FONTANKA.getCoordinates().getLon(),
                Language.RU));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private TouchRuMorda morda;
    private TouchRuPage page;

    public ScheduleCategoryRememberTest(TouchRuMorda morda) {
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
    public void rememberCategoryAfterRefresh() throws InterruptedException {
        ScheduleBlock scheduleBlock = page.getScheduleBlock();
        Thread.sleep(1000);
        scheduleBlock.setSecondCategory();
        scheduleBlock.shouldBeSelectedSecondCategory();
        refresh(driver);
        scheduleBlock.shouldBeSelectedSecondCategory();
    }

    @Test
    public void rememberCategoryAfterComeBack() throws InterruptedException {
        ScheduleBlock scheduleBlock = page.getScheduleBlock();
        Thread.sleep(1000);
        scheduleBlock.setSecondCategory();
        scheduleBlock.shouldBeSelectedSecondCategory();
        open(driver, "https://www.google.ru");
        returnBack(driver);
        scheduleBlock.shouldBeSelectedSecondCategory();
    }
}
