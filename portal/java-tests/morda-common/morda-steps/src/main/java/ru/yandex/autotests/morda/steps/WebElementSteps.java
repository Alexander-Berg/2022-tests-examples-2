package ru.yandex.autotests.morda.steps;

import org.hamcrest.Matcher;
import org.openqa.selenium.internal.WrapsElement;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.CheckBox;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.not;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;
import static ru.yandex.qatools.htmlelements.matchers.TypifiedElementMatchers.isSelected;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.isDisplayed;
import static ru.yandex.qatools.htmlelements.matchers.decorators.MatcherDecoratorsBuilder.should;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08/04/15
 */
public class WebElementSteps {

    private static final long DEFAULT_TIMEOUT = 5000L;

    public static <T extends WrapsElement> Matcher<? super T> withWait(Matcher<? super T> matcher) {
        return withWait(matcher, DEFAULT_TIMEOUT);
    }

    public static <T extends WrapsElement> Matcher<? super T> withWait(Matcher<? super T> matcher,
                                                                       long timeout) {
        return should(matcher).whileWaitingUntil(timeoutHasExpired(timeout));
    }

    public static void clickOnSilently(WrapsElement element) {
        if (element instanceof HtmlElement) {
            ((HtmlElement) element).click();
        } else {
            element.getWrappedElement().click();
        }
    }

    public static void shouldExistSilently(WrapsElement element) {
        shouldExistSilently(element, DEFAULT_TIMEOUT);
    }

    public static void shouldExistSilently(WrapsElement element, boolean toWait) {
        if (toWait) {
            shouldExistSilently(element);
        } else {
            shouldExistSilently(element, 0);
        }
    }

    public static void shouldExistSilently(WrapsElement element, long wait) {
        String errorMessage = format("%s is not found in DOM!", element);
        Matcher<? super WrapsElement> existMatcher = wait > 0
                ? withWait(exists(), wait)
                : exists();

        assertThat(errorMessage, element, existMatcher);
    }

    public static void shouldBeVisibleSilently(WrapsElement element) {
        shouldBeVisibleSilently(element, DEFAULT_TIMEOUT);
    }

    public static void shouldBeVisibleSilently(WrapsElement element, boolean toWait) {
        if (toWait) {
            shouldBeVisibleSilently(element);
        } else {
            shouldBeVisibleSilently(element, 0);
        }
    }

    public static void shouldBeVisibleSilently(WrapsElement element, long wait) {
        String errorMessage = format("%s is not visible!", element);
        Matcher<? super WrapsElement> visibleMatcher = wait > 0
                ? withWait(isDisplayed(), wait)
                : isDisplayed();

        assertThat(errorMessage, element, visibleMatcher);
    }

    public static void shouldSeeSilently(WrapsElement element) {
        shouldExistSilently(element);
        shouldBeVisibleSilently(element);
    }

    public static void shouldSeeSilently(WrapsElement element, boolean toWait) {
        shouldExistSilently(element, toWait);
        shouldBeVisibleSilently(element, toWait);
    }

    public static void shouldSeeSilently(WrapsElement element, long wait) {
        shouldExistSilently(element, wait);
        shouldBeVisibleSilently(element, wait);
    }

    public static void shouldNotSeeSilently(WrapsElement element) {
        String errorMessage = format("\"%s\" should not be visible", element);
        if (exists().matches(element)) {
            assertThat(errorMessage, element, withWait(not(isDisplayed())));
        }
    }

    public static void checkSilently(CheckBox element, boolean isChecked) {
        if (isChecked) {
            checkSilently(element);
        } else {
            uncheckSilently(element);
        }
    }

    public static void checkSilently(CheckBox checkBox) {
        shouldSeeSilently(checkBox);
        checkBox.select();
        String errorMessage = format("\"%s\" must be selected", checkBox);
        assertThat(errorMessage, checkBox, withWait(isSelected()));
    }

    public static void uncheckSilently(CheckBox checkBox) {
        shouldSeeSilently(checkBox);
        checkBox.deselect();
        String errorMessage = format("\"%s\" must be not selected", checkBox);
        assertThat(errorMessage, checkBox, withWait(not(isSelected())));
    }

    @Step
    public static void shouldNotBeChecked(CheckBox checkBox){
        String errorMessage = format("\"%s\" must be not selected", checkBox);
        assertThat(errorMessage, checkBox, withWait(not(isSelected())));
    }

    @Step
    public static void shouldBeChecked(CheckBox checkBox){
        String errorMessage = format("\"%s\" must be selected", checkBox);
        assertThat(errorMessage, checkBox, withWait(isSelected()));
    }

    @Step("Should exist \"{0}\"")
    public static void shouldExist(WrapsElement element) {
        shouldExistSilently(element);
    }

    @Step("Should exist \"{0}\"")
    public static void shouldExist(WrapsElement element, boolean toWait) {
        shouldExistSilently(element, toWait);
    }

    @Step("Should exist \"{0}\"")
    public static void shouldExist(WrapsElement element, long wait) {
        shouldExistSilently(element, wait);
    }

    @Step("Should see \"{0}\"")
    public static void shouldSee(WrapsElement element) {
        shouldSeeSilently(element);
    }

    @Step("Should see \"{0}\"")
    public static void shouldSee(WrapsElement element, boolean toWait) {
        shouldSeeSilently(element, toWait);
    }

    @Step("Should see \"{0}\"")
    public static void shouldSee(WrapsElement element, long wait) {
        shouldSeeSilently(element, wait);
    }

    @Step("Should not see \"{0}\"")
    public static void shouldNotSee(WrapsElement element) {
        shouldNotSeeSilently(element);
    }

    @Step("Click on \"{0}\"")
    public static void clickOn(WrapsElement element) {
        clickOnSilently(element);
    }

    @Step("Click on \"{0}\"")
    public static void clickOn(HtmlElement element) {
        clickOnSilently(element);
    }

    @Step("Check \"{0}\"")
    public static void check(CheckBox element) {
        checkSilently(element, true);
    }

    @Step("Uncheck \"{0}\"")
    public static void uncheck(CheckBox element) {
        checkSilently(element, false);
    }
}
