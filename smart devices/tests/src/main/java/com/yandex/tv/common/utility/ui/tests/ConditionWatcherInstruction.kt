package com.yandex.tv.common.utility.ui.tests

import android.os.Bundle

abstract class ConditionWatcherInstruction {
    var dataContainer = Bundle()
        private set

    fun setData(dataContainer: Bundle) {
        this.dataContainer = dataContainer
    }

    abstract val description: String?
    abstract fun checkCondition(): Boolean
}