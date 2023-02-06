package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.Selectable;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SELECTED;

/**
 * User: alex89
 * Date: 22.01.13
 */
@Name("Меню установки скинов")
@FindBy(xpath = "//div[contains(@class,'b-themes-list unselectable')]")
public class ThemeMenu extends HtmlElement {

    @Name("Крестик 'Закрыть'")
    @FindBy(xpath = ".//a[@class='b-themes-list__cancel-link']")
    public HtmlElement closeCross;

    @Name("Кнопка 'Отмена'")
    @FindBy(xpath = ".//div[@class='b-themes-list__decision-control']" +
            "//a[contains(@class,'b-form-button_theme_grey-m') or contains(@class, 'button_theme_normal')]")
    public HtmlElement cancelButton;

    @Name("Кнопка 'Сохранить тему'")
    @FindBy(xpath = ".//div[@class='b-themes-list__decision-control']" +
            "//a[contains(@class,'b-form-button_theme_green-m') or contains(@class, 'button_theme_action')]")
    public HtmlElement saveThemeButton;

    @Name("Ссылка 'Вернуть обычный яндекс'")
    @FindBy(xpath = ".//a[@class='b-themes-list__default-link']")
    public HtmlElement resetThemeLink;

    @Name("Блок 'Поделиться темой'")
    @FindBy(xpath = ".//span[@id='ya_skin_share']")
    public ShareBlock shareBlock;

    @Name("Список табов в меню")
    @FindBy(xpath = ".//ul[@class='b-themes-list__tabs']/li[i]")
    public List<TabMenuItem> tabsListInMenu;

    @Name("Кнопка прокрутки вправо")
    @FindBy(xpath = ".//i[@class='b-themes-list__arrow-next']")
    public HtmlElement nextButton;

    @Name("Список скинов в меню")
    @FindBy(xpath = ".//div[@class='b-themes-list__list']" +
            "//div[contains(@class, 'b-themes-list__theme b-themes-list__theme_') and not(contains(@class, 'hidden'))]")
    public List<SkinMenuItem> skinsListInMenu;

    public static class TabMenuItem extends HtmlElement implements Selectable {
        private static final String TAB_CLASS_PATTERN =
                "b-themes-list__tab b-themes-list__tab_([a-z]+)( b-themes-list__tab_selected){0,}";

        @Name("Ссылка для установки")
        @FindBy(xpath = "./i")
        private HtmlElement selectTabElement;

        Pattern validationTabPattern = Pattern.compile(TAB_CLASS_PATTERN);

        public String getId() {
            Matcher idFormat = validationTabPattern.matcher(getWrappedElement().getAttribute(CLASS.toString()));
            idFormat.matches();
            return idFormat.group(1);
        }

        @Override
        public void click() {
            selectTabElement.click();
        }

        @Override
        public void select() {
            if (!isSelected()) {
                selectTabElement.click();
            }
        }

        @Override
        public void deselect() {
            if (isSelected()) {
                selectTabElement.click();
            }
        }

        @Override
        public boolean isSelected() {
            return getWrappedElement().getAttribute(CLASS.toString()).contains(SELECTED.toString());

        }
    }

    public static class ShareBlock extends HtmlElement {
        @Name("Кнопка 'Поделиться темой'")
        @FindBy(xpath = "./span[@class='b-share']/a[@class='b-share__handle']")
        public HtmlElement shareButton;

        @Name("Выпадающая вкладка 'Поделиться темой'")
        @FindBy(xpath = "//div[contains(@class,'b-share-popup__m')]")
        public SharePopUp sharePopUp;

        @Name("Соц.иконка 'facebook'")
        @FindBy(xpath = ".//a[contains(@class,'b-share__handle') and @data-service='facebook']")
        public HtmlElement fbIcon;

        @Name("Соц.иконка 'twitter'")
        @FindBy(xpath = ".//a[contains(@class,'b-share__handle') and @data-service='twitter']")
        public HtmlElement twIcon;

