package ru.yandex.quasar.centaur_app.stack.item.lifetime

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runBlockingTest
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseCoroutinesUnitTest
import ru.yandex.quasar.centaur_app.utils.Timeout
import ru.yandex.quasar.centaur_app.utils.time.milliseconds
import ru.yandex.quasar.centaur_app.utils.time.minutes
import ru.yandex.quasar.centaur_app.utils.extensions.or

@RunWith(RobolectricTestRunner::class)
class LifetimeCheckerUnitTest: BaseCoroutinesUnitTest() {
    @Test
    fun `when no activity signal is dispatched expire`() {
        runBlockingTest {
            val checker = LifetimeChecker(
                isActiveReasons = flowOf(),
                inactivityTimeout = Timeout.Finite(3.milliseconds),
                coroutineScope = coroutineScope
            )
            testDispatcher.advanceTimeBy(4.milliseconds.milliseconds)
            assert(!checker.activeState.value) { "Must be not active" }
            assert(checker.expiredState.value) { "Must be expired" }
        }
    }

    @Test
    fun `when no activity signal is dispatched but timeout is forever don't expire`() {
        runBlockingTest {
            val checker = LifetimeChecker(
                isActiveReasons = flowOf(),
                inactivityTimeout = Timeout.Infinity,
                coroutineScope = coroutineScope
            )
            testDispatcher.advanceTimeBy(1.minutes.milliseconds)
            assert(!checker.activeState.value) { "Must be not active" }
            assert(!checker.expiredState.value) { "Must be not expired" }
        }
    }

    @Test
    fun `when short impulse arrived extend timeout time`() {
        runBlockingTest {
            val flow = MutableSharedFlow<Boolean>()
            val flow2 = MutableSharedFlow<Boolean>()
            val checker = LifetimeChecker(
                isActiveReasons = or(listOf(flow, flow2)),
                inactivityTimeout = Timeout.Finite(3.milliseconds),
                coroutineScope = coroutineScope
            )
            testDispatcher.advanceTimeBy(2.milliseconds.milliseconds)
            flow.emit(true)
            flow.emit(false)
            testDispatcher.advanceTimeBy(2.milliseconds.milliseconds)
            assert(!checker.activeState.value) { "Must not be active" }
            assert(!checker.expiredState.value) { "Must not be expired" }
            testDispatcher.advanceUntilIdle()
        }
    }

    @Test
    fun `when active stops timeout timer`() {
        runBlockingTest {
            val flow = MutableSharedFlow<Boolean>()
            val flow2 = MutableSharedFlow<Boolean>()
            val checker = LifetimeChecker(
                isActiveReasons = or(listOf(flow, flow2)),
                inactivityTimeout = Timeout.Finite(3.milliseconds),
                coroutineScope = coroutineScope
            )
            testDispatcher.advanceTimeBy(2.milliseconds.milliseconds)
            flow.emit(true)
            testDispatcher.advanceTimeBy(2.milliseconds.milliseconds)
            assert(checker.activeState.value) { "Must be active" }
            assert(!checker.expiredState.value) { "Must not be expired" }
            testDispatcher.advanceUntilIdle()
        }
    }

    @Test
    fun `when some activity event is received extend expiration time`() {
        runBlockingTest {
            val isActiveReasonsFlow = MutableStateFlow(false)
            val checker = LifetimeChecker(
                isActiveReasons = isActiveReasonsFlow,
                inactivityTimeout = Timeout.Finite(5.milliseconds),
                coroutineScope = coroutineScope
            )
            testDispatcher.advanceTimeBy(2.milliseconds.milliseconds)
            assert(!checker.activeState.value) { "Must be not active" }
            assert(!checker.expiredState.value) { "Must be not expired" }
            isActiveReasonsFlow.emit(true)
            testDispatcher.advanceTimeBy(1.milliseconds.milliseconds) // t=3
            assert(checker.activeState.value) { "Must be active" }
            assert(!checker.expiredState.value) { "Must not be expired" }
            isActiveReasonsFlow.emit(false)
            testDispatcher.advanceTimeBy(1.milliseconds.milliseconds) // t=4
            assert(!checker.activeState.value) { "Must not be active" }
            assert(!checker.expiredState.value) { "Must not be expired" }
            testDispatcher.advanceTimeBy(9.milliseconds.milliseconds)
            assert(!checker.activeState.value) { "Must not be active" }
            assert(checker.expiredState.value) { "Must be expired" }
        }
    }
}
