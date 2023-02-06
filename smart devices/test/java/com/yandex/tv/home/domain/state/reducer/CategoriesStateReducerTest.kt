package com.yandex.tv.home.domain.state.reducer

import com.yandex.tv.home.domain.state.data.LocalDataSource
import com.yandex.tv.home.domain.state.data.RemoteDataSource
import com.yandex.tv.home.domain.state.model.CategoriesState
import com.yandex.tv.home.domain.state.model.ContentAction
import com.yandex.tv.home.domain.state.model.ContentState
import com.yandex.tv.home.model.Category
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

class CategoriesStateReducerTest {

    private val helper = TestContentStateReducerHelper()

    private lateinit var localDataSource: LocalDataSource
    private lateinit var remoteDataSource: RemoteDataSource
    private lateinit var testScope: TestScope
    private lateinit var channel: Channel<ContentAction>
    private lateinit var reducer: CategoriesStateReducer

    @Before
    fun setUp() {
        localDataSource = mock()
        remoteDataSource = mock()
        testScope = TestScope()
        channel = Channel()
        reducer = CategoriesStateReducer(localDataSource, remoteDataSource, testScope)
    }

    @After
    fun setDown() {
        testScope.cancel()
        channel.cancel()
    }

    @Test
    fun `Request action, update categories from cache`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val categories = helper.createSampleCategories()
        whenever(localDataSource.getCategories()).thenReturn(categories)

        val actualState = state.reduceRequestAction()

        val expectedState = state.copy(categoriesState = CategoriesState.Ready(categories))
        assertNoMoreOutgoingActions()
        assertEquals(expectedState, actualState)
    }

    @Test
    fun `Request action, network content should call async action`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val categories = helper.createSampleCategories()
        whenever(localDataSource.getCategories()).thenReturn(null)
        whenever(remoteDataSource.getCategories()).thenReturn(categories)

        val actualState = state.reduceRequestAction()

        val expectedState = state.copy(categoriesState = CategoriesState.Progress)
        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Categories.Update(state.dataVersion, categories))
    }

    @Test
    fun `Request action, cache error should start network request`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val categories = helper.createSampleCategories()
        whenever(localDataSource.getCategories()).thenAnswer { throw IOException() }
        whenever(remoteDataSource.getCategories()).thenReturn(categories)

        val actualState = state.reduceRequestAction()

        val expectedState = state.copy(categoriesState = CategoriesState.Progress)
        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Categories.Update(state.dataVersion, categories))
    }

    @Test
    fun `Request action, network error should call async action`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val error = IOException()
        whenever(localDataSource.getCategories()).thenReturn(null)
        whenever(remoteDataSource.getCategories()).thenAnswer { throw error }

        val actualState = state.reduceRequestAction()

        val expectedState = state.copy(categoriesState = CategoriesState.Progress)
        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Categories.FailUpdate(state.dataVersion, error))
    }

    @Test
    fun `Request action, duplicate request should be ignored`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val categories = helper.createSampleCategories()
        whenever(localDataSource.getCategories()).thenReturn(null)
        whenever(remoteDataSource.getCategories()).thenReturn(categories)

        val updatedState = state.reduceRequestAction()

        val expectedState = state.copy(categoriesState = CategoriesState.Progress)
        assertEquals(expectedState, updatedState)

        val actualState = reducer.reduce(ContentAction.Categories.Request, updatedState, channel)

        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Categories.Update(state.dataVersion, categories))
    }

    @Test
    fun `Request action, update idle state`() = testScope.runTest {
        val state = helper.createSampleContentState().copy(categoriesState = CategoriesState.Idle)
        val categories = helper.createSampleCategories()
        whenever(localDataSource.getCategories()).thenReturn(categories)

        val actualState = state.reduceRequestAction()

        val expectedState = state.copy(categoriesState = CategoriesState.Ready(categories))
        assertEquals(expectedState, actualState)
    }

    @Test
    fun `Request action, update error state`() = testScope.runTest {
        val state = helper.createSampleContentState().copy(categoriesState = CategoriesState.Error(IOException()))
        val categories = helper.createSampleCategories()
        whenever(localDataSource.getCategories()).thenReturn(categories)

        val actualState = state.reduceRequestAction()

        val expectedState = state.copy(categoriesState = CategoriesState.Ready(categories))
        assertEquals(expectedState, actualState)
    }

    @Test
    fun `Request action, progress state should ignore request`() = testScope.runTest {
        val state = helper.createSampleContentState().copy(categoriesState = CategoriesState.Progress)
        val categories = helper.createSampleCategories()
        whenever(localDataSource.getCategories()).thenReturn(categories)

        val actualState = state.reduceRequestAction()

        assertEquals(state, actualState)
    }

    @Test
    fun `Request action, ready state should ignore request`() = testScope.runTest {
        val state = helper.createSampleContentState()
            .copy(categoriesState = CategoriesState.Ready(helper.createSampleCategories()))
        val categories = helper.createSampleCategories()
        whenever(localDataSource.getCategories()).thenReturn(categories)

        val actualState = state.reduceRequestAction()

        assertEquals(state, actualState)
    }

    @Test
    fun `Update action, update content and store to cache`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val categories = helper.createSampleCategories()

        val actualState = state.reduceUpdateAction(categories)

        val expectedState = state.copy(categoriesState = CategoriesState.Ready(categories))
        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
        verifyBlocking(localDataSource, times(1)) { putCategories(categories) }
        verifyNoMoreInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `Update action, cache error should update just state`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val categories = helper.createSampleCategories()
        whenever(localDataSource.putCategories(categories)).thenAnswer { throw IOException() }

        val actualState = state.reduceUpdateAction(categories)

        val expectedState = state.copy(categoriesState = CategoriesState.Ready(categories))
        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
        verifyBlocking(localDataSource, times(1)) { putCategories(categories) }
        verifyNoMoreInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `FailUpdate action, should setup error state`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val error = IOException()

        val actualState = state.reduceFailUpdateAction(error)

        val expectedState = state.copy(categoriesState = CategoriesState.Error(error))
        assertEquals(expectedState, actualState)
        assertNoMoreOutgoingActions()
        verifyNoInteractions(localDataSource, remoteDataSource)
    }

    private suspend fun ContentState.reduceRequestAction(): ContentState {
        return reducer.reduce(ContentAction.Categories.Request, this, channel)
    }

    private suspend fun ContentState.reduceUpdateAction(categories: List<Category>): ContentState {
        return reducer.reduce(ContentAction.Categories.Update(dataVersion, categories), this, channel)
    }

    private suspend fun ContentState.reduceFailUpdateAction(error: Throwable): ContentState {
        return reducer.reduce(ContentAction.Categories.FailUpdate(dataVersion, error), this, channel)
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
