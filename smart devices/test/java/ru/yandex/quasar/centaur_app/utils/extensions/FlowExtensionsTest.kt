package ru.yandex.quasar.centaur_app.utils.extensions

import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.contains
import org.hamcrest.core.IsEqual
import org.junit.Test
import ru.yandex.quasar.centaur_app.utils.time.seconds

@OptIn(ExperimentalCoroutinesApi::class)
class FlowExtensionsTest {
    @Test
    fun `when nothing emitted to chunked, chunk doesn't emit anything`() = runTest {
        val flow = MutableSharedFlow<Int>()
        val chunkTime = 5.seconds
        var isCollected = false
        val job = launch {
            flow.chunked(chunkTime).collect {
                isCollected = true
            }
        }
        testScheduler.runCurrent()

        testScheduler.advanceTimeBy(chunkTime.milliseconds + 100)
        assert(!isCollected)
        job.cancel()
    }

    @Test
    fun `chunked emits the same values with delay`() = runTest {
        val flow = MutableSharedFlow<Int>()
        val chunkTime = 10.seconds
        val collected = mutableListOf<List<Int>>()

        val job = launch {
            flow.chunked(chunkTime).collect {
                collected.add(it)
            }
        }
        testScheduler.runCurrent()

        val values1 = arrayOf(1, 2, 3)
        values1.forEach {
            flow.emit(it)
            testScheduler.advanceTimeBy(500)
        }
        testScheduler.advanceTimeBy(chunkTime.milliseconds)
        assertThat(collected.size, IsEqual(1))
        assertThat(collected[0], contains(*values1))

        val values2 = arrayOf(4, 5, 6)
        values2.forEach {
            flow.emit(it)
            testScheduler.advanceTimeBy(500)
        }
        testScheduler.advanceTimeBy(chunkTime.milliseconds)
        assertThat(collected.size, IsEqual(2))
        assertThat(collected[1], contains(*values2))

        job.cancel()
    }
}
