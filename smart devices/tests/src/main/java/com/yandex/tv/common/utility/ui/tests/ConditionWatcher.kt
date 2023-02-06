package com.yandex.tv.common.utility.ui.tests

import java.lang.Exception

class ConditionWatcher private constructor() {
    enum class Status {
        CONDITION_NOT_MET, CONDITION_MET, TIMEOUT
    }

    private var timeoutLimit = DEFAULT_TIMEOUT_LIMIT
    private var watchInterval = DEFAULT_INTERVAL

    companion object {
        const val DEFAULT_TIMEOUT_LIMIT = 1000 * 60
        const val DEFAULT_INTERVAL = 250
        private var conditionWatcher: ConditionWatcher? = null
        val instance: ConditionWatcher?
            get() {
                if (conditionWatcher == null) {
                    conditionWatcher = ConditionWatcher()
                }
                return conditionWatcher
            }

        @Throws(Exception::class)
        fun waitForCondition(instruction: ConditionWatcherInstruction) {
            var status = Status.CONDITION_NOT_MET
            var elapsedTime = 0
            do {
                if (instruction.checkCondition()) {
                    status = Status.CONDITION_MET
                } else {
                    elapsedTime += instance!!.watchInterval
                    Thread.sleep(instance!!.watchInterval.toLong())
                }
                if (elapsedTime >= instance!!.timeoutLimit) {
                    status = Status.TIMEOUT
                    break
                }
            } while (status != Status.CONDITION_MET)
            if (status == Status.TIMEOUT) {
                throw Exception(
                    instruction.description + " - took more than "
                            + instance!!.timeoutLimit / 1000 + " seconds. Test stopped."
                )
            }
        }

        fun setWatchInterval(watchInterval: Int) {
            instance!!.watchInterval = watchInterval
        }

        fun setTimeoutLimit(ms: Int) {
            instance!!.timeoutLimit = ms
        }
    }
}