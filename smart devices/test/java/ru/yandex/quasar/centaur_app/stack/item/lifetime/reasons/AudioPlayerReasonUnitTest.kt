package ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.test.runBlockingTest
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseCoroutinesUnitTest
import ru.yandex.quasar.protobuf.ModelObjects

@RunWith(RobolectricTestRunner::class)
class AudioPlayerReasonUnitTest: BaseCoroutinesUnitTest() {
    @Test
    fun `when receiving thin audio player events update acitivity state accordingly`() {
        val collected = ArrayList<Boolean>()
        val audioPlayerEvents = MutableSharedFlow<ModelObjects.AudioClientEvent>()
        val reason = AudioPlayerReason(audioPlayerThinEvents = audioPlayerEvents)
        coroutineScope.launch {
            reason.flow().collect {
                collected.add(it)
            }
        }
        runBlockingTest {
            val statesToCheck = listOf(
                ModelObjects.AudioClientState.PLAYING,
                ModelObjects.AudioClientState.BUFFERING,
                ModelObjects.AudioClientState.FAILED,
                ModelObjects.AudioClientState.FINISHED,
                ModelObjects.AudioClientState.IDLE,
                ModelObjects.AudioClientState.PAUSED,
                ModelObjects.AudioClientState.STOPPED
            )
            for (stateToCheck in statesToCheck) {
                audioPlayerEvents.emit(ModelObjects.AudioClientEvent.newBuilder().setState(stateToCheck).build())
            }
            testDispatcher.advanceUntilIdle()
            assert(collected.size == 7)
            assert(collected[0])
            assert(collected[1])
            assert(!collected[2])
            assert(!collected[3])
            assert(!collected[4])
            assert(!collected[5])
            assert(!collected[6])
        }
    }
}
