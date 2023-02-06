package ru.yandex.autotests.mordacommonsteps.steps;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.core.har.HarEntry;
import org.hamcrest.Matcher;
import org.openqa.selenium.By;
import org.openqa.selenium.Dimension;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.internal.WrapsElement;
import org.openqa.selenium.remote.LocalFileDetector;
import org.openqa.selenium.remote.RemoteWebElement;
import ru.yandex.autotests.mordacommonsteps.matchers.ListContainsElementMatcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordacommonsteps.utils.Selectable;
import ru.yandex.autotests.mordacommonsteps.utils.SettingsSelect;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.autotests.utils.morda.auth.User;
import ru.yandex.autotests.utils.morda.cookie.Cookie;
import ru.yandex.autotests.utils.morda.cookie.CookieManager;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.users.PassportManager;
import ru.yandex.qatools.allure.annotations.Attachment;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Select;

import java.io.File;
import java.net.URL;
import java.util.List;
import java.util.Random;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.select;
import static ch.lambdaj.Lambda.selectFirst;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.lessThan;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordacommonsteps.matchers.HarResponseMatcher.harResponses;
import static ru.yandex.autotests.mordacommonsteps.matchers.UrlMatcher.urlMatches;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.autotests.utils.morda.auth.UserManager.login;
import static ru.yandex.autotests.utils.morda.auth.UserManager.logout;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.setLanguage;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.setLanguageOnCom;
import static ru.yandex.autotests.utils.morda.region.RegionManager.setRegion;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.isDisplayed;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;


public class CommonMordaSteps {

    private WebDriver driver;

    public CommonMordaSteps(WebDriver driver) {
        this.driver = driver;
    }

    @Step("Open page \"{0}\"; language \"{1}\"")
    public void initTest(String url, Language language) {
        opensPage(url);
        setsLanguage(language);
    }

    @Step("Open page \"{0}\"; region \"{1}\"; language \"{2}\"")
    public void initTest(String url, Region region, Language language) {
        opensPage(url);
        setsRegion(region);
        setsLanguage(language);
    }

    @Step("Set region \"{0}\"")
    public void setsRegion(Region region) {
        setRegion(driver, region);
    }

    @Step("Set region \"{0}\" with retpath \"{1}\"")
    public void setsRegion(Region region, String retpath) {
        setRegion(driver, region, retpath);
    }

    @Step("Logout")
    public void logsOut() {
        assertThat("Не удалось разлогиниться через паспорт!", logout(driver), is(true));
    }

    @Step("Logout with retpath \"{0}\"")
    public void logsOut(String retpath) {
        assertThat("Не удалось разлогиниться через паспорт!", logout(driver, retpath), is(true));
    }

    @Step("Login as \"{0}\"")
    public void logsInAs(User user) {
        assertThat("Не удалось залогиниться через паспорт!", login(driver, user), is(true));
    }

    @Step("Login as \"{0}\" with retpath \"{1}\"")
    public void logsInAs(User user, String retpath) {
        assertThat("Не удалось залогиниться через паспорт!", login(driver, user, retpath), is(true));
    }

    @Step("Login as \"{0}\"")
    public void logsInAs(ru.yandex.autotests.utils.morda.users.User user) {
        assertThat("Не удалось залогиниться через паспорт!", PassportManager.login(driver, user), is(true));
    }

    @Step("Login as \"{0}\" with retpath \"{1}\"")
    public void logsInAs(ru.yandex.autotests.utils.morda.users.User user, String retpath) {
        assertThat("Не удалось залогиниться через паспорт!", PassportManager.login(driver, user, retpath), is(true));
    }

    @Step("Login as \"{0}\"")
    public void logsInAs(ru.yandex.autotests.utils.morda.users.User user, URL host) {
        assertThat("Не удалось залогиниться через паспорт!", PassportManager.login(driver, user, host), is(true));
    }

    @Step("Login as \"{0}\" with retpath \"{1}\"")
    public void logsInAs(ru.yandex.autotests.utils.morda.users.User user, URL host, String retpath) {
        assertThat("Не удалось залогиниться через паспорт!",
                PassportManager.login(driver, user, host, retpath), is(true));
    }

