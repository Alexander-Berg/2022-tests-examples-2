package ru.yandex.quasar.fakes

import java.util.concurrent.*

@Suppress("MemberVisibilityCanBePrivate")
open class FakeFuture<T> : Future<T> {

    // NOTE: done, not isDone, because it clashes with Future.isDone
    var done: Boolean = false

    private var _item: T? = null
    var latch = CountDownLatch(1)

    private var wasCancelled: Boolean = false

    var item: T?
        get() {
            return _item
        }
        set(newValue) {
            _item = newValue
            latch.countDown()
        }

    override fun isDone(): Boolean {
        return done
    }

    override fun get(): T {
        return get(Long.MAX_VALUE, TimeUnit.DAYS)
    }

    override fun get(timeout: Long, unit: TimeUnit?): T {
        val itemCopy = item
        if (itemCopy != null)
            return itemCopy

        latch.await(timeout, unit)

        val itemCopy2 = item
        if (itemCopy2 != null)
            return itemCopy2

        throw if (wasCancelled) CancellationException() else ExecutionException(Exception())
    }

    override fun cancel(mayInterruptIfRunning: Boolean): Boolean {
        wasCancelled = true
        latch.countDown()
        return true
    }

    override fun isCancelled(): Boolean {
        return wasCancelled
    }
}
