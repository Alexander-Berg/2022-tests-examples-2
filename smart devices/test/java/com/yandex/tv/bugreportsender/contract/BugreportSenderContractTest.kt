package com.yandex.tv.bugreportsender.contract

import android.content.Intent
import android.os.Looper
import com.yandex.tv.bugreportsender.BugReportCollectorActivity
import com.yandex.tv.common.contract.bugreport.BugreportSenderContract
import com.yandex.tv.common.utility.test.injectActivitySpy
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runBlockingTest
import org.junit.After
import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.spy
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows
import org.robolectric.android.controller.ActivityController
import java.util.concurrent.TimeUnit

@ExperimentalCoroutinesApi
@RunWith(RobolectricTestRunner::class)
class BugreportSenderContractTest {
    private var controller: ActivityController<BugReportCollectorActivity>? = null
    private var activitySpy: BugReportCollectorActivity? = null

    private fun prepareActivity(intent: Intent) {
        controller = Robolectric.buildActivity(BugReportCollectorActivity::class.java, intent)
            .also { controller ->
                activitySpy = spy(controller.get())
                    .also { activity ->
                        injectActivitySpy(controller, activity)
                    }
            }
    }

    private fun launchActivity() {
        controller?.apply {
            create()
            start()
            resume()
            visible()
        }
        Shadows.shadowOf(Looper.getMainLooper()).idleFor(10, TimeUnit.SECONDS)
    }

    private fun destroyActivity() {
        controller?.apply {
            pause()
            stop()
            destroy()
        }
        Shadows.shadowOf(Looper.getMainLooper()).idleFor(10, TimeUnit.SECONDS)
    }

    @After
    fun tearDown() {
        activitySpy = null
        controller = null
    }

    @Test
    fun `launch intent, launch successful`() {
        runBlockingTest {
            val intent = Intent(BugreportSenderContract.ACTION_SEND_REPORT)
            prepareActivity(intent)
            launchActivity()
            Assert.assertNotNull(activitySpy)
            destroyActivity()
        }
    }
}