    @Step("Open page \"{0}\"")
    public void opensPage(String url) {
        driver.get(url);
        assertThat("Не дождались открытия страницы " + url, driver,
                withWaitFor(urlMatches(startsWith(url))));
    }

    @Step("Open page \"{0}\", should see \"{1}\"")
    public void opensPage(String url, String expectedUrl) {
        driver.get(url);
        assertThat("Не дождались открытия страницы " + url, driver,
                withWaitFor(urlMatches(startsWith(expectedUrl))));
    }

    @Step("Open page \"{0}\", should see \"{1}\"")
    public void opensPage(String url, Matcher<String> expectedUrl) {
        driver.get(url);
        assertThat("Не дождались открытия страницы " + url, driver,
                withWaitFor(urlMatches(expectedUrl)));
    }

    @Step("Should see page: \"{0}\"")
    public void shouldSeePage(String url) {
        assertThat("URL открывшейся страницы неверный!", driver,
                withWaitFor(urlMatches(startsWith(url))));
    }

    @Step("Should see page: {0}")
    public void shouldSeePage(Matcher<String> url) {
        assertThat("URL открывшейся страницы неверный!",
                driver, withWaitFor(urlMatches(url)));
    }

    @Step("Return back")
    public void returnsBack() {
        driver.navigate().back();
    }

    @Step("Refresh page")
    public void refreshPage() {
        driver.navigate().refresh();
    }

    @Step("Maximize window")
    public void maximizeWindow() {
        driver.manage().window().maximize();
    }

    @Step("Resize window: ({0}, {1})")
    public void resizeWindow(int width, int height) {
        driver.manage().window().setSize(new Dimension(width, height));
    }

    @Step("Resize window: {0}")
    public void resizeWindow(Dimension size) {
        driver.manage().window().setSize(size);
    }

    @Step("Should see element \"{0}\"")
    public void shouldSeeElement(WrapsElement element) {
        assertThat(element + " отсутствует в верстке страницы!", element,
                withWaitFor(exists()));
        assertThat(element + " не отображается на странице!", element,
                withWaitFor(isDisplayed()));
    }

    @Step("Should see element \"{2}\" in list \"{0}\"")
    public <T extends HtmlElement, E> T shouldSeeElementInList(List<T> list, E element, Matcher<? super E> matcher) {
        ListContainsElementMatcher<T, E> hasItem = new ListContainsElementMatcher<T, E>(element, matcher);
        assertThat(list, withWaitFor(hasItem));
        return hasItem.getItem();
    }

    @Step("Should not see element \"{2}\" in list \"{0}\"")
    public <T extends HtmlElement, E> void shouldNotSeeElementInList(List<T> list, E element,
                                                                     Matcher<? super E> matcher) {
        ListContainsElementMatcher<T, E> hasItem = new ListContainsElementMatcher<T, E>(element, matcher);
        assertThat(list, withWaitFor(not(hasItem)));
    }

    @Step("Should not see element \"{0}\"")
    public void shouldNotSeeElement(WrapsElement element) {
        if (exists().matches(element)) {
            assertThat("Элемент \"" + element + "\" не должен быть виден  на странице!",
                    element, withWaitFor(not(isDisplayed())));
        }
    }

    @Step("Click on element \"{0}\"")
    public void clicksOn(WrapsElement element) {
        element.getWrappedElement().click();
    }

    @Step("Click on element \"{0}\"")
    public void clicksOn(HtmlElement element) {
        element.click();
    }

    @Step("Click on element \"{0}\" and waits for content loaded")
    public void clicksAndWaitsAjax(HtmlElement element) {
        element.click();
        assertThat(driver, withWaitFor(contentLoaded()));
    }

    @Step("Click on element \"{0}\" and waits for content loaded")
    public void clicksAndWaitsAjax(WrapsElement element) {
        element.getWrappedElement().click();
        assertThat(driver, withWaitFor(contentLoaded()));
    }

