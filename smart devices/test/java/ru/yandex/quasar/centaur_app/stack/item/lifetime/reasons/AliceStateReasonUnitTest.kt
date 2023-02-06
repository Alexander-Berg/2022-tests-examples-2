package ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.test.runBlockingTest
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseCoroutinesUnitTest
import ru.yandex.quasar.protobuf.ModelObjects

@RunWith(RobolectricTestRunner::class)
class AliceStateReasonUnitTest: BaseCoroutinesUnitTest() {
    @Test
    fun `when alice state machine performs transitions report it to activity flow`() {
        val collected = ArrayList<Boolean>()
        val aliceStateFlow = MutableSharedFlow<ModelObjects.AliceState>()
        val reason = AliceStateReason(aliceStateFlow = aliceStateFlow)
        coroutineScope.launch {
            reason.flow().collect {
                collected.add(it)
            }
        }
        runBlockingTest {
            val statesToCheck = listOf(
                ModelObjects.AliceState.State.IDLE,
                ModelObjects.AliceState.State.LISTENING,
                ModelObjects.AliceState.State.BUSY,
                ModelObjects.AliceState.State.SPEAKING,
                ModelObjects.AliceState.State.SHAZAM,
                ModelObjects.AliceState.State.NONE
            )
            for (stateToCheck in statesToCheck) {
                aliceStateFlow.emit(ModelObjects.AliceState.newBuilder().setState(stateToCheck).build())
            }
            testDispatcher.advanceUntilIdle()
            assert(collected.size == 6)
            assert(!collected[0])
            assert(collected[1])
            assert(collected[2])
            assert(collected[3])
            assert(collected[4])
            assert(!collected[5])
        }
    }
}
