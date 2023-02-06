package ru.yandex.quasar.centaur_app.div.actionshandler

import android.net.Uri
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.centaur_app.BaseTest
import ru.yandex.quasar.centaur_app.directives.Directive
import ru.yandex.quasar.centaur_app.stack.contract.Layer
import ru.yandex.quasar.centaur_app.stack.contract.LayerCloser

@RunWith(RobolectricTestRunner::class)
class CentaurDivActionTest: BaseTest() {

    @Test
    fun `when semantic frame directive receive then return unknown directive` () {
        val data = "dialog-action://?directives=%5B%7B%22ignore_answer%22%3Afalse%2C%22is_led_silent%22%3Afalse%2C%22name%22%3A%22%40%40mm_semantic_frame%22%2C%22payload%22%3A%7B%22%40request_id%22%3A%220ba048da-5682-4b3e-8910-6a55fc8f9240%22%2C%22%40scenario_name%22%3A%22CentaurMainScreen%22%2C%22analytics%22%3A%7B%22origin%22%3A%22SmartSpeaker%22%2C%22product_scenario%22%3A%22CentaurMainScreen%22%2C%22purpose%22%3A%22music_play_from_centaur_main_screen%22%7D%2C%22typed_semantic_frame%22%3A%7B%22music_play_semantic_frame%22%3A%7B%22object_id%22%3A%7B%22string_value%22%3A%22503646255%3A30236412%22%7D%2C%22object_type%22%3A%7B%22enum_value%22%3A%22Playlist%22%7D%7D%7D%7D%2C%22type%22%3A%22server_action%22%7D%5D"
        val directives = parseDirectives(data)

        val expected = listOf(
            Directive.Unknown(
                "@@mm_semantic_frame",
                "server_action",
                "{\"@request_id\":\"0ba048da-5682-4b3e-8910-6a55fc8f9240\",\"@scenario_name\":\"CentaurMainScreen\",\"analytics\":{\"origin\":\"SmartSpeaker\",\"product_scenario\":\"CentaurMainScreen\",\"purpose\":\"music_play_from_centaur_main_screen\"},\"typed_semantic_frame\":{\"music_play_semantic_frame\":{\"object_id\":{\"string_value\":\"503646255:30236412\"},\"object_type\":{\"enum_value\":\"Playlist\"}}}}"
            )
        )

        assertEquals(expected, directives)
    }

    @Test
    fun `when directive not exist then return empty list`() {
        val data = "dialog-action://?directives=%5B%5D"
        val directives = parseDirectives(data)

        assertEquals(emptyList<Directive>(), directives)
    }

    @Test
    fun `when parse few known directives then return correctly directive classes`() {
        val data = "dialog-action://?directives=[{\"name\":\"go_home\",\"type\":\"client_action\"},{\"name\":\"player_pause\",\"type\":\"client_action\",\"payload\":\"{}\"}]"
        val directives = parseDirectives(data)
        val expected = listOf(
            Directive.GoHome(),
            Directive.PlayerPause(),
        )

        assertEquals(expected, directives)
    }

    @Test
    fun `stop conversation on layer close by default`() {
        val actions = CentaurDivAction.parse(
            Uri.parse(
                """centaur://local_command?local_commands=[{"command":"close_layer","layer":"CONTENT"}]"""
            )
        )

        val mock = mock<LayerCloser>{}

        (actions.first() as CentaurDivAction.LayerManagerCommand).handle(mock)

        verify(mock).closeLayer(eq(Layer.CONTENT), eq(true), any())
    }

    @Test
    fun `dont stop conversation when closing layer if ordered`() {
        val actions = CentaurDivAction.parse(
            Uri.parse(
                """centaur://local_command?local_commands=[{"command":"close_layer","layer":"CONTENT","stop_conversation":false}]"""
            )
        )

        val mock = mock<LayerCloser>{}

        (actions.first() as CentaurDivAction.LayerManagerCommand).handle(mock)

        verify(mock).closeLayer(eq(Layer.CONTENT), eq(false), any())
    }

    private fun parseDirectives(data: String): List<Directive> {
        val uri = Uri.parse(data)
        val actions = CentaurDivAction.parse(uri)

        if (actions.count() == 0) {
            return emptyList()
        }
        val directiveHandler = actions.first() as CentaurDivAction.DirectiveHandler
        return directiveHandler.parse()
    }
}
