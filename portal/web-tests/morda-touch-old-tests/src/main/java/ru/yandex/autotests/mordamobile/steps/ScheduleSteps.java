package ru.yandex.autotests.mordamobile.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordamobile.blocks.ScheduleBlock.ScheduleItem;
import static ru.yandex.autotests.mordamobile.data.ScheduleData.ScheduleInfo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class ScheduleSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private HomePage homePage;
    public CommonMordaSteps userSteps;

    public ScheduleSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        homePage = new HomePage(driver);
    }

    @Step
    public ScheduleItem findScheduleItemOnPage(List<ScheduleItem> list, ScheduleInfo scheduleInfo) {
        for (ScheduleItem element : list) {
            System.out.println(element.getText());
            if (scheduleInfo.getText(CONFIG.getLang()).matches(element.getText())) {
                return element;
            }
        }
        fail("не найден элемент расписания " + scheduleInfo.getText(CONFIG.getLang()));
        return null;
    }

    @Step
    public void shouldSeeScheduleItem(ScheduleInfo scheduleInfo) {
        ScheduleItem element = findScheduleItemOnPage(homePage.scheduleBlock.allItems, scheduleInfo);
        if (element != null) {
            userSteps.shouldSeeElement(element.icon);
            userSteps.shouldSeeElementMatchingTo(element.icon, scheduleInfo.getIconMatcher());
            userSteps.shouldSeeLink(element, scheduleInfo.getLing(CONFIG.getLang()));
        }
    }
}