    @Step("Move mouse to element \"{0}\"")
    public void moveMouseOn(WrapsElement element) {
        MouseEvents.mouseTo(driver, element.getWrappedElement());
    }

    @Step("Write text \"{1}\" in input \"{0}\"")
    public void entersTextInInput(TextInput input, String text) {
        input.clear();
        assertThat("Не дождались отчистки поля ввода",
                input,
                withWaitFor(hasText(isEmptyOrNullString())));
        input.sendKeys(text);
        assertThat("Не дождались текста " + text + " в поле ввода",
                input,
                withWaitFor(hasText(equalTo(text))));
    }

    @Step("Append text \"{1}\" in input \"{0}\"")
    public void appendsTextInInput(TextInput input, String text) {
        input.sendKeys(text);
        assertThat("Не дождались текста " + text + " в поле ввода",
                input,
                withWaitFor(hasText(endsWith(text))));
    }

    @Step("Clear input \"{0}\"")
    public void clearsInput(TextInput input) {
        input.clear();
        assertThat("Не дождались отчистки поля ввода",
                input,
                withWaitFor(hasText(isEmptyOrNullString())));
    }

    @Step("Should see element \"{0}\" with text: \"{1}\"")
    public void shouldSeeElementWithText(WrapsElement element, String text) {
        assertThat(element + " имеет некорректный текст!", element.getWrappedElement(),
                withWaitFor(hasText(equalTo(text))));
    }

    @Step("Should see element \"{0}\" with text: {1}")
    public void shouldSeeElementWithText(WrapsElement element, Matcher<String> matcher) {
        assertThat("Текст элемента не удовлетворяет матчеру!", element.getWrappedElement(),
                withWaitFor(hasText(matcher)));
    }

    @Step("Should see text \"{1}\" in input \"{0}\"")
    public void shouldSeeInputWithText(TextInput input, String text) {
        assertThat("Текст в поле ввода не удовлетворяет матчеру!", input, withWaitFor(hasText(equalTo(text))));
    }

    @Step("Should see text {1} in input \"{0}\"")
    public void shouldSeeInputWithText(TextInput input, Matcher<String> matcher) {
        assertThat("Текст в поле ввода не удовлетворяет матчеру!", input, withWaitFor(hasText(matcher)));
    }

    @Step("Should see element \"{0}\": {1}")
    public void shouldSeeElementMatchingTo(HtmlElement element, Matcher<? super HtmlElement> matcher) {
        assertThat(element, withWaitFor(matcher));
    }

    @Step("Should see element \"{0}\": {1}")
    public void shouldSeeElementMatchingTo(HtmlElement element, Matcher<? super HtmlElement>... matchers) {
        assertThat(element, withWaitFor(allOf(matchers)));
    }

    @Step("Should see link: {1}")
    public void shouldSeeLinkLight(HtmlElement link, LinkInfo info) {
        shouldSeeElement(link);
        shouldSeeElementWithText(link, info.text);
        shouldSeeElementMatchingTo(link, info.attributes);
    }

    @Step("Should see link: {1}")
    public void shouldSeeLink(HtmlElement link, LinkInfo info) {
        shouldSeeElement(link);
        shouldSeeElementWithText(link, info.text);
        shouldSeeElementMatchingTo(link, info.attributes);
        clicksOn(link);
        shouldSeePage(info.url);
    }

    @Step("Should see list \"{0}\" with size {1}")
    public void shouldSeeListWithSize(List<?> list, Matcher<Integer> matcher) {
        assertThat("У списка неверный размер", list, withWaitFor(hasSize(matcher)));
    }

    @Step("Should see select \"{0}\" with size {1}")
    public void shouldSeeSelectWithSize(Select select, Matcher<Integer> matcher) {
        assertThat("У селектора неверное количество опций", select.getOptions(), withWaitFor(hasSize(matcher)));
    }

    @Step("Select element \"{0}\"")
    public void selectElement(Selectable element) {
        element.select();
    }

