package com.yandex.tv.home.domain.state

import com.yandex.tv.home.di.CoroutineDispatchers
import com.yandex.tv.home.domain.state.model.CarouselPaginationData
import com.yandex.tv.home.domain.state.model.CarouselRequestData
import com.yandex.tv.home.domain.state.model.CategoriesState
import com.yandex.tv.home.domain.state.model.ContentAction
import com.yandex.tv.home.domain.state.model.ContentCarousel
import com.yandex.tv.home.domain.state.model.ContentState
import com.yandex.tv.home.domain.state.model.Screen
import com.yandex.tv.home.domain.state.model.ScreenContentPage
import com.yandex.tv.home.domain.state.model.ScreenContentState
import com.yandex.tv.home.domain.state.model.ScreenRequestData
import com.yandex.tv.home.domain.state.reducer.ContentStateReducer
import com.yandex.tv.home.model.Category
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.channels.SendChannel
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.Test
import kotlin.test.assertEquals

class ContentStateStoreTest {

    @Test
    fun passEqualsVersion() = runStoreTest(TEST_VERSION) { store, reducer ->
        val action = ContentAction.Categories.Update(TEST_VERSION, emptyList())
        store.sendAction(action)
        assertEquals(listOf(action), reducer.actions)
    }

    @Test
    fun failHigherVersion() = runStoreTest(TEST_VERSION) { store, reducer ->
        val version = TEST_VERSION + 1
        val action = ContentAction.Categories.Update(version, emptyList())
        store.sendAction(action)
        assertEquals(emptyList(), reducer.actions)
    }

    @Test
    fun failLowerVersion() = runStoreTest(TEST_VERSION) { store, reducer ->
        val version = TEST_VERSION - 1
        val action = ContentAction.Categories.Update(version, emptyList())
        store.sendAction(action)
        assertEquals(emptyList(), reducer.actions)
    }

    @Test
    fun passUnversionedAction() = runStoreTest(ContentAction.UNVERSIONED) { store, reducer ->
        val action = ContentAction.Common.Invalidate
        store.sendAction(action)
        assertEquals(listOf(action), reducer.actions)
    }

    @Test
    fun awaitCompletableAction() = runStoreTest { store, _ ->
        val action = ContentAction.Common.Invalidate
        store.sendAction(action)
        action.await()
    }

    @Test
    fun updateCategories() = runStoreTest { store, _ ->
        assertEquals(CategoriesState.Idle, store.observeCategories().first())
        val category = Category("id", "id", null, "title", 1, null)
        val categories = listOf(category)
        val action = ContentAction.Categories.Update(ContentAction.UNVERSIONED, categories)
        store.sendAction(action)
        assertEquals(CategoriesState.Ready(categories), store.observeCategories().first())
    }

    @Test
    fun updateScreenContentState() = runStoreTest { store, _ ->
        assertEquals(CategoriesState.Idle, store.observeCategories().first())
        val screenRequestData = ScreenRequestData("id", null)
        val carouselRequestData = CarouselRequestData(screenRequestData, "id", null)
        val paginationData = CarouselPaginationData("url", "url", "title")
        val carousel =
            ContentCarousel(carouselRequestData, "title", paginationData, null, emptyList(), true, 0, null, 0)
        val carousels = listOf(carousel)
        val page = ScreenContentPage("url", carousels)
        val action = ContentAction.Screen.AddPage(ContentAction.UNVERSIONED, screenRequestData, 0, page)
        store.sendAction(action)
        assertEquals(ScreenContentState.Ready(carousels), store.observeScreensState(screenRequestData).first())
    }

    private inline fun runStoreTest(
        dataVersion: Long = ContentAction.UNVERSIONED,
        crossinline block: suspend TestScope.(store: ContentStateStore, reducer: TestReducer) -> Unit
    ) {
        runTest {
            val reducer = TestReducer(dataVersion)
            val dispatcher = UnconfinedTestDispatcher(testScheduler)
            val dispatchers = CoroutineDispatchers(Dispatchers.Main, dispatcher, dispatcher)
            val storeContext = SupervisorJob()
            val store = ContentStateStore(reducer, dispatchers, storeContext)
            block(store, reducer)
            storeContext.cancelAndJoin()
        }
    }

    private class TestReducer(private val dataVersion: Long) : ContentStateReducer {

        val actions: List<ContentAction> get() = _actions.toList()
        private val _actions = mutableListOf<ContentAction>()

        override suspend fun getDefaultState(): ContentState {
            return ContentState(
                dataVersion = dataVersion
            )
        }

        override suspend fun reduce(
            action: ContentAction,
            state: ContentState,
            channel: SendChannel<ContentAction>
        ): ContentState {
            _actions.add(action)
            return when (action) {
                is ContentAction.Categories.Update -> state.copy(
                    categoriesState = CategoriesState.Ready(action.categories)
                )
                is ContentAction.Screen.AddPage -> state.copy(
                    screens = listOf(
                        Screen(
                            action.requestData,
                            action.page.nextPageUrl,
                            ScreenContentState.Ready(action.page.items)
                        )
                    )
                )
                else -> state
            }
        }
    }

    private companion object {

        private const val TEST_VERSION = 200L
    }
}
