package com.yandex.tv.home.domain.state.reducer

import com.yandex.tv.home.domain.state.data.LocalDataSource
import com.yandex.tv.home.domain.state.data.RemoteDataSource
import com.yandex.tv.home.domain.state.model.ContentAction
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
import org.mockito.kotlin.doAnswer
import org.mockito.kotlin.mock
import org.mockito.kotlin.times
import org.mockito.kotlin.verifyBlocking
import org.mockito.kotlin.verifyNoInteractions
import org.mockito.kotlin.verifyNoMoreInteractions
import org.mockito.kotlin.whenever
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class CarouselStateReducerTest {

    private val helper = TestContentStateReducerHelper()

    private lateinit var localDataSource: LocalDataSource
    private lateinit var remoteDataSource: RemoteDataSource
    private lateinit var testScope: TestScope
    private lateinit var channel: Channel<ContentAction>
    private lateinit var reducer: CarouselStateReducer

    @Before
    fun setUp() {
        localDataSource = mock()
        remoteDataSource = mock()
        testScope = TestScope()
        channel = Channel()
        reducer = CarouselStateReducer(localDataSource, remoteDataSource, testScope)
    }

    @After
    fun setDown() {
        testScope.cancel()
        channel.cancel()
    }

    @Test
    fun `RequestNextPage action, update empty carousel from cache`() = testScope.runTest {
        val state = helper.createSampleContentState()
        val carousel = helper.getTargetCarousel(state)
        val page = helper.createSampleCarouselPage(carousel)
        whenever(localDataSource.getCarouselPage(carousel, 0)).thenReturn(page)

        val actualState =
            reducer.reduce(ContentAction.Carousel.RequestNextPage(carousel.requestData), state, channel)

        val expectedCarousel = carousel.copy(
            paginationData = page.paginationData,
            items = page.items
        )
        val expectedState = helper.updateTargetCarousel(state, expectedCarousel)
        assertNoMoreOutgoingActions()
        assertEquals(expectedState, actualState)
    }

    @Test
    fun `RequestNextPage action, update filled carousel from cache`() = testScope.runTest {
        val items = helper.generateItems()
        val state = helper.createSampleContentState(items)
        val carousel = helper.getTargetCarousel(state)
        val page = helper.createSampleCarouselPage(carousel)
        whenever(localDataSource.getCarouselPage(carousel, items.size)).thenReturn(page)

        val actualState =
            reducer.reduce(ContentAction.Carousel.RequestNextPage(carousel.requestData), state, channel)

        val expectedCarousel = carousel.copy(
            paginationData = page.paginationData,
            items = carousel.items + page.items
        )
        val expectedState = helper.updateTargetCarousel(state, expectedCarousel)
        assertNoMoreOutgoingActions()
        assertEquals(expectedState, actualState)
    }

    @Test
    fun `RequestNextPage action, network content should call async action`() = testScope.runTest {
        val items = helper.generateItems()
        val state = helper.createSampleContentState(items)
        val carousel = helper.getTargetCarousel(state)
        val page = helper.createSampleCarouselPage(carousel)
        val offset = items.size
        whenever(localDataSource.getCarouselPage(carousel, offset)).thenReturn(null)
        whenever(remoteDataSource.getCarouselPage(carousel, offset)).thenReturn(page)

        val actualState =
            reducer.reduce(ContentAction.Carousel.RequestNextPage(carousel.requestData), state, channel)

        val expectedState = state.copy(carouselPageRequests = state.carouselPageRequests + carousel.requestData)
        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Carousel.AddPage(state.dataVersion, carousel, offset, page))
    }

    @Test
    fun `RequestNextPage action, network error should call async action`() = testScope.runTest {
        val items = helper.generateItems()
        val state = helper.createSampleContentState(items)
        val carousel = helper.getTargetCarousel(state)
        val offset = items.size
        whenever(localDataSource.getCarouselPage(carousel, offset)).thenReturn(null)
        val error = IOException()
        whenever(remoteDataSource.getCarouselPage(carousel, offset)).thenAnswer { throw error }

        val actualState =
            reducer.reduce(ContentAction.Carousel.RequestNextPage(carousel.requestData), state, channel)

        val expectedState = state.copy(carouselPageRequests = state.carouselPageRequests + carousel.requestData)
        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Carousel.FailUpdate(state.dataVersion, carousel.requestData, error))
    }

    @Test
    fun `RequestNextPage action, duplicate request should be ignored`() = testScope.runTest {
        val items = helper.generateItems()
        val state = helper.createSampleContentState(items)
        val carousel = helper.getTargetCarousel(state)
        val page = helper.createSampleCarouselPage(carousel)
        val offset = items.size
        whenever(localDataSource.getCarouselPage(carousel, offset)).thenReturn(null)
        whenever(remoteDataSource.getCarouselPage(carousel, offset)).thenReturn(page)

        val updatedState =
            reducer.reduce(ContentAction.Carousel.RequestNextPage(carousel.requestData), state, channel)

        val expectedState = state.copy(carouselPageRequests = state.carouselPageRequests + carousel.requestData)
        assertEquals(expectedState, updatedState)

        val actualState =
            reducer.reduce(ContentAction.Carousel.RequestNextPage(carousel.requestData), updatedState, channel)

        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Carousel.AddPage(state.dataVersion, carousel, offset, page))
    }

    @Test
    fun `RequestNextPage action, cache error should request update from network`() = testScope.runTest {
        val items = helper.generateItems()
        val state = helper.createSampleContentState(items)
        val carousel = helper.getTargetCarousel(state)
        val page = helper.createSampleCarouselPage(carousel)
        val offset = items.size
        whenever(localDataSource.getCarouselPage(carousel, offset)).doAnswer { throw IOException() }
        whenever(remoteDataSource.getCarouselPage(carousel, offset)).thenReturn(page)

        val actualState =
            reducer.reduce(ContentAction.Carousel.RequestNextPage(carousel.requestData), state, channel)

        val expectedState = state.copy(carouselPageRequests = state.carouselPageRequests + carousel.requestData)

        assertEquals(expectedState, actualState)
        assertOutgoingActions(ContentAction.Carousel.AddPage(state.dataVersion, carousel, offset, page))
    }

    @Test
    fun `RequestNextPage action, missing screen case should ignore request`() = testScope.runTest {
        val items = helper.generateItems()
        val state = helper.createSampleContentState(items)
        val carousel = helper.getTargetCarousel(state)

        val missingScreenList = state.screens.take(TestContentStateReducerHelper.TARGET_SCREEN_INDEX) +
                state.screens.drop(TestContentStateReducerHelper.TARGET_SCREEN_INDEX + 1)
        val missingScreenState = state.copy(screens = missingScreenList)
        val actualState =
            reducer.reduce(ContentAction.Carousel.RequestNextPage(carousel.requestData), missingScreenState, channel)

        assertEquals(missingScreenState, actualState)
        verifyNoInteractions(localDataSource, remoteDataSource)
    }

    @Test
    fun `AddPage action, update empty carousel`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetCarouselRequest = true)
        val carousel = helper.getTargetCarousel(state)
        val page = helper.createSampleCarouselPage(carousel)
        val offset = 0

        val action = ContentAction.Carousel.AddPage(state.dataVersion, carousel, offset, page)
        val actualState = reducer.reduce(action, state, channel)

        val expectedCarousel = carousel.copy(
            paginationData = page.paginationData,
            items = carousel.items + page.items
        )
        val expectedState = helper.updateTargetCarousel(state, expectedCarousel)
            .copy(carouselPageRequests = state.carouselPageRequests.filter { it != carousel.requestData })

        assertNoMoreOutgoingActions()
        assertEquals(expectedState, actualState)
        verifyBlocking(localDataSource, times(1)) { addCarouselPage(carousel, page, offset) }
        verifyNoMoreInteractions(remoteDataSource, localDataSource)
    }

    @Test
    fun `AddPage action, update filled carousel`() = testScope.runTest {
        val items = helper.generateItems()
        val state = helper.createSampleContentState(items, addTargetCarouselRequest = true)
        val carousel = helper.getTargetCarousel(state)
        val page = helper.createSampleCarouselPage(carousel)
        val offset = items.size

        val action = ContentAction.Carousel.AddPage(state.dataVersion, carousel, offset, page)
        val actualState = reducer.reduce(action, state, channel)

        val expectedCarousel = carousel.copy(
            paginationData = page.paginationData,
            items = carousel.items + page.items
        )
        val expectedState = helper.updateTargetCarousel(state, expectedCarousel)
            .copy(carouselPageRequests = state.carouselPageRequests.filter { it != carousel.requestData })

        assertNoMoreOutgoingActions()
        assertEquals(expectedState, actualState)
        verifyBlocking(localDataSource, times(1)) { addCarouselPage(carousel, page, offset) }
        verifyNoMoreInteractions(remoteDataSource, localDataSource)
    }

    @Test
    fun `AddPage action, store error should update just state`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetCarouselRequest = true)
        val carousel = helper.getTargetCarousel(state)
        val page = helper.createSampleCarouselPage(carousel)
        val offset = 0
        whenever(localDataSource.addCarouselPage(carousel, page, offset)).thenAnswer { throw IOException() }

        val action = ContentAction.Carousel.AddPage(state.dataVersion, carousel, 0, page)
        val actualState = reducer.reduce(action, state, channel)

        val expectedCarousel = carousel.copy(
            paginationData = page.paginationData,
            items = carousel.items + page.items
        )
        val expectedState = helper.updateTargetCarousel(state, expectedCarousel)
            .copy(carouselPageRequests = state.carouselPageRequests.filter { it != carousel.requestData })

        assertNoMoreOutgoingActions()
        assertEquals(expectedState, actualState)
        verifyBlocking(localDataSource, times(1)) { addCarouselPage(carousel, page, offset) }
        verifyNoMoreInteractions(remoteDataSource, localDataSource)
    }

    @Test
    fun `AddPage action, missing screen case should store content to cache`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetCarouselRequest = true)
        val carousel = helper.getTargetCarousel(state)
        val page = helper.createSampleCarouselPage(carousel)
        val offset = 0

        val missingScreenList = state.screens.take(TestContentStateReducerHelper.TARGET_SCREEN_INDEX) +
                state.screens.drop(TestContentStateReducerHelper.TARGET_SCREEN_INDEX + 1)
        val missingScreenState = state.copy(screens = missingScreenList)
        val action = ContentAction.Carousel.AddPage(state.dataVersion, carousel, offset, page)
        val actualState = reducer.reduce(action, missingScreenState, channel)

        val expectedRequests = missingScreenState.carouselPageRequests.filter { it != carousel.requestData }
        val expectedState = missingScreenState.copy(carouselPageRequests = expectedRequests)
        assertNoMoreOutgoingActions()
        assertEquals(expectedState, actualState)
        verifyBlocking(localDataSource) { addCarouselPage(carousel, page, offset) }
        verifyNoMoreInteractions(remoteDataSource, localDataSource)
    }

    @Test
    fun `FailUpdate action, should drop async request`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetCarouselRequest = true)
        val carousel = helper.getTargetCarousel(state)

        val action = ContentAction.Carousel.FailUpdate(state.dataVersion, carousel.requestData, IOException())
        val actualState = reducer.reduce(action, state, channel)

        val expectedState =
            state.copy(carouselPageRequests = state.carouselPageRequests.filter { it != carousel.requestData })

        assertNoMoreOutgoingActions()
        assertEquals(expectedState, actualState)
        verifyNoMoreInteractions(remoteDataSource, localDataSource)
    }

    @Test
    fun `FailUpdate action, missing screen case should drop async request`() = testScope.runTest {
        val state = helper.createSampleContentState(addTargetCarouselRequest = true)
        val carousel = helper.getTargetCarousel(state)

        val missingScreenList = state.screens.take(TestContentStateReducerHelper.TARGET_SCREEN_INDEX) +
                state.screens.drop(TestContentStateReducerHelper.TARGET_SCREEN_INDEX + 1)
        val missingScreenState = state.copy(screens = missingScreenList)
        val action = ContentAction.Carousel.FailUpdate(state.dataVersion, carousel.requestData, IOException())
        val actualState = reducer.reduce(action, missingScreenState, channel)

        val expectedRequests = missingScreenState.carouselPageRequests.filter { it != carousel.requestData }
        val expectedState = missingScreenState.copy(carouselPageRequests = expectedRequests)
        assertNoMoreOutgoingActions()
        assertEquals(expectedState, actualState)
        verifyNoMoreInteractions(remoteDataSource, localDataSource)
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
