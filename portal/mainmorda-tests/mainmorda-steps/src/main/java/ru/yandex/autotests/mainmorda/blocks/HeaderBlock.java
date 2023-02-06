package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: alex89
 * Date: 17.07.12
 * Элементы header-а на новой "морде".
 */

@FindBy(xpath = "//div[contains(@class,'line_bar')]")
@Name("Header")
public class HeaderBlock extends HtmlElement {
    @Name("Текст 'Сделать Яндекс стартовой страницей'")
    @FindBy(xpath = ".//span[@class='b-sethome__text']")
    public HtmlElement setHomeText;

    @Name("Ссылка 'стартовой страницей'")
    @FindBy(xpath = ".//span[@class='b-sethome__text']/a")
    public HtmlElement setHomeLink;

    @Name("Выпадающая вкладка для установки стартовой страницы")
    @FindBy(xpath = "//div[@class='popup__content'][.//div[contains(@class,'b-sethome__popupa-content')]]")
    public SetHomePopUp setHomePopUp;

    @Name("Переключалка языка")
    @FindBy(xpath = ".//div[contains(@class, 'b-inline b-head-item')]//div[contains(@class, 'dropdown-menu  dropdown')]" +
            "//a[contains(@class, 'dropdown-menu__switcher')]")
    public HtmlElement langSwitcher;

    @Name("Выпадушка переключалки языка")
    @FindBy(xpath = "//div[contains(@class,'popup__content')][.//span[@class='b-langs__item']]")
    public LangSwitcherPopUp langSwitcherPopUp;

    @Name("Выпадушка переключалки языка")
    @FindBy(xpath = "//div[contains(@class,'popup__content')][.//span[@class='b-langs__item']]")
    public LangSwitcherExtPopUp langSwitcherExtPopUp;

    @Name("Ссылка 'Личные настройки'")
    @FindBy(xpath = "//a[contains(@class, 'header__action_type_settings')]")
    public HtmlElement setupLink;

    @Name("Выпадающая вкладка 'Личные настройки'")
    @FindBy(xpath = "//div[contains(@class, 'popup_visibility_visible')]//div[@class='popup__content']")
    public SetupMainPopUp setupMainPopUp;

    @Name("Выпадающая вкладка 'Личные настройки'")
    @FindBy(xpath = "//div[contains(@class, 'popup_visibility_visible')]//div[@class='popup__content']")
    public SetupChooseThemePopUp setupChooseThemePopUp;

    @Name("Выпадающая вкладка 'Личные настройки'")
    @FindBy(xpath = "//div[contains(@class, 'popup_visibility_visible')]//div[@class='popup__content']")
    public SetupThemePopUp setupThemePopUp;

    @Name("Ссылка c именем логина")
    @FindBy(xpath = ".//div//a[.//span[contains(@class,'user__name')]]")
    public HtmlElement loginNameLink;

    @Name("Кнопка 'Войти в почту'")
    @FindBy(xpath = ".//a[.//button[contains(@class, 'user__enter')]]")
    public HtmlElement loginButton;

    @Name("Выпадающая вкладка под именем логина")
    @FindBy(xpath = "//div[contains(@class, 'popup_user_yes')]//div[@class='popup__content']")
    public LoginPopUp loginPopUp;

    public static class SetHomePopUp extends HtmlElement {
        @Name("Текст о установке стартовой страницы")
        @FindBy(xpath = ".//p[@class='b-sethome__popupa-text']")
        public HtmlElement popUpText;

        @Name("Иконка для перетаскивания для установки стартовой страницы")
        @FindBy(xpath = ".//i[@class='b-sethome_browser_ff__drag-me']")
        public HtmlElement popUpIcon;

        @Name("Иконка для перетаскивания для установки стартовой страницы")
        @FindBy(xpath = ".//span[@class='b-sethome_browser_ff__drag-me-text']")
        public HtmlElement popUpIconText;

        @Name("Ссылка иконки для перетаскивания для установки стартовой страницы")
        @FindBy(xpath = ".//a[i[@class='b-sethome_browser_ff__drag-me']]")
        public HtmlElement popUpIconLink;
    }

    public static class LangSwitcherPopUp extends HtmlElement {
        @Name("Доступный язык")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][1]//a")
        public LangElement secondLang;

