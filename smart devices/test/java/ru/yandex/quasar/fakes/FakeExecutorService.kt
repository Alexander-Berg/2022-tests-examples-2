package ru.yandex.quasar.fakes

import java.util.*
import java.util.concurrent.Callable
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Future
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.ScheduledFuture
import java.util.concurrent.TimeUnit

@Suppress("MemberVisibilityCanBePrivate")
class FakeExecutorService : ScheduledExecutorService {

    @Volatile
    var isShuttedDown: Boolean = false
        private set

    var items = ConcurrentHashMap<String, ExecutingItem>()

    var terminationLatch = CountDownLatch(1)

    override fun shutdown() {
        isShuttedDown = true
    }

    override fun <T : Any?> submit(task: Callable<T>?): Future<T> {
        if (isShuttedDown) {
            throw RejectedExecutionException("shutted down")
        }

        val future = FakeFuture<T>()
        val key = UUID.randomUUID().toString()
        items[key] = ExecutingItem(Runnable {
            future.item = task?.call()
            future.done = true
            items.remove(key)
        }, future)
        return future
    }

    override fun <T : Any?> submit(task: Runnable?, result: T): Future<T> {
        if (isShuttedDown) {
            throw RejectedExecutionException("shutted down")
        }

        val future = FakeFuture<T>()
        val key = UUID.randomUUID().toString()
        items[key] = ExecutingItem(Runnable {
            task?.run()
            future.item = result
            future.done = true
            items.remove(key)
        }, future)
        return future
    }

    override fun submit(task: Runnable?): Future<*> {
        if (isShuttedDown) {
            throw RejectedExecutionException("shutted down")
        }

        val future = FakeFuture<Boolean>()
        val key = UUID.randomUUID().toString()
        items[key] = ExecutingItem(Runnable {
            task?.run()
            future.item = true
            future.done = true
            items.remove(key)
        }, future)
        return future
    }

    override fun shutdownNow(): MutableList<Runnable> {
        val notCalledItems = ArrayList<Runnable>(items.values.map { t -> t.runnable })
        isShuttedDown = true
        return notCalledItems
    }

    override fun isShutdown(): Boolean {
        return isShuttedDown
    }

    override fun awaitTermination(timeout: Long, unit: TimeUnit?): Boolean {
        if (!isShuttedDown) {
            shutdownNow()
        }

        terminationLatch.await(timeout, unit)

        return false
    }

    override fun <T : Any?> invokeAny(tasks: MutableCollection<out Callable<T>>?): T {
        return invokeAny(tasks, Long.MAX_VALUE, TimeUnit.DAYS)
    }

    @Suppress("ReplaceGuardClauseWithFunctionCall")
    override fun <T : Any?> invokeAny(
        tasks: MutableCollection<out Callable<T>>?,
        timeout: Long,
        unit: TimeUnit?
    ): T {
        if (isShuttedDown) {
            throw RejectedExecutionException("shut down")
        }
        if (tasks == null) {
            throw IllegalArgumentException("tasks")
        }

        val future = FakeFuture<T>()
        val key = UUID.randomUUID().toString()
        for ((index, task) in tasks.withIndex()) {
            items[key + index] = ExecutingItem(Runnable {
                future.item = task.call()
                future.done = true
                items.remove(key + index)
            }, future)
        }

        return future.get(timeout, unit)
    }

    override fun isTerminated(): Boolean {
        return isShuttedDown && items.isEmpty()
    }

    override fun <T : Any?> invokeAll(tasks: MutableCollection<out Callable<T>>?): MutableList<Future<T>> {
        return invokeAll(tasks, Long.MAX_VALUE, TimeUnit.DAYS)
    }

    @Suppress("ReplaceGuardClauseWithFunctionCall")
    override fun <T : Any?> invokeAll(
        tasks: MutableCollection<out Callable<T>>?,
        timeout: Long,
        unit: TimeUnit?
    ): MutableList<Future<T>> {
        if (isShuttedDown) {
            throw RejectedExecutionException("shut down")
        }
        if (tasks == null) {
            throw IllegalArgumentException("tasks")
        }

        val futures = ArrayList<Future<T>>()
        for (task in tasks) {
            val future = FakeFuture<T>()
            val key = UUID.randomUUID().toString()
            items[key] = ExecutingItem(Runnable {
                future.item = task.call()
                future.done = true
                items.remove(key)
            }, future)
            futures.add(future)
        }

        return futures
    }

    override fun execute(command: Runnable?) {
        val key = UUID.randomUUID().toString()
        items[key] = ExecutingItem(Runnable {
            command?.run()
            items.remove(key)
        }, null)
    }

    override fun schedule(command: Runnable?, delay: Long, unit: TimeUnit?): ScheduledFuture<*> {
        if (isShuttedDown) {
            throw RejectedExecutionException("shutted down")
        }

        val future = FakeScheduledFuture<Boolean>(delay, unit)
        val key = UUID.randomUUID().toString()
        items[key] = ExecutingItem(Runnable {
            command?.run()
            future.item = true
            future.done = true
            items.remove(key)
        }, future)
        return future
    }

    override fun <V : Any?> schedule(
        callable: Callable<V>?,
        delay: Long,
        unit: TimeUnit?
    ): ScheduledFuture<V> {
        if (isShuttedDown) {
            throw RejectedExecutionException("shut down")
        }

        val future = FakeScheduledFuture<V>(delay, unit)
        val key = UUID.randomUUID().toString()
        items[key] = ExecutingItem(Runnable {
            future.item = callable?.call()
            future.done = true
            items.remove(key)
        }, future)
        return future
    }

    override fun scheduleAtFixedRate(
        command: Runnable?,
        initialDelay: Long,
        period: Long,
        unit: TimeUnit?
    ): ScheduledFuture<*> {
        if (isShuttedDown) {
            throw RejectedExecutionException("shut down")
        }

        val future = FakeScheduledFuture<Boolean>(initialDelay, unit)
        val key = UUID.randomUUID().toString()
        var startedAt = System.currentTimeMillis() + TimeUnit.MILLISECONDS.convert(
            initialDelay,
            unit ?: TimeUnit.SECONDS
        )
        items[key] = ExecutingItem(Runnable {
            if (future.item == null)
                future.item = true
            val now = System.currentTimeMillis()
            val stride = now - startedAt
            val periodInMS = TimeUnit.MILLISECONDS.convert(period, unit ?: TimeUnit.SECONDS)
            val count = stride / periodInMS
            for (i in 0..count) {
                command?.run()
            }
            startedAt += count * periodInMS
        }, future)
        return future
    }

    override fun scheduleWithFixedDelay(
        command: Runnable?,
        initialDelay: Long,
        delay: Long,
        unit: TimeUnit?
    ): ScheduledFuture<*> {
        // NOTE: this is not precisely correct, but with 'invoke it yourself' nature of fakes it is a good approximation
        return scheduleAtFixedRate(command, initialDelay, delay, unit)
    }

    fun runAllJobs() {
        for (item in items) {
            item.value.runnable.run()
        }
    }


    /**
     * Run all jobs while can.
     * If one of jobs will create another job, the job will be executed too
     */
    fun runAllJobsRecursive() {
        while (items.isNotEmpty()) {
            runAllJobs()
        }
    }

    data class ExecutingItem(val runnable: Runnable, val future: Future<*>?)
}
