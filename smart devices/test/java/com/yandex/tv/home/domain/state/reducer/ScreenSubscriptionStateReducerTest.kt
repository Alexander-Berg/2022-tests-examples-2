package com.yandex.tv.home.domain.state.reducer

import com.yandex.tv.home.domain.state.model.ContentAction
import com.yandex.tv.home.domain.state.model.Screen
import com.yandex.tv.home.domain.state.model.ScreenContentState
import com.yandex.tv.home.domain.state.model.ScreenRequestData
import kotlinx.coroutines.channels.Channel
import org.junit.After
import org.junit.Before
import org.junit.Test
import kotlin.test.assertEquals

class ScreenSubscriptionStateReducerTest {

    private val helper = TestContentStateReducerHelper()

    private lateinit var channel: Channel<ContentAction>
    private lateinit var reducer: ScreenSubscriptionStateReducer

    @Before
    fun setUp() {
        channel = Channel()
        reducer = ScreenSubscriptionStateReducer()
    }

    @After
    fun setDown() {
        channel.cancel()
    }

    @Test
    fun `Subscribe action, first observer should add screen`() {
        val requestData = ScreenRequestData("test-id", null)
        val state = helper.createSampleContentState()

        val actualState = reducer.reduce(ContentAction.ScreenSubscription.Subscribe(requestData), state)

        val expectedScreen = Screen(requestData, null, ScreenContentState.Progress)
        val expectedState = state.copy(
            screens = state.screens + expectedScreen,
            screenObservers = state.screenObservers + requestData
        )
        assertEquals(expectedState, actualState)
    }

    @Test
    fun `Subscribe action, second observer`() {
        val state = helper.createSampleContentState()
        val targetScreen = helper.getTargetScreen(state)
        val requestData = targetScreen.requestData

        val actualState = reducer.reduce(ContentAction.ScreenSubscription.Subscribe(requestData), state)

        val expectedState = state.copy(
            screenObservers = state.screenObservers + requestData
        )
        assertEquals(expectedState, actualState)
    }

    @Test
    fun `Unsubscribe action, last observer should remove screen`() {
        val state = helper.createSampleContentState()
        val targetScreen = helper.getTargetScreen(state)
        val requestData = targetScreen.requestData

        val actualState = reducer.reduce(ContentAction.ScreenSubscription.Unsubscribe(requestData), state)

        val expectedScreens = state.screens.take(TestContentStateReducerHelper.TARGET_SCREEN_INDEX) +
                state.screens.drop(TestContentStateReducerHelper.TARGET_SCREEN_INDEX + 1)
        val expectedState = state.copy(
            screens = expectedScreens,
            screenObservers = state.screenObservers.filter { it != requestData }
        )
        assertEquals(expectedState, actualState)
    }

    @Test
    fun `Unsubscribe action, second observer`() {
        val sampleState = helper.createSampleContentState().copy()
        val targetScreen = helper.getTargetScreen(sampleState)
        val requestData = targetScreen.requestData
        val state = sampleState.copy(screenObservers = sampleState.screenObservers + requestData)

        val actualState = reducer.reduce(ContentAction.ScreenSubscription.Unsubscribe(requestData), state)

        val expectedState = state.copy(
            screenObservers = state.screenObservers.take(TestContentStateReducerHelper.TARGET_SCREEN_INDEX) +
                    state.screenObservers.drop(TestContentStateReducerHelper.TARGET_SCREEN_INDEX + 1)
        )
        assertEquals(expectedState, actualState)
    }
}