        @Name("Выбранный язык")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][2]//span[@class='b-langs__item']")
        public LangElement currentLang;

        @Name("Ссылка 'Еще'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][4]//a")
        public HtmlElement more;
    }

    public static class LangSwitcherExtPopUp extends HtmlElement {
        @Name("Дефолтный язык")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][1]//a")
        public LangElement defaultLang;

        @Name("Национальный язык")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][2]//a")
        public LangElement nationalLang;

        @Name("Выбранный язык")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][3]//span[@class='b-langs__item']")
        public LangElement currentLang;

        @Name("Ссылка 'Еще'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][5]//a")
        public HtmlElement more;
    }


    public static class SetupMainPopUp extends HtmlElement {
        @Name("Ссылка 'Поставить тему' в выпадающей вкладке 'Настроить'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][1]//a")
        public HtmlElement setThemeLink;

        @Name("Список всех ссылок'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')]//a")
        public List<HtmlElement> allLinks;

        @Name("Ссылка 'Настроить Яндекс'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][2]//a")
        public HtmlElement setUpYandex;

        @Name("Ссылка 'Добавить виджет'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][3]//a")
        public HtmlElement addWidget;

        @Name("Ссылка 'Изменить город' в выпадающей вкладке 'Настроить'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][5]//a")
        public HtmlElement changeCityLink;

        @Name("Ссылка 'Другие настройки' в выпадающей вкладке 'Настроить'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][6]//a")
        public HtmlElement otherSettingsLink;
    }

    public static class SetupChooseThemePopUp extends HtmlElement {
        @Name("Список всех ссылок'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')]//a")
        public List<HtmlElement> allLinks;

        @Name("Текст (без ссылки) 'Поставить тему' в выпадающей вкладке 'Настроить'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][1]//span")
        public HtmlElement setThemeText;

        @Name("Ссылка 'Изменить город' в выпадающей вкладке 'Настроить'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][3]//a")
        public HtmlElement changeCityLink;

        @Name("Ссылка 'Другие настройки' в выпадающей вкладке 'Настроить'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][4]//a")
        public HtmlElement otherSettingsLink;
    }

    public static class SetupThemePopUp extends HtmlElement {
        @Name("Список всех ссылок'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')]//a")
        public List<HtmlElement> allLinks;

        @Name("Ссылка 'Поставить тему' в выпадающей вкладке 'Настроить'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][1]//a")
        public HtmlElement setThemeLink;

        @Name("Ссылка 'Сбросить тему' в выпадающей вкладке 'Настроить'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][2]//a")
        public HtmlElement dropThemeLink;

        @Name("Ссылка 'Настроить Яндекс'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][3]//a")
        public HtmlElement setUpYandex;

        @Name("Ссылка 'Добавить виджет'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][4]//a")
        public HtmlElement addWidget;

        @Name("Ссылка 'Изменить город' в выпадающей вкладке 'Настроить'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][6]//a")
        public HtmlElement changeCityLink;

        @Name("Ссылка 'Другие настройки' в выпадающей вкладке 'Настроить'")
        @FindBy(xpath = ".//li[contains(@class, 'b-menu__item')][7]//a")
        public HtmlElement otherSettingsLink;
    }

    public static class LoginPopUp extends HtmlElement {

        @Name("Блок с ссылками настройка и паспорт")
        @FindBy(xpath = ".//div[@class='user__menu']")
        public HtmlElement settingsAndPassportLinks;

        @Name("Блок мультиавторизации")
        @FindBy(xpath = ".//div[@class='userlist i-bem userlist_js_inited']")
        public MultiAuthorizationBlock multiAuthorizationBlock;

        public static class MultiAuthorizationBlock extends  HtmlElement {
            @Name("Ссылка добавить юзера")
            @FindBy(xpath = ".//a [@class='userlist__item userlist__item-add']")
            public HtmlElement addUserLink;

            @Name("Первый юзер в списке")
            @FindBy(xpath = "//span[contains(@class, 'userlist__item-user')][1]")
            public HtmlElement firstUser;

            @Name("ССылка редактировать список")
            @FindBy(xpath = ".//a [@class='userlist__item userlist__item-edit']")
            public HtmlElement editListLink;

            @Name("Ссылка выйти")
            @FindBy(xpath = ".//a [@class='userlist__item userlist__item-logout']")
            public HtmlElement exitLink;

            @Name("Промо блок")
            @FindBy(xpath = "//div [contains(@class, 'popup multiauth-promo')]")
            public HtmlElement promoWindow;
        }

        @Name("Ссылка 'Настройка' в выпадающей вкладке")
        @FindBy(xpath = ".//a[1]")
        public HtmlElement settingsLink;


        @Name("Ссылка 'Паспорт' в выпадающей вкладке")
        @FindBy(xpath = ".//a[2]")
        public HtmlElement passportLink;

        @Name("Ссылка 'Выход' в выпадающей вкладке")
        @FindBy(xpath = ".//a[contains(@class, 'logout')]")
        public HtmlElement exitLink;
    }

    public static class LangElement extends HtmlElement {
        @Name("Иконка языка")
        @FindBy(xpath = ".//img")
        public HtmlElement icon;
    }
}