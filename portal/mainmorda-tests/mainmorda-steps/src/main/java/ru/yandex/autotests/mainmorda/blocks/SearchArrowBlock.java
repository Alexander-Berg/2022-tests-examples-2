package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.CheckBox;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.Button;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
@FindBy(xpath = "//div[contains(@class, 'b-line_search')]")
@Name("Search Arrow")
public class SearchArrowBlock extends HtmlElement {
    @Name("Все табы")
    @FindBy(xpath = ".//div[contains(@class,'b-head-tabs__tab')]/a")
    public List<HtmlElement> allTabs;

    @Name("Все видимые табы")
    @FindBy(xpath = ".//div[contains(@class,'b-head-tabs__tab') and not(contains(@class,'i-adaptive'))]/a")
    public List<HtmlElement> tabs;

    @Name("Все невидимые табы")
    @FindBy(xpath = ".//div[contains(@class,'b-head-tabs__tab') and contains(@class,'i-adaptive')]/a")
    public List<HtmlElement> tabsHidden;

    @Name("ещё")
    @FindBy(xpath = ".//a[contains(@class, 'b-head-tabs__more')]")
    public HtmlElement more;

    @Name("Все 'еще' табы")
    @FindBy(xpath = "//div[contains(@class, 'b-services-more')]//a")
    public List<HtmlElement> allMoreTabs;

    @Name("Все 'еще' видимые табы")
    @FindBy(xpath = "//div[contains(@class, 'b-services-more')]//div[not(contains(@class,'i-adaptive'))]/a")
    public List<HtmlElement> moreTabs;

    @Name("Все 'еще' невидимые табы")
    @FindBy(xpath = "//div[contains(@class, 'b-services-more')]//div[contains(@class,'i-adaptive')]/a")
    public List<HtmlElement> moreTabsHidden;

    @Name("таб Все сервисы")
    @FindBy(xpath = ".//div[contains(@class,'b-head-tabs__tab')][10]/a")
    public HtmlElement all;

    @Name("поле ввода")
    @FindBy(xpath = ".//input[@id='text']")
    public TextInput input;

    @Name("кнопка поиска")
    @FindBy(xpath = ".//button[contains(@class, 'suggest2-form__button')]")
    public HtmlElement submit;

    @Name("текст 'Например'")
    @FindBy(xpath = ".//span[contains(@class,'_sampl')]")
    public HtmlElement forExample;

    @Name("поисковый пример")
    @FindBy(xpath = ".//span[contains(@class,'sample')]/a[contains(@class, 'input__sample')]")
    public HtmlElement example;

    @Name("иконка клавиатуры")
    @FindBy(xpath = ".//div[contains(@class,' keyboard-loader')]/i")
    public HtmlElement keyboard;

    @Name("саджест")
    @FindBy(xpath = "//ul[contains(@class, 'suggest2__content')]")
    public HtmlElement suggest;

    @Name("Чекбокс 'поиск только на белорусских сайтах'")
    @FindBy(xpath = ".//input[@class='b-morda-region-search__checkbox']")
    public CheckBox checkBoxCountry;

    @Name("Текст чекбокса 'поиск только на *** сайтах'")
    @FindBy(xpath = ".//span[@class='b-morda-region-search']/label")
    public HtmlElement checkBoxCountryText;

    @Name("lr")
    @FindBy(xpath = ".//input[@type='hidden' and @name='lr']")
    public HtmlElement lr;

    @Name("msid")
    @FindBy(xpath = ".//input[@type='hidden' and @name='msid']")
    public HtmlElement msid;

    @Name("Кнопка 'Поиск'")
    @FindBy(xpath = ".//span[./input[@type='submit']]")
    public Button submitWrapped;
}
