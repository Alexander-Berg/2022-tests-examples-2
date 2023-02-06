package ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons

import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert
import org.hamcrest.core.IsEqual
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseCoroutinesUnitTest
import ru.yandex.quasar.centaur_app.videocalls.telegram.calls.TelegramCallInfo
import ru.yandex.quasar.centaur_app.videocalls.telegram.calls.TelegramCallStatus
import kotlin.random.Random

@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(RobolectricTestRunner::class)
class VideoCallReasonUnitTest : BaseCoroutinesUnitTest() {
    @Test
    fun `when receiving video call events update activity state accordingly`() {
        val collected = ArrayList<Boolean>()
        val videoCallEvents = MutableSharedFlow<TelegramCallStatus>()
        val reason = VideoCallReason(
            telegramCallStatusFlow = videoCallEvents
        )
        coroutineScope.launch {
            reason.flow().collect {
                collected.add(it)
            }
        }

        val callInfo = TelegramCallInfo(
            id = Random.nextInt(0, Int.MAX_VALUE),
            recipientId = Random.nextLong(0, Long.MAX_VALUE)
        )
        runTest {
            val statesToCheck = listOf(
                TelegramCallStatus.Ringing(isOutgoing = false, isVideo = false, callInfo = callInfo) to true,
                TelegramCallStatus.Accepted(callInfo) to true,
                TelegramCallStatus.Established(callInfo) to true,
                TelegramCallStatus.HangingUp(callInfo) to true,
                TelegramCallStatus.Discarded(callInfo, TelegramCallStatus.Discarded.Reason.EMPTY) to false,
                TelegramCallStatus.Error(callInfo, errorCode = -1, errorMessage = "some error") to false,
                TelegramCallStatus.None to false,
            )
            for (stateToCheck in statesToCheck) {
                videoCallEvents.emit(stateToCheck.first)
            }
            testDispatcher.scheduler.advanceUntilIdle()
            MatcherAssert.assertThat(collected.size, IsEqual(statesToCheck.size))
            collected.forEachIndexed { index, value ->
                MatcherAssert.assertThat(
                    value,
                    IsEqual(statesToCheck[index].second)
                )
            }
        }
    }
}
