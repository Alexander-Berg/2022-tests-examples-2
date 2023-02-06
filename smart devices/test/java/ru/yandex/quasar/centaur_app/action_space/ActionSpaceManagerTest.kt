package ru.yandex.quasar.centaur_app.action_space

import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.yield
import org.junit.Assert.assertEquals
import org.junit.Test
import ru.yandex.quasar.centaur_app.BaseTest
import ru.yandex.quasar.centaur_app.directives.Directive

class ActionSpaceManagerTest: BaseTest() {

    @Test
    fun `send space action after new id`() = runTest {

        var lastAction: String? = null
        val actionSpaceManager = ActionSpaceManager(
            directives = flowOf(
                Directive.UpdateSpaceActions("{\"id1\": \"action1\", \"id2\": \"action2\"}")
            ),
            coroutineScope = this,
            activeActionSender = { lastAction = it }
        )
        yield()
        assertEquals(null, lastAction)

        actionSpaceManager.onActionSpaceIdChanged("id1")
        assertEquals("action1", lastAction)

        actionSpaceManager.onActionSpaceIdChanged("unknown_id")
        assertEquals(null, lastAction)

        actionSpaceManager.onActionSpaceIdChanged("id2")
        assertEquals("action2", lastAction)

        actionSpaceManager.onActionSpaceIdChanged(null)
        assertEquals(null, lastAction)
    }

}
