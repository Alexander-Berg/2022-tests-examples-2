package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.sql.Time;
import java.util.List;

/**
 * User: alex89
 * Date: 17.07.12
 * Блок новостей на новой "морде".
 */

@Name("Блок новостей")
@FindBy(xpath = "//div[contains(@class, 'wrapper-topnews')]")
public class NewsBlock extends Widget {
    @Name("Таб 'Новости'")
    @FindBy(xpath = ".//div[contains(@class,'b-tabs__head')]//a[@name='tab0']")
    public TvAfishaNewsTab mainNewsTab;

    @Name("Таб региональных новостей")
    @FindBy(xpath = ".//div[contains(@class,'b-tabs__head')]//a[@name='tab1']")
    public TvAfishaNewsTab regNewsTab;

    @Name("Таб 'Блоги-Спорт'")
    @FindBy(xpath = ".//div[contains(@class,'b-tabs__head')]//a[@name='tab2']")
    public TvAfishaNewsTab sportTab;

    @Name("Список новостей")
    @FindBy(xpath = ".//div[@class='b-tabs__items']/div[1]//li")
    public List<NewsItem> mainNews;

    @Name("Список региональных новостей")
    @FindBy(xpath = ".//div[@class='b-tabs__items']/div[2]//li")
    public List<NewsItem> regionalNews;

    @Name("Список новостей спорта/блогов")
    @FindBy(xpath = ".//div[@class='b-tabs__items']/div[3]//li")
    public List<NewsItem> sportNews;

    @Name("Время")
    @FindBy(xpath = ".//span[@class='datetime__time']/a")
    public TimeElement time;

    @Name("Дата")
    @FindBy(xpath = ".//span[@class='datetime__date']")
    public Date date;

    public static class NewsItem extends HtmlElement {
        @Name("Номер новости")
        @FindBy(xpath = ".//span[contains(@class,'num')]")
        public HtmlElement number;

        @Name("Ссылка на новость")
        @FindBy(xpath = ".//a")
        public HtmlElement link;
    }

    public static class TimeElement extends HtmlElement {
        @Name("Текущее время: часы")
        @FindBy(xpath = ".//span[contains(@class, 'hour')]")
        public HtmlElement hours;

        @Name("Текущее время: минуты")
        @FindBy(xpath = ".//span[contains(@class, 'min')]")
        public HtmlElement minutes;

        @Name("разделитель(:)")
        @FindBy(xpath = ".//span[contains(@class, 'datetime__flicker')]")
        public HtmlElement divider;

        public Time getTime() {
            String h = hours.getText();
            String m = minutes.getText();
            return Time.valueOf(h + ":" + m + ":00");
        }
    }

    public static class Date extends HtmlElement {
        @Name("Дата:число")
        @FindBy(xpath = ".//span[contains(@class,'_day')]")
        public HtmlElement day;

        @Name("Дата:день недели")
        @FindBy(xpath = ".//span[contains(@class,'_wday')]")
        public HtmlElement wDay;

        @Name("Дата:месяц")
        @FindBy(xpath = ".//span[contains(@class,'_month')]")
        public HtmlElement month;
    }
}