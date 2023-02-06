package ru.yandex.autotests.turkey.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.turkey.blocks.*;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.List;

/**
 * User: leonsabr
 * Date: 04.10.12
 */
public class YandexComTrPage {
    public YandexComTrPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Header")
    public HeaderBlock headerBlock;

    @Name("Блок информаров")
    public InformersBlock informersBlock;

    @Name("Логотип")
    @FindBy(xpath = ".//div[contains(@class,'logo')]//div[contains(@class,'logo__image')]")
    public HtmlElement logotype;

    @Name("Футер")
    public FooterBlock footerBlock;

    @Name("Поисковая форма")
    public SearchArrowBlock search;

    @Name("Блок табов")
    public TabsBlock tabsBlock;

    @Name("Виртуальная клавиатура")
    public VirtualKeyboard keyboard;

    @Name("Элементы с BADID")
    @FindBy(xpath = "//*[contains(@onmousedown, 'BADID')]")
    public List<HtmlElement> elementsWithBadId;

    @Name("Футбольный блок: Сохранить/Нет")
    public FootballSaveThemeBlock saveFootballStyleBlock;

    @Name("Футбольное оформление")
    @FindBy(xpath = "//body[contains(@class,'b-page_football-face')]")
    public HtmlElement footballStyle;

}
