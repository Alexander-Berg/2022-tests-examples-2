package ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.test.runBlockingTest
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseCoroutinesUnitTest
import ru.yandex.quasar.centaur_app.ui.interaction.UserInteraction

@RunWith(RobolectricTestRunner::class)
class UserInteractionReasonUnitTest: BaseCoroutinesUnitTest() {
    @Test
    fun `when touch user interaction is emitted make the activity impulse`() {
        val collected = ArrayList<Boolean>()
        val userInteractions = MutableSharedFlow<UserInteraction>()
        val reason = UserInteractionReason(
            userInteractions = userInteractions,
            coroutineScope = coroutineScope
        )
        coroutineScope.launch {
            reason.flow().collect {
                collected.add(it)
            }
        }
        runBlockingTest {
            userInteractions.emit(UserInteraction(UserInteraction.Type.TOUCH_DOWN))
            userInteractions.emit(UserInteraction(UserInteraction.Type.TOUCH_UP))
            userInteractions.emit(UserInteraction(UserInteraction.Type.DIV))
            testDispatcher.advanceUntilIdle()
            assert(collected.size == 2)
            assert(collected[0])
            assert(!collected[1])
        }
    }
}
