package com.yandex.tv.common.utility.ui.tests

import android.content.Context
import android.view.View
import androidx.test.espresso.AmbiguousViewMatcherException
import androidx.test.espresso.AppNotIdleException
import androidx.test.espresso.FailureHandler
import androidx.test.espresso.NoActivityResumedException
import androidx.test.espresso.PerformException
import androidx.test.espresso.base.DefaultFailureHandler
import androidx.test.uiautomator.StaleObjectException
import com.yandex.tv.common.utility.ui.tests.SystemHelpers.takeScreenshot
import junit.framework.TestCase.fail
import org.hamcrest.Matcher

class CustomFailureHandler(targetContext: Context?) : FailureHandler {

    private val delegate: FailureHandler

    override fun handle(error: Throwable, viewMatcher: Matcher<View>) {
        try {
            delegate.handle(error, viewMatcher)
        } catch (e: NoSuchElementException) {
            takeScreenshot("NoSuchElementException")
            fail(String.format("View %s is not found!", viewMatcher))
        } catch (e: PerformException) {
            takeScreenshot("PerformException")
            fail(String.format("Error performing on view '%s'!", viewMatcher))
        } catch (e: AmbiguousViewMatcherException) {
            takeScreenshot("AmbiguousViewMatcherException")
            fail(String.format("View %s matches multiple views in the hierarchy!", viewMatcher))
        } catch (e: AppNotIdleException) {
            takeScreenshot("AppNotIdleException")
            fail("AppNotIdleException: $e")
        } catch (e: StaleObjectException) {
            takeScreenshot("StaleObjectException")
            fail("StaleObjectException: $e")
        } catch (e: NoActivityResumedException) {
            takeScreenshot("NoActivityResumedException")
            fail(String.format("No activities in stage RESUMED, while searching for %s!", viewMatcher))
        }
    }

    init {
        delegate = DefaultFailureHandler(targetContext)
    }
}