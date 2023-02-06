package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: ivannik
 * Date: 10.09.2014
 */
@Name("Блок электричек")
@FindBy(xpath = "//div[contains(@class, 'b-widget  b-etrains')]")
public class EtrainsBlock extends HtmlElement {

    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class,'b-widget__title')]")
    public HtmlElement title;

    @Name("Видимое направление")
    @FindBy(xpath = ".//div[contains(@class, 'b-etrains__track')][1]")
    public DirectionBlock directionBlock1;

    @Name("Невидимое направление")
    @FindBy(xpath = ".//div[contains(@class, 'b-etrains__track')][2]")
    public DirectionBlock directionBlock2;

    public static class DirectionBlock extends HtmlElement {

        @Name("Ссылка направления")
        @FindBy(xpath = ".//a[contains(@class,'b-etrains__direction')]")
        public HtmlElement directionLink;

        @Name("Ссылки времени")
        @FindBy(xpath = ".//li[contains(@class,'b-etrains__time')]/a")
        public List<HtmlElement> timeLinks;

        @Name("Хинт")
        @FindBy(xpath = ".//div[@class='hint']")
        public Hint hint;
    }

    public static class Hint extends HtmlElement {

        @Name("Ссылка 'Посмотреть расписание'")
        @FindBy(xpath = ".//div[@class='hint__url']/a")
        public HtmlElement raspLink;
    }
}
