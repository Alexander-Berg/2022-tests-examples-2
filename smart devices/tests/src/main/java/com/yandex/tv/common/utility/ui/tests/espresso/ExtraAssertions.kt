package com.yandex.tv.common.utility.ui.tests.espresso

import android.os.SystemClock
import android.view.View
import androidx.test.espresso.AmbiguousViewMatcherException
import androidx.test.espresso.Espresso
import androidx.test.espresso.NoMatchingViewException
import androidx.test.espresso.assertion.ViewAssertions
import androidx.test.espresso.matcher.ViewMatchers
import com.yandex.tv.common.utility.ui.tests.SystemHelpers
import com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.DEFAULT_TIMEOUT_BETWEEN_ACTIONS
import org.hamcrest.Matcher
import org.hamcrest.Matchers
import org.junit.Assert

object ExtraAssertions {

    @SafeVarargs
    fun shouldSee(vararg viewMatcher: Matcher<View?>) {
        shouldSee(DEFAULT_TIMEOUT_BETWEEN_ACTIONS, *viewMatcher)
    }

    @SafeVarargs
    fun shouldSee(timeout: Int, vararg viewMatcher: Matcher<View?>) {
        for (item in viewMatcher) {
            val endTime = SystemClock.elapsedRealtime() + timeout
            var findNext: Boolean
            do {
                try {
                    Espresso.onView(item).check(ViewAssertions.matches(Matchers.allOf(ViewMatchers.isDisplayed())))
                    findNext = true
                    break
                } catch (notDisplayedYet: AssertionError) {
                    findNext = false
                } catch (notDisplayedYet: NoMatchingViewException) {
                    findNext = false
                } catch (notDisplayedYet: AmbiguousViewMatcherException) {
                    findNext = false
                }
            } while (SystemClock.elapsedRealtime() < endTime || findNext)
            if (!findNext) {
                Assert.fail(String.format("View %s is not found!", item))
            }
        }
    }

    @SafeVarargs
    fun shouldNotSee(vararg matcher: Matcher<View?>) {
        for (item in matcher) {
            try {
                Espresso.onView(item).check(ViewAssertions.doesNotExist())
            } catch (notDisplayedYet: AssertionError) {
                Assert.fail("View is found!")
            } catch (notDisplayedYet: NoMatchingViewException) {
                Assert.fail("View is found!")
            } catch (notDisplayedYet: AmbiguousViewMatcherException) {
                Assert.fail("View is found!")
            }
        }
    }

    fun shouldBeSelected(viewMatcher: Matcher<View?>) {
        shouldSee(viewMatcher)
        try {
            Espresso.onView(viewMatcher).check(ViewAssertions.matches(ViewMatchers.isSelected()))
        } catch (notDisplayedYet: AssertionError) {
            Assert.fail(String.format("View %s is not found!", viewMatcher))
        } catch (notDisplayedYet: NoMatchingViewException) {
            Assert.fail(String.format("View %s is not found!", viewMatcher))
        } catch (notDisplayedYet: AmbiguousViewMatcherException) {
            Assert.fail(String.format("View %s is not found!", viewMatcher))
        }
    }
}