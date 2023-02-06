package com.yandex.tv.common.utility.ui.tests.rules

import androidx.test.espresso.Espresso.setFailureHandler
import com.yandex.tv.common.utility.ui.tests.CustomFailureHandler
import com.yandex.tv.common.utility.ui.tests.UiObjectHelpers
import org.junit.rules.ExternalResource

class CustomFailureHandlerSetHelper : ExternalResource() {
    override fun before() {
        setFailureHandler(CustomFailureHandler(UiObjectHelpers.sTargetContext))
    }
}