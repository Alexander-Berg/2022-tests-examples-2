package com.yandex.tv.common.utility.ui.tests.espresso

import android.os.SystemClock
import android.view.View
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.UiController
import androidx.test.espresso.ViewAction
import androidx.test.espresso.action.ViewActions
import androidx.test.espresso.matcher.ViewMatchers
import androidx.test.espresso.util.TreeIterables
import com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.DEFAULT_TIMEOUT_BETWEEN_ACTIONS
import org.hamcrest.Matcher
import org.junit.Assert

object EspressoViewActions {
    /**
     * Perform action of waiting for a specific view id.
     */
    private fun waitFor(viewMatcher: Matcher<View?>): ViewAction {
        return object : ViewAction {
            override fun getConstraints(): Matcher<View> {
                return ViewMatchers.isRoot()
            }

            override fun getDescription(): String {
                return ("wait for a specific view with id $viewMatcher during $DEFAULT_TIMEOUT_BETWEEN_ACTIONS millis.")
            }

            override fun perform(uiController: UiController, view: View) {
                uiController.loopMainThreadUntilIdle()
                val startTime = SystemClock.elapsedRealtime()
                val endTime: Long = startTime + DEFAULT_TIMEOUT_BETWEEN_ACTIONS
                do {
                    for (child in TreeIterables.breadthFirstViewTraversal(view)) {
                        // found view with required ID
                        if (viewMatcher.matches(child)) {
                            return
                        }
                    }
                    uiController.loopMainThreadForAtLeast(50)
                } while (SystemClock.elapsedRealtime() < endTime)

                // timeout happens
                Assert.fail("Element is not found: $viewMatcher")
            }
        }
    }

    fun clickButton(viewMatcher: Matcher<View?>) {
        onView(ViewMatchers.isRoot()).perform(waitFor(viewMatcher))
        onView(viewMatcher).perform(ViewActions.click())
    }
}