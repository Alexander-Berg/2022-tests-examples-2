package com.yandex.tv.home.domain.state.reducer

import com.yandex.tv.home.domain.state.model.CarouselPage
import com.yandex.tv.home.domain.state.model.CarouselPaginationData
import com.yandex.tv.home.domain.state.model.CarouselRequestData
import com.yandex.tv.home.domain.state.model.ContentCarousel
import com.yandex.tv.home.domain.state.model.ContentState
import com.yandex.tv.home.domain.state.model.Screen
import com.yandex.tv.home.domain.state.model.ScreenContentPage
import com.yandex.tv.home.domain.state.model.ScreenContentState
import com.yandex.tv.home.domain.state.model.ScreenRequestData
import com.yandex.tv.home.model.Category
import com.yandex.tv.home.model.ContentItem
import com.yandex.tv.home.model.vh.VhLibraryItem

internal class TestContentStateReducerHelper {

    private val reducerHelper = ContentStateReducerHelper()

    fun createSampleContentState(
        items: List<ContentItem> = emptyList(),
        addTargetScreenRequest: Boolean = false,
        addTargetCarouselRequest: Boolean = false
    ): ContentState {
        return createScreensState {
            addScreen(ScreenContentState.Ready(emptyList()))
            addScreen(ScreenContentState.Progress)
            addReadyScreen { requestData ->
                addCarousel(requestData)
                addCarousel(requestData, items)
                addCarousel(requestData)
                addCarousel(requestData, generateItems())
            }
            addScreen(ScreenContentState.Ready(emptyList()))
            addScreen(ScreenContentState.Error(IllegalStateException()))
            addScreen(ScreenContentState.Progress)
        }.let { state ->
            val targetScreen = getTargetScreen(state)
            val targetScreenState = targetScreen.contentState as ScreenContentState.Ready
            val screenPageRequests = mutableListOf<ScreenRequestData>()
            if (addTargetScreenRequest) {
                screenPageRequests.add(state.screens[TARGET_SCREEN_INDEX].requestData)
            }
            screenPageRequests.add(state.screens[5].requestData)
            val carouselRequests = mutableListOf<CarouselRequestData>()
            if (addTargetCarouselRequest) {
                carouselRequests.add(targetScreenState.items[TARGET_CAROUSEL_INDEX].requestData)
            }
            carouselRequests.add(targetScreenState.items[3].requestData)
            val screenObservers = state.screens.map { it.requestData }
            state.copy(
                screenPageRequests = screenPageRequests,
                carouselPageRequests = carouselRequests,
                screenObservers = screenObservers
            )
        }
    }

    fun createSampleCarouselPage(carousel: ContentCarousel): CarouselPage {
        val pageItems = generateItems(carousel.items.size)
        val paginationData = carousel.paginationData?.copy(url = "${carousel.paginationData.url}-new")
        return CarouselPage(paginationData, pageItems)
    }

    fun createSampleScreenPage(screen: Screen): ScreenContentPage {
        val requestData = screen.requestData
        val offset = (screen.contentState as? ScreenContentState.Ready)?.items?.size ?: 0
        val items = mutableListOf<ContentCarousel>().apply {
            addCarousel(requestData, offset = offset)
            addCarousel(requestData, generateItems(), offset = offset)
            addCarousel(requestData, offset = offset)
        }
        return ScreenContentPage(nextPageUrl = "${screen.nextPageUrl}-new", items)
    }

    fun getTargetScreen(state: ContentState): Screen {
        return state.screens[TARGET_SCREEN_INDEX]
    }

    fun getTargetCarousel(state: ContentState): ContentCarousel {
        val screen = getTargetScreen(state)
        val screenState = screen.contentState as ScreenContentState.Ready
        return screenState.items[TARGET_CAROUSEL_INDEX]
    }

    fun updateTargetCarousel(state: ContentState, carousel: ContentCarousel): ContentState {
        val screen = getTargetScreen(state)
        val screenState = screen.contentState as ScreenContentState.Ready
        val items = screenState.items
        val updatedItems = reducerHelper.replaceElement(items, TARGET_CAROUSEL_INDEX, carousel)
        val updatedScreen = screen.copy(contentState = ScreenContentState.Ready(updatedItems))
        val updatedScreens = reducerHelper.replaceScreen(state.screens, TARGET_SCREEN_INDEX, updatedScreen)
        return state.copy(screens = updatedScreens)
    }

    fun createSampleCategories(): List<Category> {
        return List(5) { idx ->
            Category("id$idx", "id$idx", null, "title$idx", idx, null)
        }
    }

    private fun createScreensState(block: MutableList<Screen>.() -> Unit): ContentState {
        val items = mutableListOf<Screen>()
        items.block()
        return ContentState(screens = items)
    }

    private fun MutableList<Screen>.addScreen(state: ScreenContentState) {
        val number = size
        val requestData = ScreenRequestData("id$number", null)
        add(Screen(requestData, "url$number", state))
    }

    private fun MutableList<Screen>.addReadyScreen(
        block: MutableList<ContentCarousel>.(requestData: ScreenRequestData) -> Unit
    ) {
        val number = size
        val requestData = ScreenRequestData("id$number", null)
        val items = mutableListOf<ContentCarousel>()
        items.block(requestData)
        val screen = Screen(requestData, "url$number", ScreenContentState.Ready(items))
        add(screen)
    }

    fun generateItems(from: Int = 0): List<ContentItem> {
        return List(10) { idx ->
            VhLibraryItem.createEmpty("id${from + idx}")
        }
    }

    private fun MutableList<ContentCarousel>.addCarousel(
        screenRequestData: ScreenRequestData,
        items: List<ContentItem> = emptyList(),
        offset: Int = 0
    ) {
        val number = offset + size
        val carouselRequestData = CarouselRequestData(screenRequestData, "id$number", null)
        val paginationData = CarouselPaginationData("url$number", "url", "title")
        val carousel = ContentCarousel(
            carouselRequestData,
            "title$number",
            paginationData,
            "url$number",
            items,
            true,
            200,
            null,
            number
        )
        add(carousel)
    }

    companion object {

        const val PROGRESS_SCREEN_INDEX = 1
        const val TARGET_SCREEN_INDEX = 2
        const val EMPTY_SCREEN_INDEX = 3
        const val ERROR_SCREEN_INDEX = 4
        const val TARGET_CAROUSEL_INDEX = 1
    }
}
