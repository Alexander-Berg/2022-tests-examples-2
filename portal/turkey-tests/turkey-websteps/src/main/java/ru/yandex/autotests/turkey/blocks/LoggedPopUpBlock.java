package ru.yandex.autotests.turkey.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: ivannik
 * Date: 24.07.13
 * Time: 17:59
 */
@Name("Выпадающая вкладка под именем логина")
@FindBy(xpath = "//div[contains(@class, 'popup_domik_trigger')]//div[@class='popup__content']")
public class LoggedPopUpBlock extends HtmlElement {

    @Name("Ссылка 'Персональные данные' в выпадающей вкладке")
    @FindBy(xpath = ".//div[1]//a")
    public HtmlElement passportLink;

    @Name("Ссылка 'Изменить город' в выпадающей вкладке")
    @FindBy(xpath = ".//div[2]//a")
    public HtmlElement regionLink;

    @Name("Ссылка 'Другие настройки' в выпадающей вкладке")
    @FindBy(xpath = ".//div[3]//a")
    public HtmlElement settingsLink;

    @Name("Ссылка 'Выйти' в выпадающей вкладке")
    @FindBy(xpath = ".//div[4]//a")
    public HtmlElement logoutLink;
}
