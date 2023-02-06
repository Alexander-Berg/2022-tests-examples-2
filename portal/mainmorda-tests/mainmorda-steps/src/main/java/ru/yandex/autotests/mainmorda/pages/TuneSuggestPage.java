package ru.yandex.autotests.mainmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.CheckBox;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff
 * Date: 11.12.12
 */
public class TuneSuggestPage {
    public TuneSuggestPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Чекбокс включения/выключения саджеста")
    @FindBy(xpath = "//span[contains(@class,'checkbox_type_suggest')]//input")
    public CheckBox suggestCheckBox;

    @Name("Чекбокс включения/выключения моих запросов в саджесте")
    @FindBy(xpath = "//input[@class='b-checkbox b-checkbox_type_nahodki']")
    public CheckBox suggestMyCheckBox;

    @Name("Чекбокс включения/выключения любимых сайтов в саджесте")
    @FindBy(xpath = "//input[@class='b-checkbox b-checkbox_type_favorite']")
    public CheckBox suggestFavoriteCheckBox;

    @Name("Кнопка сохранения")
    @FindBy(xpath = "//input[@class='b-form-button__input'][@type='submit']")
    public HtmlElement saveButton;


}
