package ru.yandex.quasar.glagol.impl

import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import org.hamcrest.Matchers.`is`
import org.hamcrest.Matchers.equalTo
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Assert
import org.junit.Test
import ru.yandex.quasar.glagol.Config
import java.io.IOException

class NsdCommandsProcessorTest {

    @Test
    fun testSuccessQueueAllEventsProcessed() {
        val events = ArrayList<Event>()
        val nsdCommandsProcessor = NsdCommandsProcessor(FatedCommandExecutorImpl(Fate.SUCCESS))
        for (i in 1 .. 10) {
            val listener = DummyDiscoveryListener(events)
            nsdCommandsProcessor.start(listener)
            nsdCommandsProcessor.stop(listener)
        }

        val expected = ArrayList<Event>()
        for (i in 1 .. 10) {
            expected.add(Event("start"))
            expected.add(Event("stop"))
        }

        Assert.assertEquals(expected, events)
    }

    @Test
    fun testExceptionOnUnregisteredListener() {
        var exceptionThrown = false
        val nsdCommandsProcessor = NsdCommandsProcessor(FatedCommandExecutorImpl(Fate.FAILURE))
        try {
            nsdCommandsProcessor.stop(DummyDiscoveryListener(mutableListOf()))
        } catch (e: IOException) {
            exceptionThrown = true
        }
        assertThat(exceptionThrown, `is`(true))
    }

    @Test
    fun testFailedQueueAllEventsProcessed() {
        val events = ArrayList<Event>()
        val nsdCommandsProcessor = NsdCommandsProcessor(FatedCommandExecutorImpl(Fate.FAILURE))
        for (i in 1 .. 10) {
            val listener = DummyDiscoveryListener(events)
            nsdCommandsProcessor.start(listener)
        }

        val expected = ArrayList<Event>()
        for (i in 1 .. 10) {
            expected.add(Event("startFail"))
        }

        assertThat(events, equalTo(expected))
    }

    @Test
    fun testRotatingQueue1AllEventsProcessed() {
        val events = ArrayList<Event>()
        val nsdCommandsProcessor = NsdCommandsProcessor(FatedCommandExecutorImpl(Fate.ROTATING))
        for (i in 1 .. 10) {
            val listener = DummyDiscoveryListener(events)
            nsdCommandsProcessor.start(listener)
            nsdCommandsProcessor.stop(listener)
        }

        val expected = ArrayList<Event>()
        for (i in 1 .. 10) {
            expected.add(Event("start"))
            expected.add(Event("stopFail"))
        }

        assertThat(events, equalTo(expected))
    }

    @Test
    fun testRotatingQueue3AllEventsProcessed() {
        val events = ArrayList<Event>()
        val nsdCommandsProcessor = NsdCommandsProcessor(FatedCommandExecutorImpl(Fate.ROTATING))
        for (i in 1 .. 20) {
            nsdCommandsProcessor.start(DummyDiscoveryListener(events))
        }

        val expected = ArrayList<Event>()
        for (i in 1 .. 10) {
            expected.add(Event("start"))
            expected.add(Event("startFail"))
        }

        assertThat(events, equalTo(expected))
    }

    @Test
    fun testRotatingQueue4AllEventsProcessed() {
        val events = ArrayList<Event>()
        val nsdCommandsProcessor = NsdCommandsProcessor(FatedCommandExecutorImpl(Fate.ROTATING))
        for (i in 1 .. 20) {
            val listener = DummyDiscoveryListener(events)
            nsdCommandsProcessor.start(listener)
            nsdCommandsProcessor.stop(listener)
        }

        val expected = ArrayList<Event>()
        for (i in 1 .. 20) {
            expected.add(Event("start"))
            expected.add(Event("stopFail"))
        }

        assertThat(events, equalTo(expected))
    }

    @Test
    fun testAsyncQueueAllEventsProcessed() {
        val events = ArrayList<Event>()
        val nsdCommandsProcessor = NsdCommandsProcessor(FatedCommandExecutorImpl(Fate.SUCCESS, 2))

        val threads = ArrayList<Thread>()
        for (i in 1 .. 20) {
            threads.add(Thread{
                for (j in 1 .. 50) {
                    val listener = DummyDiscoveryListener(events)
                    nsdCommandsProcessor.start(listener)
                    nsdCommandsProcessor.stop(listener)
                }
            })
        }

        threads.forEach { it.start() }

        Thread.sleep(2000)
        assertThat(events.size < 1500, `is`(true))
        Thread.sleep(4000)
        assertThat(events.size, equalTo(2000))
    }


    enum class Fate {
        FAILURE, SUCCESS, ROTATING
    }

    class FatedCommandExecutorImpl(
        private val fate: Fate,
        private val sleepTimeout: Long = 50) : NsdCommandsProcessor.CommandExecutor {
        private val serviceType = Config.DEFAULT_DISCOVERY_SERVICE_TYPE
        private var isSuccessUpcoming: Boolean = false

        private fun isSuccess() = when(fate) {
            Fate.SUCCESS -> true
            Fate.FAILURE -> false
            Fate.ROTATING -> {
                isSuccessUpcoming = !isSuccessUpcoming
                isSuccessUpcoming
            }
        }

        override fun execute(pending: NsdCommandsProcessor.PendingCommand) {
            Thread {
                Thread.sleep(sleepTimeout)
                if (pending.command == NsdCommandsProcessor.Command.START) {
                    if (isSuccess()) {
                        pending.listener.onDiscoveryStarted(serviceType)
                    } else {
                        pending.listener.onStartDiscoveryFailed(serviceType, NsdManager.FAILURE_INTERNAL_ERROR)
                    }
                } else {
                    if (isSuccess()) {
                        pending.listener.onDiscoveryStopped(serviceType)
                    } else {
                        pending.listener.onStopDiscoveryFailed(serviceType, NsdManager.FAILURE_INTERNAL_ERROR)
                    }
                }
            }.run()
        }
    }

    data class Event(
        val name: String) {
        val ts = System.currentTimeMillis()

        override fun equals(other: Any?): Boolean {
            return other is Event && name == other.name
        }

    }

    class DummyDiscoveryListener(val events: MutableList<Event>) : NsdManager.DiscoveryListener {
        override fun onStartDiscoveryFailed(serviceType: String?, errorCode: Int) {
            events.add(Event("startFail"))
            println("onStartDiscoveryFailed err=$errorCode type=$serviceType")
        }

        override fun onStopDiscoveryFailed(serviceType: String?, errorCode: Int) {
            events.add(Event("stopFail"))
            println("onStopDiscoveryFailed err=$errorCode type=$serviceType")
        }

        override fun onDiscoveryStarted(serviceType: String?) {
            events.add(Event("start"))
            println("onDiscoveryStarted type=$serviceType")
        }

        override fun onDiscoveryStopped(serviceType: String?) {
            events.add(Event("stop"))
            println("onDiscoveryStopped type=$serviceType")
        }

        override fun onServiceFound(serviceInfo: NsdServiceInfo?) {
            // unused
        }

        override fun onServiceLost(serviceInfo: NsdServiceInfo?) {
            // unused
        }

    }
}
