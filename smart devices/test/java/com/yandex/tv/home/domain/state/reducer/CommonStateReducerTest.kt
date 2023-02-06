package com.yandex.tv.home.domain.state.reducer

import com.yandex.io.sdk.environment.TandemRole
import com.yandex.tv.home.domain.state.data.LocalDataSource
import com.yandex.tv.home.domain.state.model.CategoriesState
import com.yandex.tv.home.domain.state.model.ContentAction
import com.yandex.tv.home.domain.state.model.ContentState
import com.yandex.tv.home.domain.state.model.Screen
import com.yandex.tv.home.domain.state.model.ScreenContentState
import kotlinx.coroutines.cancel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.advanceTimeBy
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
import kotlin.test.assertTrue

class CommonStateReducerTest {

    private val helper = TestContentStateReducerHelper()

    private lateinit var localDataSource: LocalDataSource
    private lateinit var testScope: TestScope
    private lateinit var channel: Channel<ContentAction>
    private lateinit var reducer: CommonStateReducer

    @Before
    fun setUp() {
        localDataSource = mock()
        testScope = TestScope()
        channel = Channel()
        reducer = CommonStateReducer(localDataSource, testScope)
    }

    @After
    fun setDown() {
        testScope.cancel()
        channel.cancel()
    }

    @Test
    fun `Reset action`() = runTest {
        val tandemRole = TandemRole.STAND_ALONE
        val state = helper.createSampleContentState().copy()
        whenever(localDataSource.getTandemRole()).thenReturn(tandemRole)

        val testJob = testScope.launch { delay(TEST_JOB_TIMER_MS) }
        val actualState = reducer.reduce(ContentAction.Common.Reset, state)

        val expectedState = getExpectedState(state, tandemRole)
        assertEquals(expectedState, actualState)
        assertTrue(testJob.isCancelled)
        verifyBlocking(localDataSource, times(1)) { getTandemRole() }
        verifyNoMoreInteractions(localDataSource)
    }

    @Test
    fun `Reset action, tandem error should be handled with null value`() = runTest {
        val state = helper.createSampleContentState().copy()
        whenever(localDataSource.getTandemRole()).thenAnswer { throw IOException() }

        val testJob = testScope.launch { delay(TEST_JOB_TIMER_MS) }
        val actualState = reducer.reduce(ContentAction.Common.Reset, state)

        val expectedState = getExpectedState(state, null)
        assertEquals(expectedState, actualState)
        assertTrue(testJob.isCancelled)
        verifyBlocking(localDataSource, times(1)) { getTandemRole() }
        verifyNoMoreInteractions(localDataSource)
    }

    @Test
    fun `Invalidate action`() = runTest {
        val tandemRole = TandemRole.STAND_ALONE
        val state = helper.createSampleContentState().copy()
        whenever(localDataSource.getTandemRole()).thenReturn(tandemRole)

        val testJob = testScope.launch { delay(TEST_JOB_TIMER_MS) }
        val actualState = reducer.reduce(ContentAction.Common.Invalidate, state)

        val expectedState = getExpectedState(state, tandemRole)
        assertEquals(expectedState, actualState)
        assertTrue(testJob.isCancelled)
        verifyBlocking(localDataSource, times(1)) { getTandemRole() }
        verifyBlocking(localDataSource, times(1)) { clearContent() }
        verifyNoMoreInteractions(localDataSource)
    }

    @Test
    fun `Invalidate action, cache error should update just state`() = runTest {
        val tandemRole = TandemRole.STAND_ALONE
        val state = helper.createSampleContentState().copy()
        whenever(localDataSource.getTandemRole()).thenReturn(tandemRole)
        whenever(localDataSource.clearContent()).thenAnswer { throw IOException() }

        val testJob = testScope.launch { delay(TEST_JOB_TIMER_MS) }
        val actualState = reducer.reduce(ContentAction.Common.Invalidate, state)

        val expectedState = getExpectedState(state, tandemRole)
        assertEquals(expectedState, actualState)
        assertTrue(testJob.isCancelled)
        verifyBlocking(localDataSource, times(1)) { getTandemRole() }
        verifyBlocking(localDataSource, times(1)) { clearContent() }
        verifyNoMoreInteractions(localDataSource)
    }