        @Name("Соц.иконка 'yaru'")
        @FindBy(xpath = ".//a[contains(@class,'b-share__handle') and @data-service='yaru']")
        public HtmlElement yaruIcon;

        @Name("Соц.иконка 'vk'")
        @FindBy(xpath = ".//a[contains(@class,'b-share__handle') and @data-service='vkontakte']")
        public HtmlElement vkIcon;

        @Name("Соц.иконка 'odnoklassniki'")
        @FindBy(xpath = ".//a[contains(@class,'b-share__handle') and @data-service='odnoklassniki']")
        public HtmlElement odnoklIcon;

        @Name("Соц.иконка 'moimir'")
        @FindBy(xpath = ".//a[contains(@class,'b-share__handle') and @data-service='moimir']")
        public HtmlElement moimirlIcon;
    }


    public static class SharePopUp extends HtmlElement {
        @Name("Заголовок выпадушки 'Поделиться темой'")
        @FindBy(xpath = ".//div[contains(@class,'b-share-popup__header')]")
        public HtmlElement sharePopUpHeader;

        @Name("Надпись над полем с url 'Поделиться темой'")
        @FindBy(xpath = ".//label[contains(@class,'b-share-popup__input')]")
        public HtmlElement shareFieldLabel;

        @Name("Поле с url 'Поделиться темой'")
        @FindBy(xpath = ".//label[contains(@class,'b-share-popup__input')]" +
                "/input[@readonly='readonly' and @class='b-share-popup__input__input']")
        public TextInput shareField;

        @Name("Соц.ссылка 'facebook'")
        @FindBy(xpath = ".//a[@class='b-share-popup__item' and @target='_blank' and @data-service='facebook']")
        public HtmlElement fbIcon;

        @Name("Соц.ссылка 'twitter'")
        @FindBy(xpath = ".//a[@class='b-share-popup__item' and @target='_blank' and @data-service='twitter']")
        public HtmlElement twIcon;

        @Name("Соц.ссылка 'vk'")
        @FindBy(xpath = ".//a[@class='b-share-popup__item' and @target='_blank' and @data-service='vkontakte']")
        public HtmlElement vkIcon;

        @Name("Соц.ссылка 'yaru'")
        @FindBy(xpath = ".//a[@class='b-share-popup__item' and @target='_blank' and @data-service='yaru']")
        public HtmlElement yaruIcon;

        @Name("Соц.ссылка 'odnoklassniki'")
        @FindBy(xpath = ".//a[@class='b-share-popup__item' and @target='_blank' and @data-service='odnoklassniki']")
        public HtmlElement odnoklIcon;

        @Name("Соц.ссылка 'moimir'")
        @FindBy(xpath = ".//a[@class='b-share-popup__item' and @target='_blank' and @data-service='moimir']")
        public HtmlElement moimirlIcon;

        @Name("Соц.ссылка 'lj'")
        @FindBy(xpath = ".//a[@class='b-share-popup__item' and @target='_blank' and @data-service='lj']")
        public HtmlElement ljIcon;
    }

    public static class SkinMenuItem extends HtmlElement {
        private static final String SKIN_CLASS_PATTERN =
                "b-themes-list__theme b-themes-list__theme_([a-z0-9]+)( b-themes-list__theme_selected){0,}" +
                        "( b-themes-list__theme-hidden){0,}";

        @Name("Ссылка для установки")
        @FindBy(xpath = "./a")
        public HtmlElement skinSetUpLink;

        @Name("Иконка скина")
        @FindBy(xpath = ".//img")
        public HtmlElement skinIcon;

        Pattern validationPattern = Pattern.compile(SKIN_CLASS_PATTERN);

        public String getNotation() {
            Matcher idFormat = validationPattern.matcher(getWrappedElement().getAttribute(CLASS.toString()));
            idFormat.matches();
            return idFormat.group(1);
        }

        @Override
        public void click() {
            skinSetUpLink.click();
        }
    }
}