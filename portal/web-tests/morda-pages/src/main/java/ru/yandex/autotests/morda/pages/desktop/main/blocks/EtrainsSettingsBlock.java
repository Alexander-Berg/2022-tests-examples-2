package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.junit.Assert;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.SettingsSelect;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.WidgetSetupPopup;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Select;

import static ru.yandex.autotests.morda.steps.WebElementSteps.clickOn;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldNotSee;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;

/**
 * Created by asamar on 18.01.16.
 */
@Name("Настройки электричек")
@FindBy(xpath = "//div[@class='b-widget-settings__form']")
public class EtrainsSettingsBlock extends WidgetSetupPopup{

    @Name("Кнопка \"Сохранить настройки \"")
    @FindBy(xpath = "//input[contains(@id, 'save-settings')]")
    public HtmlElement saveSettingsButton;

    @Name("Кнопка \"Закрыть \"")
    @FindBy(xpath = "//input[contains(@class, 'b-widget-settings__button')][2]")
    public HtmlElement closeSettingsButton;

    @Name("Кнопка \"Сброс настроек\"")
    @FindBy(xpath = "//input[contains(@id, 'clear-settings')]")
    public HtmlElement resetSettingsButton;

    @Name("Селектор города")
    @FindBy(xpath = "//select[@name='rasp_city']")
    public Select citySelector;

    @Name("Селектор направления")
    @FindBy(xpath = "//select[@name='rasp_direction']")
    public Select directionSelector;

    @Name("Селектор станции отправления")
    @FindBy(xpath = "//select[@name='rasp_from']")
    public Select fromStationSelector;

    @Name("Селектор станции прибытия")
    @FindBy(xpath = "//select[@name='rasp_to']")
    public Select toStationSelectorSelector;

    @Name("Селектор количества электричек")
    @FindBy(xpath = "//select[@name='n']")
    public Select etrainsNumberSelector;

    @Step("In \"{0}\" select element number {1}")
    public void selectOption(Select select, int pos) {
        try {
            select.selectByIndex(pos);
        } catch (NoSuchElementException var4) {
            Assert.fail(var4.getMessage());
        }

    }

    @Step("Close widget settings")
    @Override
    public void close() {
        shouldSee(close);
        clickOn(close);
        shouldNotSee(this);
    }

    @Step("Reset widget settings")
    @Override
    public void reset() {
        shouldSee(resetSettingsButton);
        shouldSee(resetSettingsButton);
        clickOn(resetSettingsButton);
        shouldNotSee(this);
    }

    @Step("Cancel widget settings")
    @Override
    public void cancel() {
        shouldSee(closeSettingsButton);
        shouldSee(closeSettingsButton);
        clickOn(closeSettingsButton);
        shouldNotSee(this);
    }

    @Step("Save widget settings")
    @Override
    public void save() {
        shouldSee(saveSettingsButton);
        shouldSee(saveSettingsButton);
        clickOn(saveSettingsButton);
        shouldNotSee(this);
    }

}