    @Step("Deselect element \"{0}\"")
    public void deselectElement(Selectable element) {
        element.deselect();
    }

    @Step("In \"{0}\" select element with visible text {1}")
    public void selectByVisibleText(Select select, String visibleText) {
        try {
            select.selectByVisibleText(visibleText);
        } catch (NoSuchElementException e) {
            fail(e.getMessage());
        }
    }

    @Step("In \"{0}\" select element with value {1}")
    public void selectByValue(Select select, String value) {
        try {
            select.selectByValue(value);
        } catch (NoSuchElementException e) {
            fail(e.getMessage());
        }
    }

    @Step("In \"{0}\" select element number {1}")
    public void selectOption(Select select, int pos) {
        try {
            select.selectByIndex(pos);
        } catch (NoSuchElementException e) {
            fail(e.getMessage());
        }
    }

    @Step("Select random option in \"{0}\"")
    public int selectRandomOption(Select select) {
        if (select.getOptions().size() == 0) {
            fail("В селекторе нет опций");
        }
        int pos = new Random().nextInt(select.getOptions().size());
        select.selectByIndex(pos);
        return pos;
    }

    @Step("Select random option in \"{0}\" after pos {1}")
    public int selectRandomOption(Select select, int from) {
        if (from < 0) {
            throw new IllegalArgumentException("from must be greater than or equal to 0");
        }
        if (select.getOptions().size() < from) {
            fail("В селекторе недостаточно опций: всего " + select.getOptions().size() + ", а надо не меньше " + from);
        }
        int pos = new Random().nextInt(select.getOptions().size() - from) + from;
        select.selectByIndex(pos);
        return pos;
    }

    @Step("In \"{0}\" select element with value {1}")
    public String selectRandom(SettingsSelect settingsSelect) {
        Select select = settingsSelect.getSelect();

        List<String> values = select.getOptions().stream()
                .map(e -> e.getAttribute("value"))
                .collect(Collectors.toList());

        String currentLang = settingsSelect.getSelectedOption();
        int currentIndex = values.indexOf(currentLang);

        if (currentIndex >= 0) {
            int targetIndex = (currentIndex + 1) % values.size();
            settingsSelect.button.click();
            settingsSelect.popup.items.get(targetIndex).click();
            return values.get(targetIndex);
        }

        throw new RuntimeException("Some shit happened");
    }

    //todo: use matchers!
    @Step("Should see option {1} is selected in \"{0}\"")
    public void shouldSeeOptionIsSelected(Select select, int pos) {
        assertThat("Позиция элемента выходит за рамки массива", pos,
                allOf(greaterThanOrEqualTo(0), lessThan(select.getOptions().size())));
        assertTrue("Опция " + pos + " не выбрана", select.getOptions().get(pos).isSelected());
    }

    //todo: use matchers!
    @Step("Should see option {1} is not selected in \"{0}\"")
    public void shouldSeeOptionIsNotSelected(Select select, int pos) {
        assertThat("Позиция элемента выходит за рамки массива", pos,
                allOf(greaterThanOrEqualTo(0), lessThan(select.getOptions().size())));
        assertFalse("Опция " + pos + " выбрана", select.getOptions().get(pos).isSelected());
    }

    @Step("Set language \"{0}\"")
    public void setsLanguage(Language lang) {
        setLanguage(driver, lang);
    }

    @Step("Set language on .com \"{0}\"")
    public void setsLanguageOnCom(Language lang) {
        setLanguageOnCom(driver, lang);
    }

    @Step("Get size of list \"{0}\"")
    public int getSize(List list) {
        return list.size();
    }

    @Step("Get size of select \"{0}\"")
    public int getSize(Select select) {
        return select.getOptions().size();
    }

    @Step("Get text of element \"{0}\"")
    public String getElementText(WrapsElement element) {
        return element.getWrappedElement().getText();
    }


    @Step("Get text of element \"{0}\"")
    public String getElementText(HtmlElement element) {
        return element.getText();
    }

