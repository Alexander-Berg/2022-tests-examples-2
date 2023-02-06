package com.yandex.tv.home.domain.state.reducer

import com.yandex.tv.home.domain.state.data.LocalDataSource
import com.yandex.tv.home.domain.state.data.RemoteDataSource
import com.yandex.tv.home.domain.state.model.ContentAction
import com.yandex.tv.home.domain.state.model.ContentState
import com.yandex.tv.home.domain.state.model.Screen
import com.yandex.tv.home.domain.state.model.ScreenContentPage
import com.yandex.tv.home.domain.state.model.ScreenContentState
import com.yandex.tv.home.domain.state.model.ScreenRequestData
import kotlinx.coroutines.cancel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.toList
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import okio.IOException
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.times
import org.mockito.kotlin.verifyBlocking
import org.mockito.kotlin.verifyNoInteractions
import org.mockito.kotlin.verifyNoMoreInteractions
import org.mockito.kotlin.whenever
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ScreenStateReducerTest {

    private val helper = TestContentStateReducerHelper()
    private val reducerHelper = ContentStateReducerHelper()

    private lateinit var localDataSource: LocalDataSource
    private lateinit var remoteDataSource: RemoteDataSource
    private lateinit var testScope: TestScope
    private lateinit var channel: Channel<ContentAction>
    private lateinit var reducer: ScreenStateReducer

    @Before
    fun setUp() {
        localDataSource = mock()
        remoteDataSource = mock()
        testScope = TestScope()
        channel = Channel()
        reducer = ScreenStateReducer(localDataSource, remoteDataSource, testScope)
    }

    @After
    fun setDown() {
        testScope.cancel()
        channel.cancel()
    }

    @Test
    fun `RequestNextPage action, update progress state from cache`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val screenIndex = TestContentStateReducerHelper.PROGRESS_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)
        whenever(localDataSource.getScreenContentPage(requestData, screen.nextPageUrl, offset)).thenReturn(page)

        val actualState = state.reduceRequestNextPageAction(requestData)

        val expectedScreen = Screen(screen.requestData, page.nextPageUrl, ScreenContentState.Ready(page.items))
        val expectedState = state.updateScreen(expectedScreen, screenIndex)

        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
    }

    @Test
    fun `RequestNextPage action, update empty ready state from cache`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val screenIndex = TestContentStateReducerHelper.EMPTY_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)
        whenever(localDataSource.getScreenContentPage(requestData, screen.nextPageUrl, offset)).thenReturn(page)

        val actualState = state.reduceRequestNextPageAction(requestData)

        val expectedScreen = Screen(screen.requestData, page.nextPageUrl, ScreenContentState.Ready(page.items))
        val expectedState = state.updateScreen(expectedScreen, screenIndex)

        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
    }

    @Test
    fun `RequestNextPage action, update filled ready state from cache`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val screenIndex = TestContentStateReducerHelper.TARGET_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val items = (screen.contentState as ScreenContentState.Ready).items
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)
        whenever(localDataSource.getScreenContentPage(requestData, screen.nextPageUrl, offset)).thenReturn(page)

        val actualState = state.reduceRequestNextPageAction(requestData)

        val expectedScreen = Screen(screen.requestData, page.nextPageUrl, ScreenContentState.Ready(items + page.items))
        val expectedState = state.updateScreen(expectedScreen, screenIndex)

        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
    }

    @Test
    fun `RequestNextPage action, update error state from cache`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val screenIndex = TestContentStateReducerHelper.ERROR_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)
        whenever(localDataSource.getScreenContentPage(requestData, screen.nextPageUrl, offset)).thenReturn(page)

        val actualState = state.reduceRequestNextPageAction(requestData)

        val expectedScreen = Screen(screen.requestData, page.nextPageUrl, ScreenContentState.Ready(page.items))
        val expectedState = state.updateScreen(expectedScreen, screenIndex)

        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
    }

    @Test
    fun `RequestNextPage action, network content should call async action`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val screenIndex = TestContentStateReducerHelper.PROGRESS_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)
        whenever(localDataSource.getScreenContentPage(requestData, screen.nextPageUrl, offset)).thenReturn(null)
        whenever(remoteDataSource.getScreenContentPage(requestData, screen.nextPageUrl, offset)).thenReturn(page)

        val actualState = state.reduceRequestNextPageAction(requestData)

        val expectedState = state.copy(screenPageRequests = state.screenPageRequests + screen.requestData)

        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Screen.AddPage(state.dataVersion, requestData, offset, page))
    }

    @Test
    fun `RequestNextPage action, cache error should request content from network`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val screenIndex = TestContentStateReducerHelper.PROGRESS_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)
        whenever(localDataSource.getScreenContentPage(requestData, screen.nextPageUrl, offset))
            .thenAnswer { throw IOException() }
        whenever(remoteDataSource.getScreenContentPage(requestData, screen.nextPageUrl, offset)).thenReturn(page)

        val actualState = state.reduceRequestNextPageAction(requestData)

        val expectedState = state.copy(screenPageRequests = state.screenPageRequests + screen.requestData)

        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Screen.AddPage(state.dataVersion, requestData, offset, page))
    }

    @Test
    fun `RequestNextPage action, network error should call async action`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val screenIndex = TestContentStateReducerHelper.PROGRESS_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val error = IOException()
        whenever(localDataSource.getScreenContentPage(requestData, screen.nextPageUrl, offset)).thenReturn(null)
        whenever(remoteDataSource.getScreenContentPage(requestData, screen.nextPageUrl, offset))
            .thenAnswer { throw error }

        val actualState = state.reduceRequestNextPageAction(requestData)

        val expectedState = state.copy(screenPageRequests = state.screenPageRequests + screen.requestData)

        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Screen.FailUpdate(state.dataVersion, requestData, error))
    }

    @Test
    fun `RequestNextPage action, duplicate request should be ignored`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetScreenRequest = true)
        val screenIndex = TestContentStateReducerHelper.TARGET_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData

        val actualState = state.reduceRequestNextPageAction(requestData)

        assertEquals(state, actualState)
        assertNoMoreOutgoingActions()
        verifyNoInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `RequestNextPage action, missing screen case should ignore request`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetScreenRequest = true)
        val requestData = ScreenRequestData("missing-id", null)

        val actualState = state.reduceRequestNextPageAction(requestData)

        assertEquals(state, actualState)
        assertNoMoreOutgoingActions()
        verifyNoInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `AddPage action, update progress state`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetScreenRequest = true)
        val screenIndex = TestContentStateReducerHelper.PROGRESS_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)

        val actualState = state.reduceAddPageAction(requestData, offset, page)

        val expectedScreen = mergeScreen(screen, page)
        val expectedScreens = reducerHelper.replaceScreen(state.screens, screenIndex, expectedScreen)
        val expectedState = state.copy(
            screens = expectedScreens,
            screenPageRequests = state.screenPageRequests.filter { it != screen.requestData }
        )

        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
        verifyBlocking(localDataSource, times(1)) { addScreenContentPage(requestData, page, offset) }
        verifyNoMoreInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `AddPage action, store error should update just state`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetScreenRequest = true)
        val screenIndex = TestContentStateReducerHelper.PROGRESS_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)
        whenever(localDataSource.addScreenContentPage(requestData, page, offset)).thenAnswer { throw IOException() }

        val actualState = state.reduceAddPageAction(requestData, offset, page)

        val expectedScreen = mergeScreen(screen, page)
        val expectedScreens = reducerHelper.replaceScreen(state.screens, screenIndex, expectedScreen)
        val expectedState = state.copy(
            screens = expectedScreens,
            screenPageRequests = state.screenPageRequests.filter { it != screen.requestData }
        )

        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
        verifyBlocking(localDataSource, times(1)) { addScreenContentPage(requestData, page, offset) }
        verifyNoMoreInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `AddPage action, update empty ready state`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetScreenRequest = true)
        val screenIndex = TestContentStateReducerHelper.EMPTY_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)

        val actualState = state.reduceAddPageAction(requestData, offset, page)

        val expectedScreen = mergeScreen(screen, page)
        val expectedScreens = reducerHelper.replaceScreen(state.screens, screenIndex, expectedScreen)
        val expectedState = state.copy(
            screens = expectedScreens,
            screenPageRequests = state.screenPageRequests.filter { it != screen.requestData }
        )

        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
        verifyBlocking(localDataSource, times(1)) { addScreenContentPage(requestData, page, offset) }
        verifyNoMoreInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `AddPage action, update filled ready state`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetScreenRequest = true)
        val screenIndex = TestContentStateReducerHelper.TARGET_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)

        val actualState = state.reduceAddPageAction(requestData, offset, page)

        val expectedScreen = mergeScreen(screen, page)
        val expectedScreens = reducerHelper.replaceScreen(state.screens, screenIndex, expectedScreen)
        val expectedState = state.copy(
            screens = expectedScreens,
            screenPageRequests = state.screenPageRequests.filter { it != screen.requestData }
        )

        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
        verifyBlocking(localDataSource, times(1)) { addScreenContentPage(requestData, page, offset) }
        verifyNoMoreInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `AddPage action, update error state`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetScreenRequest = true)
        val screenIndex = TestContentStateReducerHelper.ERROR_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)

        val actualState = state.reduceAddPageAction(requestData, offset, page)

        val expectedScreen = mergeScreen(screen, page)
        val expectedScreens = reducerHelper.replaceScreen(state.screens, screenIndex, expectedScreen)
        val expectedState = state.copy(
            screens = expectedScreens,
            screenPageRequests = state.screenPageRequests.filter { it != screen.requestData }
        )

        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
        verifyBlocking(localDataSource, times(1)) { addScreenContentPage(requestData, page, offset) }
        verifyNoMoreInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `AddPage action, missing screen case should store content to cache`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetScreenRequest = true)
        val screenIndex = TestContentStateReducerHelper.PROGRESS_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = ScreenRequestData("missing-id", null)
        val offset = getScreenPositionOffset(screen)
        val page = helper.createSampleScreenPage(screen)

        val actualState = state.reduceAddPageAction(requestData, offset, page)

        assertEquals(state, actualState)
        assertNoMoreOutgoingActions()
        verifyBlocking(localDataSource, times(1)) { addScreenContentPage(requestData, page, offset) }
        verifyNoMoreInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `FailUpdate action, should drop async request`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetScreenRequest = true)
        val screenIndex = TestContentStateReducerHelper.ERROR_SCREEN_INDEX
        val screen = state.screens[screenIndex]
        val requestData = screen.requestData
        val error = IOException()

        val actualState = state.reduceFailUpdateAction(requestData, error)

        val expectedScreen = Screen(requestData, screen.nextPageUrl, ScreenContentState.Error(error))
        val expectedScreens = reducerHelper.replaceScreen(state.screens, screenIndex, expectedScreen)
        val expectedState = state.copy(
            screens = expectedScreens,
            screenPageRequests = state.screenPageRequests.filter { it != screen.requestData }
        )

        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
        verifyNoInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `FailUpdate action, missing screen case should drop async request`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetScreenRequest = true)
        val requestData = ScreenRequestData("missing-id", null)
        val error = IOException()

        val actualState = state.reduceFailUpdateAction(requestData, error)

        assertEquals(state, actualState)
        assertNoMoreOutgoingActions()
        verifyNoInteractions(localDataSource, remoteDataSource)
    }

    private suspend fun ContentState.reduceRequestNextPageAction(requestData: ScreenRequestData): ContentState {
        return reducer.reduce(ContentAction.Screen.RequestNextPage(requestData), this, channel)
    }

    private suspend fun ContentState.reduceAddPageAction(
        requestData: ScreenRequestData,
        offset: Int,
        page: ScreenContentPage
    ): ContentState {
        return reducer.reduce(ContentAction.Screen.AddPage(dataVersion, requestData, offset, page), this, channel)
    }

    private suspend fun ContentState.reduceFailUpdateAction(requestData: ScreenRequestData, error: Throwable): ContentState {
        return reducer.reduce(ContentAction.Screen.FailUpdate(dataVersion, requestData, error), this, channel)
    }

    private fun getScreenPositionOffset(screen: Screen): Int {
        return (screen.contentState as? ScreenContentState.Ready)?.items?.lastOrNull()?.rank ?: 0
    }

    private fun ContentState.updateScreen(screen: Screen, index: Int): ContentState {
        val screens = reducerHelper.replaceScreen(screens, index, screen)
        return copy(screens = screens)
    }

    private fun mergeScreen(screen: Screen, page: ScreenContentPage): Screen {
        val items = (screen.contentState as? ScreenContentState.Ready)?.items.orEmpty()
        return Screen(screen.requestData, page.nextPageUrl, ScreenContentState.Ready(items + page.items))
    }

    private fun assertNoMoreOutgoingActions() {
        assertTrue(channel.isEmpty)
    }

    private suspend fun TestScope.assertOutgoingActions(vararg actions: ContentAction) {
        runCurrent()
        channel.close()
        assertFalse(channel.isEmpty)
        val actualActions = channel.toList()
        assertEquals(actions.toList(), actualActions)
    }
}
