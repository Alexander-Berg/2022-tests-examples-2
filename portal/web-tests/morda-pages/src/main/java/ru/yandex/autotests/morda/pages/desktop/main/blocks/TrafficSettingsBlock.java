package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.WidgetSetupPopup;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.TextInput;

/**
 * User: asamar
 * Date: 01.03.16
 */
@Name("Окно настройки Пробок")
public class TrafficSettingsBlock extends WidgetSetupPopup {

    @Name("Фрейм")
    @FindBy(xpath = ".//iframe")
    public HtmlElement iframe;

    @Name("Дом")
    @FindBy(xpath = "//input[@id='router-home-addr']")
    public TextInput home;

    @Name("Работа")
    @FindBy(xpath = "//input[@id='router-work-addr']")
    public TextInput work;

    //li[contains(@class, 'geosuggest_item')]

    @Name("Сохранить")
    @FindBy(xpath = "//button[contains(@class, 'b-saveall')]")
    public HtmlElement save;


    @Step("Save widget settings")
    public void s(){
//        clickOn(save);
//        shouldSee(save);
        save.click();
    }
}