    @Test
    fun `Invalidate action, tandem error should be handled with null value`() = runTest {
        val state = helper.createSampleContentState().copy()
        whenever(localDataSource.getTandemRole()).thenAnswer { throw IOException() }

        val testJob = testScope.launch { delay(TEST_JOB_TIMER_MS) }
        val actualState = reducer.reduce(ContentAction.Common.Invalidate, state)

        val expectedState = getExpectedState(state, null)
        assertEquals(expectedState, actualState)
        assertTrue(testJob.isCancelled)
        verifyBlocking(localDataSource, times(1)) { getTandemRole() }
        verifyBlocking(localDataSource, times(1)) { clearContent() }
        verifyNoMoreInteractions(localDataSource)
    }

    @Test
    fun `UpdateTandemRole action`() = runTest {
        val tandemRole = TandemRole.STAND_ALONE
        val state = helper.createSampleContentState()

        val testJob = testScope.launch { delay(TEST_JOB_TIMER_MS) }
        val actualState = reducer.reduce(ContentAction.Common.UpdateTandemRole(tandemRole), state)

        val expectedState = getExpectedState(state, tandemRole)
        assertEquals(expectedState, actualState)
        assertTrue(testJob.isCancelled)
        verifyBlocking(localDataSource, times(1)) { setTandemRole(tandemRole) }
        verifyBlocking(localDataSource, times(1)) { clearContent() }
        verifyNoMoreInteractions(localDataSource)
    }

    @Test
    fun `UpdateTandemRole action, fail to store tandem role should continue flow`() = runTest {
        val tandemRole = TandemRole.STAND_ALONE
        val state = helper.createSampleContentState()
        whenever(localDataSource.setTandemRole(tandemRole)).thenAnswer { throw IOException() }

        val testJob = testScope.launch { delay(TEST_JOB_TIMER_MS) }
        val actualState = reducer.reduce(ContentAction.Common.UpdateTandemRole(tandemRole), state)

        val expectedState = getExpectedState(state, tandemRole)
        assertEquals(expectedState, actualState)
        assertTrue(testJob.isCancelled)
        verifyBlocking(localDataSource, times(1)) { setTandemRole(tandemRole) }
        verifyBlocking(localDataSource, times(1)) { clearContent() }
        verifyNoMoreInteractions(localDataSource)
    }

    @Test
    fun `UpdateTandemRole action, same tandem role should keep current content`() = runTest {
        val tandemRole = TandemRole.STAND_ALONE
        val state = helper.createSampleContentState().copy(tandemRole = tandemRole)

        val testJob = testScope.launch { delay(TEST_JOB_TIMER_MS) }
        val actualState = reducer.reduce(ContentAction.Common.UpdateTandemRole(tandemRole), state)
        testScope.advanceTimeBy(TEST_JOB_TIMER_MS)
        testScope.runCurrent()

        assertEquals(state, actualState)
        assertTrue(testJob.isCompleted)
        verifyNoInteractions(localDataSource)
    }

    private fun getExpectedState(state: ContentState, tandemRole: TandemRole?): ContentState {
        val expectedScreens = state.screens.map { screen ->
            Screen(
                requestData = screen.requestData,
                nextPageUrl = null,
                contentState = ScreenContentState.Progress
            )
        }
        return ContentState(
            dataVersion = state.dataVersion + 1,
            categoriesState = CategoriesState.Idle,
            screens = expectedScreens,
            tandemRole = tandemRole,
            screenPageRequests = emptyList(),
            carouselPageRequests = emptyList(),
            screenObservers = state.screenObservers
        )
    }

    private companion object {

        private const val TEST_JOB_TIMER_MS = 10_000L
    }
}
