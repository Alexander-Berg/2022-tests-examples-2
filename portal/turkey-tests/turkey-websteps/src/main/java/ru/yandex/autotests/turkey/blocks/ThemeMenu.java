package ru.yandex.autotests.turkey.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.Selectable;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;

/**
 * User: alex89
 * Date: 22.01.13
 */
@Name("Меню установки скинов")
@FindBy(xpath = "//div[@class='themes-list i-bem']")
public class ThemeMenu extends HtmlElement {

    @Name("Ссылка 'Вернуть обычный яндекс'")
    @FindBy(xpath = ".//div[@class='themes-list__cancel']/a")
    public HtmlElement resetThemeButton;

    @Name("Список табов в меню")
    @FindBy(xpath = ".//ul[@class='tabs themes-list__tabs']/li")
    public List<TabMenuItem> tabs;

    @Name("Список скинов в меню")
    @FindBy(xpath = "//div[contains(@class, 'themes-list__theme themes-list__theme') " +
            "and not(contains(@class, 'hidden'))]")
    public List<SkinMenuItem> skinsListInMenu;

    @Name("Выбранный скин")
    @FindBy(xpath = ".//*[contains(@class, 'theme_selected')]")
    public SkinMenuItem selectedSkin;

    @Name("Кнопка прокрутки вправо")
    @FindBy(xpath = ".//div[contains(@class, 'themes-list__arrow_prev')]")
    public HtmlElement prevButton;

    @Name("Кнопка прокрутки вправо")
    @FindBy(xpath = ".//div[contains(@class, 'themes-list__arrow_next')]")
    public HtmlElement nextButton;

    @Name("Блок подтверждения/отмены установки скина")
    @FindBy(xpath = "//div[contains(@class, 'themes-popup__wrapper')]/div")
    public ThemePopup themeAcceptPopup;

    public static class SkinMenuItem extends HtmlElement {
        private static final String SKIN_CLASS_PATTERN =
                "b-inline themes-list__theme themes-list__theme_([a-z0-9]+)" +
                        "( themes-list__theme_hidden)?( themes-list__theme_selected)?";

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
            System.out.println(idFormat.group(1));
            return idFormat.group(1);
        }

        @Override
        public void click() {
            skinSetUpLink.click();
        }

    }

    public static class TabMenuItem extends HtmlElement implements Selectable {
        private static final String TAB_CLASS_PATTERN =
                "tabs__item themes-list__tab themes-list__tab_([a-z]+)( tabs__item_selected)?";
//                "b-themes-list__tab b-themes-list__tab_([a-z]+)( b-themes-list__tab_selected){0,}";

        private static final String SELECTED = "selected";

        Pattern validationTabPattern = Pattern.compile(TAB_CLASS_PATTERN);

        public String getId() {
            Matcher idFormat = validationTabPattern.matcher(getWrappedElement().getAttribute(CLASS.toString()));
            idFormat.matches();
            return idFormat.group(1);
        }


        @Override
        public void select() {
            if (!isSelected()) {
                click();
            }
        }

        @Override
        public void deselect() {
            if (isSelected()) {
                click();
            }
        }

        @Override
        public boolean isSelected() {
            return getWrappedElement().getAttribute(CLASS.toString()).contains(SELECTED);
        }
    }

    public static class ThemePopup extends HtmlElement {
        @Name("Кнопка 'Отмена'")
        @FindBy(xpath = ".//a[contains(@class, 'button_theme_normal')]")
        public HtmlElement cancelButton;

        @Name("Кнопка 'OK'")
        @FindBy(xpath = ".//a[contains(@class, 'button_theme_action')]")
        public HtmlElement okButton;
    }
}