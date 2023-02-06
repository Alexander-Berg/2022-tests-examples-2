package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.Random;

import static ch.lambdaj.function.matcher.OrMatcher.or;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mainmorda.data.EtrainsSettingsData.FROM_TO_ARROW;
import static ru.yandex.autotests.mainmorda.data.EtrainsSettingsData.NUMBER_TEXT;
import static ru.yandex.autotests.mainmorda.data.EtrainsSettingsData.Route;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.exists;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.isDisplayed;


/**
 * User: eoff
 * Date: 14.01.13
 */
public class EtrainsSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private ModeSteps modeSteps;
    private MainPage mainPage;

    public EtrainsSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.modeSteps = new ModeSteps(driver);
        this.mainPage = new MainPage(driver);
    }

    @Step
    public void shouldSeeNumberSelectText() {
        int size = mainPage.etrainsSettings.number.getOptionsAsHtmlElements().size();
        for (int i = 0; i != size; i++) {
            userSteps.shouldSeeElementWithText(mainPage.etrainsSettings.number
                    .getOptionsAsHtmlElements().get(i), equalTo(NUMBER_TEXT.get(i)));
        }
    }

    @Step
    public void switchToEtrainsFrame() {
        driver.switchTo().frame(driver.findElement(By.xpath("//iframe[contains(@id,'wd-prefs-_etrains-')]")));
    }

    @Step
    public void switchToDefaultContent() {
        driver.switchTo().defaultContent();
    }

    @Step
    public Route randomlyFillEtrainsSettings() {
        boolean success = false;
        Route route = new Route();
        while (!success) {
            userSteps.selectRandomOption(mainPage.etrainsSettings.city, 1);
            userSteps.shouldNotSeeElement(mainPage.etrainsSettings.okButton);
            userSteps.selectRandomOption(mainPage.etrainsSettings.direction, 1);
            Random random = new Random();
            int from = random.nextInt(mainPage.etrainsSettings.from.getOptions().size() - 1) + 1;
            int size = mainPage.etrainsSettings.to.getOptions().size();
            int to = getDifferentInt(from, random, size);
            userSteps.selectOption(mainPage.etrainsSettings.from, from);
            userSteps.selectOption(mainPage.etrainsSettings.to, to);
            route.from = mainPage.etrainsSettings.from.getFirstSelectedOption()
                    .getText();
            route.to = mainPage.etrainsSettings.to.getFirstSelectedOption()
                    .getText();
            userSteps.shouldSeeElement(mainPage.etrainsSettings.okButton);
            userSteps.clicksOn(mainPage.etrainsSettings.okButton);
            if (isFilledSuccessfully()) {
                success = true;
            }
        }
        return route;
    }

    private int getDifferentInt(int prevInt, Random random, int size) {
        int newInt;
        do {
            newInt = random.nextInt(size - 1) + 1;
        } while (newInt == prevInt);
        return newInt;
    }

    private boolean isFilledSuccessfully() {
        withWaitFor(allOf(exists(), isDisplayed())).matches(mainPage.etrainsSettings.noRoutes);
        return !mainPage.etrainsSettings.noRoutes.isDisplayed();
    }

    @Step
    public void routeTextMatches(String from, String to) {
        if (to.contains("(")) {
            userSteps.shouldSeeElementWithText(mainPage.etrainsBlock.direction,
                    or(equalTo(from + FROM_TO_ARROW +
                            to.substring(to.indexOf("(") + 1, to.indexOf(")"))),
                            equalTo(from + FROM_TO_ARROW + to)));
        } else {
            userSteps.shouldSeeElementWithText(mainPage.etrainsBlock.direction,
                    equalTo(from + FROM_TO_ARROW + to));
        }
    }

    @Step
    public void resetButtonWorks() {
        String cityDefault = mainPage.etrainsSettings.city.getFirstSelectedOption().getText();
        String directionDefault = mainPage.etrainsSettings.direction.getFirstSelectedOption()
                .getText();
        String fromDefault = mainPage.etrainsSettings.from.getFirstSelectedOption().getText();
        String toDefault = mainPage.etrainsSettings.to.getFirstSelectedOption().getText();
        String numberDefault = mainPage.etrainsSettings.number.getFirstSelectedOption().getText();
        randomlyFillEtrainsSettings();
        switchToDefaultContent();
        modeSteps.saveSettings();
        modeSteps.setEditMode(CONFIG.getBaseURL());
        userSteps.clicksOn(mainPage.etrainsBlock.editIcon);
        switchToEtrainsFrame();
        userSteps.clicksOn(mainPage.etrainsSettings.resetSettingsButton);
        switchToDefaultContent();
        modeSteps.saveSettings();
        modeSteps.setEditMode(CONFIG.getBaseURL());
        userSteps.clicksOn(mainPage.etrainsBlock.editIcon);
        switchToEtrainsFrame();
        userSteps.shouldSeeElementWithText(mainPage.etrainsSettings.city
                .getFirstSelectedOptionAsHtmlElement(), equalTo(cityDefault));
        userSteps.shouldSeeElementWithText(mainPage.etrainsSettings.direction
                .getFirstSelectedOptionAsHtmlElement(), equalTo(directionDefault));
        userSteps.shouldSeeElementWithText(mainPage.etrainsSettings.from
                .getFirstSelectedOptionAsHtmlElement(), equalTo(fromDefault));
        userSteps.shouldSeeElementWithText(mainPage.etrainsSettings.to
                .getFirstSelectedOptionAsHtmlElement(), equalTo(toDefault));
        userSteps.shouldSeeElementWithText(mainPage.etrainsSettings.number
                .getFirstSelectedOptionAsHtmlElement(), equalTo(numberDefault));
    }
}

