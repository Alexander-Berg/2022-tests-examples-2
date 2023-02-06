package com.yandex.tv.home.domain.state.reducer

import com.yandex.tv.home.domain.state.model.Screen
import com.yandex.tv.home.domain.state.model.ScreenContentState
import com.yandex.tv.home.domain.state.model.ScreenRequestData
import org.junit.Test
import kotlin.test.assertEquals

class ContentStateReducerHelperTest {

    private val helper = ContentStateReducerHelper()

    @Test
    fun `replaceScreen middle position should be moved to first`() {
        val screen1 = createScreen(1)
        val screen2 = createScreen(2)
        val screen3 = createScreen(3)
        val newScreen = createScreen(4)
        val items = listOf(screen1, screen2, screen3)

        val actualItems = helper.replaceScreen(items, 1, newScreen)
        val expectedItems = listOf(newScreen, screen1, screen3)
        assertEquals(expectedItems, actualItems)
    }

    @Test
    fun `replaceScreen first position`() {
        val screen1 = createScreen(1)
        val screen2 = createScreen(2)
        val screen3 = createScreen(3)
        val newScreen = createScreen(4)
        val items = listOf(screen1, screen2, screen3)

        val actualItems = helper.replaceScreen(items, 0, newScreen)
        val expectedItems = listOf(newScreen, screen2, screen3)
        assertEquals(expectedItems, actualItems)
    }

    @Test
    fun `replaceScreen last position should be moved to first`() {
        val screen1 = createScreen(1)
        val screen2 = createScreen(2)
        val screen3 = createScreen(3)
        val newScreen = createScreen(4)
        val items = listOf(screen1, screen2, screen3)

        val actualItems = helper.replaceScreen(items, 2, newScreen)
        val expectedItems = listOf(newScreen, screen1, screen2)
        assertEquals(expectedItems, actualItems)
    }

    @Test
    fun `replaceElement middle position`() {
        val screen1 = createScreen(1)
        val screen2 = createScreen(2)
        val screen3 = createScreen(3)
        val newScreen = createScreen(4)
        val items = listOf(screen1, screen2, screen3)

        val actualItems = helper.replaceElement(items, 1, newScreen)
        val expectedItems = listOf(screen1, newScreen, screen3)
        assertEquals(expectedItems, actualItems)
    }

    @Test
    fun `replaceElement first position`() {
        val screen1 = createScreen(1)
        val screen2 = createScreen(2)
        val screen3 = createScreen(3)
        val newScreen = createScreen(4)
        val items = listOf(screen1, screen2, screen3)

        val actualItems = helper.replaceElement(items, 0, newScreen)
        val expectedItems = listOf(newScreen, screen2, screen3)
        assertEquals(expectedItems, actualItems)
    }

    @Test
    fun `replaceElement last position`() {
        val screen1 = createScreen(1)
        val screen2 = createScreen(2)
        val screen3 = createScreen(3)
        val newScreen = createScreen(4)
        val items = listOf(screen1, screen2, screen3)

        val actualItems = helper.replaceElement(items, 2, newScreen)
        val expectedItems = listOf(screen1, screen2, newScreen)
        assertEquals(expectedItems, actualItems)
    }

    private fun createScreen(number: Int): Screen {
        val requestData = ScreenRequestData("id$number", null)
        return Screen(requestData, "url$number", ScreenContentState.Progress)
    }
}
