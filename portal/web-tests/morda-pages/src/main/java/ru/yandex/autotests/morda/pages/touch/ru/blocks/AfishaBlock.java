package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaEvent;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static java.lang.Thread.sleep;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.WebElementSteps.clickOn;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_KEY;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/05/15
 */
@Name("Блок Афиша")
@FindBy(xpath = "//div[contains(@class,'afisha')]")
public class AfishaBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//a[@class='block__title-text']")
    private HtmlElement title;

    @Name("Список фильмов")
    @FindBy(xpath = ".//a[contains(@class, 'afisha__film-link')]")
    private List<AfishaItem> items;

    @Name("Список кинотеатров")
    @FindBy(xpath = ".//div[contains(@class,'afisha__cinemas-list')]//a")
    private List<HtmlElement> cinemaTabs;

    @Name("Иконка определения местоположения")
    @FindBy(xpath = ".//div[contains(@class, 'geoblock2__locate-icon')]")
    private HtmlElement locateIcon;

    @Name("\"Показать кинотеатры рядом\"")
    @FindBy(xpath = ".//span[contains(@class, 'geoblock2__locate-text')]")
    private HtmlElement locateText;

    @Step("Afisha focus")
    public void focus(WebDriver driver){
        title.click();
    }

    @Step("Set second category")
    public void setSecondCinema() throws InterruptedException {
        HtmlElement category = cinemaTabs.get(0);
        shouldSee(category);
        clickOn(category);
    }

    @Step("Should be selected second category")
    public void shouldBeSelectedSecondCinema() throws InterruptedException {
        String classAttribute = cinemaTabs.get(0).getAttribute("class");
        assertThat("Category don't selected",
                classAttribute,
                containsString("afisha__category_selected_yes"));
    }

    public void setSecondCinema(WebDriver driver) throws InterruptedException {
        sleep(500);
        List<WebElement> tabs = driver.findElements(By.xpath("//div[contains(@class,'afisha__cinemas-list')]//a"));
        WebElement category =  tabs.get(0);
        category.click();
    }

    public void shouldBeSelectedSecondCinema(WebDriver driver) throws InterruptedException {
        List<WebElement> tabs = driver.findElements(By.xpath("//div[contains(@class,'afisha__cinemas-list')]//a"));
        String classAttribute = tabs.get(0).getAttribute("class");
        assertThat("Category don't selected",
                classAttribute,
                containsString("afisha__category_selected_yes"));
    }

    @Override
    @Step("Check afisha")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(validator),
                        validateItems(validator),
                        validateLocationDataItems(validator)
                );
    }

    @Step("Check title")
    public HierarchicalErrorCollector validateTitle(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(title))
                .check(
                        shouldSeeElementMatchingTo(title, allOfDetailed(
                                hasText(getTranslation(Dictionary.Home.Afisha.TITLE, validator.getMorda().getLanguage())),
                                hasAttribute(HREF, equalTo(validator.getCleanvars().getAfisha().getHref()))
                        ))
                );
    }

    @Step("Check items")
    public HierarchicalErrorCollector validateItems(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(validator.getCleanvars().getAfisha().getEvents().size(), items.size()); i++) {
            AfishaItem item = items.get(i);
            AfishaEvent afishaEvent = validator.getCleanvars().getAfisha().getEvents().get(i);

            collector.check(validateItem(validator, item, afishaEvent));
        }

        HierarchicalErrorCollector movieCountCollector = collector().check(
                shouldSeeElementMatchingTo(items,
                        hasSize(validator.getCleanvars().getAfisha().getEvents().size())
                ));

        collector.check(movieCountCollector);

        return collector;
    }

    @Step("Check item: {1}")
    public HierarchicalErrorCollector validateItem(Validator<? extends TouchRuMorda> validator,
                                                   AfishaItem item,
                                                   AfishaEvent afishaEvent) {
        HierarchicalErrorCollector collector = collector()
                .check(shouldSeeElement(item))
                .check(
                        collector()
                                .check(shouldSeeElementMatchingTo(item, hasAttribute(HREF,
                                                equalTo(afishaEvent.getHref().replaceAll("&amp;", "&")))
                                )),
                        collector()
                                .check(shouldSeeElement(item.movieIcon)),
                        collector()
                                .check(shouldSeeElement(item.movieTitle))
                                .check(shouldSeeElementMatchingTo(item.movieTitle, hasText(afishaEvent.getFull().trim()))),
                        collector()
//                                .check(shouldSeeElement(item.movieGenre))
                                .check(shouldSeeElementMatchingTo(item.movieGenre,
                                                hasText(anyOf(
                                                                equalTo(afishaEvent.getGenre()),
                                                                isEmptyOrNullString())
                                                ))
                                )
                );

        if (!isEmptyOrNullString().matches(afishaEvent.getPremiereBadge())) {
            collector.check(
                    collector()
                            .check(shouldSeeElement(item.moviePremiere))
                            .check(shouldSeeElementMatchingTo(item.moviePremiere.getText().replace("\n", " "),
                                    equalTo(afishaEvent.getPremiereBadge().replace("&nbsp;"," ").toUpperCase())))
            );

        }
        return collector;
    }

    @Step("Check location block")
    public HierarchicalErrorCollector validateLocationBlock(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(
                        collector()
                                .check(shouldSeeElement(locateIcon)),
                        collector()
                                .check(shouldSeeElement(locateText))
                                .check(shouldSeeElementMatchingTo(locateText, hasText(
                                        getTranslation(Dictionary.Home.Afisha.SHOW_OBJECTS, validator.getMorda().getLanguage()))))
                );
    }

    @Step("Check location data items")
    public HierarchicalErrorCollector validateLocationDataItems(Validator<? extends TouchRuMorda> validator) {
        if (validator.isGeoLocated()) {
            return collector().check(validateCinemasTabs(validator));
        } else {
            return collector().check(validateLocationBlock(validator));
        }
    }

    @Step("Check cinema tabs")
    private HierarchicalErrorCollector validateCinemasTabs(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();
        List<ru.yandex.autotests.mordabackend.beans.geohelper.AfishaItem> expectedItems = validator.getGeohelperResponse().getAfisha();

        for (int i = 0; i != Math.min(expectedItems.size(), cinemaTabs.size()); i++) {
            HtmlElement item = cinemaTabs.get(i);

            collector.check(validateRaspTabItem(item, expectedItems.get(i)));
        }

        HierarchicalErrorCollector raspTabsCountCollector = collector().check(
                shouldSeeElementMatchingTo(cinemaTabs, hasSize(expectedItems.size())
                ));

        collector.check(raspTabsCountCollector);

        return collector;
    }

    @Step("Check cinema tab item: {0}")
    private HierarchicalErrorCollector validateRaspTabItem(HtmlElement item,
                                                           ru.yandex.autotests.mordabackend.beans.geohelper.AfishaItem info) {
        return collector()
                .check(shouldSeeElement(item))
                .check(shouldSeeElementMatchingTo(item, hasText(startsWith(info.getTitle().toUpperCase()))))
                .check(shouldSeeElementMatchingTo(item, hasAttribute(HREF, equalTo(info.getHref()))))
                .check(shouldSeeElementMatchingTo(item, hasAttribute(DATA_KEY, equalTo(String.valueOf(info.getId())))));
    }


    public static class AfishaItem extends HtmlElement {
        @Name("Премьера")
        @FindBy(xpath = ".//span[contains(@class, 'afisha__film-premiere')]")
        private HtmlElement moviePremiere;

        @Name("Картинка фильма")
        @FindBy(xpath = ".//span[contains(@class, 'afisha__film-image')]")
        private HtmlElement movieIcon;

        @Name("Название фильма")
        @FindBy(xpath = ".//span[contains(@class, 'afisha__film-title')]")
        private HtmlElement movieTitle;

        @Name("Жанр фильма")
        @FindBy(xpath = ".//span[contains(@class, 'afisha__film-genre')]")
        private HtmlElement movieGenre;
    }

}
