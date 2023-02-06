package com.yandex.tv.common.utility.ui.tests.rules

import com.yandex.tv.common.utility.ui.tests.ConditionWatcher
import com.yandex.tv.common.utility.ui.tests.ConditionWatcherInstruction
import com.yandex.tv.common.utility.ui.tests.SystemHelpers
import org.junit.rules.ExternalResource

class WaitForLaunchActivityRule : ExternalResource() {

    @Throws(Throwable::class)
    override fun before() {
        ConditionWatcher.waitForCondition(StartAppIdlingResourceInstruction())
    }

    class StartAppIdlingResourceInstruction : ConditionWatcherInstruction() {
        override val description = "App should be visible in activity"
        override fun checkCondition(): Boolean {
            return SystemHelpers.currentActivity != null
        }
    }
}