    @Step("Should see selected element \"{0}\"")
    public void shouldSeeElementIsSelected(WrapsElement element) {
        assertTrue(element + "должен быть выбран!", element.getWrappedElement().isSelected());
    }

    @Step("Should see not selected element \"{0}\"")
    public void shouldSeeElementIsNotSelected(WrapsElement element) {
        assertFalse(element + "не должен быть выбран!", element.getWrappedElement().isSelected());
    }

    //todo: can we use matchers here?
    @Step("Should see selected element \"{0}\"")
    public void shouldSeeElementIsSelected(HtmlElement element) {
        assertTrue(element + " должен быть выбран (активен)!", element.isSelected());
    }

    //todo: can we use matchers here?
    @Step("Should see not selected element \"{0}\"")
    public void shouldSeeElementIsNotSelected(HtmlElement element) {
        assertFalse(element + " не должен быть выбран (активен)!", element.isSelected());
    }

    @Step("Find element in \"{0}\" that fits {2}")
    public <T, E> T findFirst(List<T> list, E element, Matcher<? super E> matcher) {
        return selectFirst(list, having(element, matcher));
    }

    @Step("Find all elements in \"{0}\" that fits {2}")
    public <T, E> List<T> find(List<T> list, E element, Matcher<? super E> matcher) {
        return select(list, having(element, matcher));
    }

    @Step("Find element in \"{0}\" that fits {1}")
    public <T> T findFirst(List<T> list, Matcher<? super T> matcher) {
        return selectFirst(list, matcher);
    }

    @Step("Find all elements in \"{0}\" that fits {1}")
    public <T> List<T> find(List<T> list, Matcher<? super T> matcher) {
        return select(list, matcher);
    }

    @Step
    public <T> T getRandomItem(List<T> list) {
        assertThat("Нет доступных элементов", list, withWaitFor(hasSize(greaterThan(0))));
        return list.get(new Random().nextInt(list.size()));
    }

    @Step
    public void acceptsAlert() {
        driver.switchTo().alert().accept();
    }

    @Step("Should see cookie \"{0}\" with value \"{1}\"")
    public void shouldSeeCookie(ru.yandex.autotests.utils.morda.cookie.Cookie cookie, String value) {
        assertThat(CookieManager.getCookie(driver, cookie), equalTo(value));
    }

    @Step("Should see cookie \"{0}\" with value {1}")
    public void shouldSeeCookie(ru.yandex.autotests.utils.morda.cookie.Cookie cookie, Matcher<String> value) {
        assertThat(CookieManager.getCookie(driver, cookie), value);
    }

    @Attachment
    public byte[] screenshot() {
        return ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
    }
    
    @Step
    public void shouldSeeStaticIsDownloaded(Har har) {
        assertThat(har, harResponses());
    }

    @Step
    public void shouldSeeStaticIsDownloaded(Har har, Predicate<HarEntry> harEntryPredicate) {
        assertThat(har, harResponses(harEntryPredicate));
    }

    @Step("Uploads file \"{1}\"")
    public void uploadsFile(HtmlElement fileInput, String filename) {
        try {
            String path = getClass().getClassLoader().getResource(filename).getPath();
            RemoteWebElement element = (RemoteWebElement) fileInput.getWrappedElement().findElement(By.xpath("."));
            String absolutePath = new File(path).getAbsolutePath();
            element.setFileDetector(new LocalFileDetector());
            element.sendKeys(absolutePath);
            assertThat(driver, withWaitFor(contentLoaded()));
        } catch(NullPointerException exception) {
            fail("Файл не был загружен\n" + exception);
        }
    }

    @Step("Add Cookie {1} = {2}")
    public void addCookie(WebDriver driver, Cookie cookie, String value) {
        CookieManager.addCookie(driver, cookie, value);
    }

    @Step("List has items {1}")
    public <T> void shouldSeeItemsInList(List<T> actual, List<T> expected) {
        assertThat(actual, hasSameItemsAsCollection(expected));
    }
    
    @Step("Submit form {0}")
    public void submits(HtmlElement element) {
        element.submit();
    }
}
