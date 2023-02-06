package ru.yandex.quasar.fakes

import java.util.concurrent.Delayed
import java.util.concurrent.ScheduledFuture
import java.util.concurrent.TimeUnit

@Suppress("MemberVisibilityCanBePrivate")
class FakeScheduledFuture<T>(
    val delay: Long,
    val unit: TimeUnit?
) : FakeFuture<T>(), Delayed, ScheduledFuture<T> {
    override fun compareTo(other: Delayed?): Int {
        return 0 // TODO:
    }

    override fun getDelay(unit: TimeUnit?): Long {
        if (unit != null) {
            return unit.convert(delay, this.unit ?: TimeUnit.SECONDS)
        }

        return delay
    }
}
