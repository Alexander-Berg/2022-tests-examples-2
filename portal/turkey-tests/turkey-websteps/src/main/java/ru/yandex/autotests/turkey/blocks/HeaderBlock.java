package ru.yandex.autotests.turkey.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 11.10.12
 */

@FindBy(xpath = "//div[contains(concat(' ', @class, ' '), ' b-line__bar ')]")
@Name("Header")
public class HeaderBlock extends HtmlElement {

    @Name("Ссылка почты")
    @FindBy(xpath = ".//div[contains(@class, 'b-line__bar-right')]/a")
    public HtmlElement mailLink;

    @Name("Кнопка открытия меню с логином пользователем")
    @FindBy(xpath = ".//a[contains(@class, 'user_menu_yes')]")
    public HtmlElement loginNameButton;

    public LoggedPopUpBlock loggedPopUp;

    @Name("Ссылка 'Сделать Яндекс стартовой страницей'")
    @FindBy(xpath = ".//span[@class='b-sethome__text']//a[contains(@class, 'b-sethome__link')]")
    public HtmlElement setHomeLink;

    @Name("Выпадающая вкладка для установки стартовой страницы")
    @FindBy(xpath = "//div[contains(@class, 'popupa_sethome_fx')]")
    public SetHomePopUp setHomePopUp;

    public static class SetHomePopUp extends HtmlElement {
        @Name("Текст о установке стартовой страницы")
        @FindBy(xpath = ".//p[@class='b-sethome__popupa-text']")
        public HtmlElement popUpText;

        @Name("Иконка для перетаскивания для установки стартовой страницы")
        @FindBy(xpath = ".//i[@class='b-sethome_browser_ff__drag-me']")
        public HtmlElement popUpIcon;

        @Name("Подпись иконки для перетаскивания для установки стартовой страницы")
        @FindBy(xpath = ".//span[@class='b-sethome_browser_ff__drag-me-text']")
        public HtmlElement popUpIconText;

        @Name("Ссылка иконки для перетаскивания для установки стартовой страницы")
        @FindBy(xpath = ".//a[i[@class='b-sethome_browser_ff__drag-me']]")
        public HtmlElement popUpIconLink;
    }
}
