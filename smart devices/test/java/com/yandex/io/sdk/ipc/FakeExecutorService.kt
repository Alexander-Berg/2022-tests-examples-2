package com.yandex.io.sdk.ipc

import java.util.concurrent.AbstractExecutorService
import java.util.concurrent.TimeUnit

class FakeExecutorService: AbstractExecutorService() {
    override fun execute(command: Runnable) {
        command.run()
    }

    override fun shutdown() {
    }

    override fun shutdownNow(): MutableList<Runnable> {
        return mutableListOf()
    }

    override fun isShutdown(): Boolean {
        return false
    }

    override fun isTerminated(): Boolean {
        return false
    }

    override fun awaitTermination(timeout: Long, unit: TimeUnit?): Boolean {
        return false
    }
}
