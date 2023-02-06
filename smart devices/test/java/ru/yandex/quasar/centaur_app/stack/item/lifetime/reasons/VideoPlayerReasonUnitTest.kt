package ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.test.runBlockingTest
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseCoroutinesUnitTest
import ru.yandex.quasar.centaur_app.video.VideoPlayerEvent

@RunWith(RobolectricTestRunner::class)
class VideoPlayerReasonUnitTest: BaseCoroutinesUnitTest() {
    @Test
    fun `when receiving thin audio player events update acitivity state accordingly`() {
        val collected = ArrayList<Boolean>()
        val videoPlayerEvents = MutableSharedFlow<VideoPlayerEvent>()
        val reason = VideoPlayerReason(
            videoPlayerEvents = videoPlayerEvents,
            coroutineScope = coroutineScope
        )
        coroutineScope.launch {
            reason.flow().collect {
                collected.add(it)
            }
        }
        runBlockingTest {
            val statesToCheck = listOf(
                VideoPlayerEvent.PlaybackStarted("1"),
                VideoPlayerEvent.PlaybackStopped("1"),
                VideoPlayerEvent.PlaybackStarted("1"),
                VideoPlayerEvent.PlaybackStarted("2"),
                VideoPlayerEvent.PlaybackStopped("1"),
                VideoPlayerEvent.PlaybackStopped("2")
            )
            for (stateToCheck in statesToCheck) {
                videoPlayerEvents.emit(stateToCheck)
            }
            testDispatcher.advanceUntilIdle()
            assert(collected.size == 4)
            assert(collected[0])
            assert(!collected[1])
            assert(collected[2])
            assert(!collected[3])
        }
    }
}
