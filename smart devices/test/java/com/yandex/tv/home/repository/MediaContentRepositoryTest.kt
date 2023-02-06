package com.yandex.tv.home.repository

import android.content.Context
import android.os.Build
import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.common.utility.test.RxImmediateSchedulerRule
import com.yandex.tv.home.content.MediaContentRepository
import com.yandex.tv.home.content.MediaContentRepositoryImpl
import com.yandex.tv.home.content.local.LocalMediaContentRepositoryImpl
import com.yandex.tv.home.content.remote.RemoteMediaContentRepositoryImpl
import com.yandex.tv.home.di.homeAppModule
import com.yandex.tv.home.model.Carousel
import com.yandex.tv.home.model.CarouselWithFilters
import com.yandex.tv.home.model.Category
import com.yandex.tv.home.model.ContentItem
import com.yandex.tv.home.model.FilterBundle
import com.yandex.tv.home.model.FilterCategory
import com.yandex.tv.home.model.FilterInfo
import com.yandex.tv.home.model.SectionItem
import com.yandex.tv.home.model.vh.VhEpisodeItem
import com.yandex.tv.home.network.HttpRequestTask
import com.yandex.tv.home.network.RestApi
import com.yandex.tv.home.policy.PolicyManager
import com.yandex.tv.home.utils.HttpRequestManager
import com.yandex.tv.home.utils.commonTestModule
import io.reactivex.rxjava3.core.Completable
import io.reactivex.rxjava3.schedulers.Schedulers
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.instanceOf
import org.junit.After
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.rules.Timeout
import org.junit.runner.RunWith
import org.koin.android.ext.koin.androidContext
import org.koin.core.context.startKoin
import org.koin.core.context.stopKoin
import org.koin.test.KoinTest
import org.koin.test.get
import org.mockito.kotlin.any
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.doAnswer
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.eq
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.reset
import org.mockito.kotlin.spy
import org.mockito.kotlin.stub
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.verifyNoInteractions
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit


private const val DROIDEKA_HOST = "https://droideka.tst.smarttv.yandex.net/"

//from response_carousels.json
private const val CAROUSELS_MAIN_MORE_PATH =
    "api/v7/carousels?category_id=main&limit=10&offset=10&cache_hash=egEAAAAAAAAotS_9YHoAzQQAYkwfFoAHYEAYk1lKfRjEZDdpOW_wdlYaaHBjxowZIzBjxowJmCRLqnOdLH3_J0RJF8m-O9ra8CSkaku_L_2vWroopDbXttDOPtuyqhD8855_0a1q5wiietfKbvcMb3ZC7ElJqPejTcs2IXQ1vR-t3rSmuhADhIOBoZBAUFAYACQJmBDq_f8dBxB-Smz5yWPxcEG_vV1ny7kU&max_items_count=10&external_carousel_offset=1"
private const val CAROUSELS_MAIN_CACHE_HASH =
    "egEAAAAAAAAotS_9YHoAzQQAYkwfFoAHYEAYk1lKfRjEZDdpOW_wdlYaaHBjxowZIzBjxowJmCRLqnOdLH3_J0RJF8m-O9ra8CSkaku_L_2vWroopDbXttDOPtuyqhD8855_0a1q5wiietfKbvcMb3ZC7ElJqPejTcs2IXQ1vR-t3rSmuhADhIOBoZBAUFAYACQJmBDq_f8dBxB-Smz5yWPxcEG_vV1ny7kU"

//from response_carousel_*.json
private const val TEST_CAROUSEL_ID =
    "ChJoaGhkbmxtb2FqeWl6eW5kaGgSCXR2YW5kcm9pZBoibW92aWUmZ2VucmVfdGhyaWxsZXImcG9zdGVyX2V4aXN0cyABKAA="
private const val TEST_CATEGORY_ID = "main"
private const val TEST_CAROUSEL_TITLE = "Триллеры"
private const val TEST_CAROUSEL_MORE_PATH_10 =
    "api/v7/carousel?offset=10&limit=10&docs_cache_hash=bQAAAAAAAAAotS_9IG3dAgCUBBIAGAAiADAAOABCXwgPEAsYACJRFwAAAAoAFv__P2ABBgAAADlmXJo1f3Prs-JTIe8HZOTeAEmSSSIO9PT-0TPNKAkwATgASgAGADKDxy2hswWa2FhaFgNj&carousel_id=ChJoaGhkbmxtb2FqeWl6eW5kaGgSCXR2YW5kcm9pZBoibW92aWUmZ2VucmVfdGhyaWxsZXImcG9zdGVyX2V4aXN0cyABKAA%3D"

//from response_carousel_no_offset_filters.json
private const val TEST_FILTERS_CAROUSEL_ID = "CATEG_NAVIGATION_VIDEO"
private const val TEST_FILTERS_CATEGORY_ID = "main"
private const val TEST_FILTERS_CAROUSEL_TITLE = "Фильмы"
private const val TEST_FILTERS_MORE_PATH =
    "api/v7/carousel?carousel_id=CATEG_NAVIGATION_VIDEO&offset=0&limit=10&tag=movie"
private val TEST_FILTERS = listOf(
    FilterInfo("2010-2020", "year=ge:2010,lt:2020", 0),
    FilterInfo("Биография", "genre=ruw267584", 1)
)

//from response_card_details.json
private const val TEST_CONTENT_ID = "493e50ee9414369a86b073e29c81d030"
private const val TEST_CONTENT_TYPE = "vod-episode"

//from response_section_details.json
private const val TEST_SECTION_ID = "CATEG_FILM"
private const val TEST_SECTION_TYPE = "embedded_carousel"

//from response_seasons_no_offset.json
private const val TEST_LIBRARY_ID = "4dbe3685655d2e7e99ea665f4b23ab29"
private const val TEST_SEASON_ID = "4b49cd710f76e67f9871889f1b48823c"
private const val TEST_SEASON_MORE_PATH =
    "api/v6/series/episodes?season_id=4b49cd710f76e67f9871889f1b48823c&offset=1&limit=5"
private const val TEST_SEASONS_MORE_PATH =
    "api/v7/series/seasons?series_id=4dbe3685655d2e7e99ea665f4b23ab29&offset=10&limit=10"


@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], application = RepositoryTestApp::class)
class MediaContentRepositoryTest : KoinTest {
    @Rule
    @JvmField
    val schedulerRule = RxImmediateSchedulerRule()

    @Rule
    @JvmField
    val taskExecutorRule = InstantTaskExecutorRule()

    @Rule
    @JvmField
    var timeout: Timeout = Timeout(20000, TimeUnit.MILLISECONDS)

    private var carouselsMainMoreUrl = ""
    private var testCarouselMoreUrl10 = ""
    private var testFiltersMoreUrl = ""
    private var testSeasonMoreUrl = ""

    private var testSeasonsMoreUrl = ""

    private var callsExecutor = Executors.newSingleThreadExecutor()

    private lateinit var repository: MediaContentRepositoryImpl

    private fun createRepository(): MediaContentRepositoryImpl {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val localRepository = LocalMediaContentRepositoryImpl().apply {
            init(context)
            deleteAllMediaContent()
        }
        val remoteRepository = RemoteMediaContentRepositoryImpl().apply {
            init(context)
            deleteAllMediaContent()
        }
        return MediaContentRepositoryImpl(spy(localRepository), spy(remoteRepository))
    }

    private fun createServer(): MockWebServer {
        return MockWebServer().also {
            it.start()
            RestApi.overrideProxyUrl(it.url("").toString())
            carouselsMainMoreUrl = it.url(CAROUSELS_MAIN_MORE_PATH).toString()
            testCarouselMoreUrl10 = it.url(TEST_CAROUSEL_MORE_PATH_10).toString()
            testFiltersMoreUrl = it.url(TEST_FILTERS_MORE_PATH).toString()
            testSeasonMoreUrl = it.url(TEST_SEASON_MORE_PATH).toString()
            testSeasonsMoreUrl = it.url(TEST_SEASONS_MORE_PATH).toString()
        }
    }

    private fun MockWebServer.enqueueServerResponse(
        responseFileName: String? = null,
        responseCode: Int = 200
    ) {
        val responseBody = responseFileName
            ?.let { fileName ->
                RemoteMediaContentRepositoryTest::class.java.classLoader
                    ?.getResourceAsStream(fileName)
                    ?.use { loadJSONFromResources(it) }
            }
            ?: ""
        enqueue(
            MockResponse()
                .setResponseCode(responseCode)
                .setBody(responseBody)
        )
    }

    @Before
    fun setUp() {
        startKoin {
            androidContext(ApplicationProvider.getApplicationContext())
            modules(listOf(homeAppModule, repositoryTestModule, commonTestModule))
        }
        callsExecutor.shutdownNow()
        callsExecutor = Executors.newSingleThreadExecutor()
        Schedulers.shutdown()

        val policyManager = get<PolicyManager>()
        val httpRequestManager = get<HttpRequestManager>()

        httpRequestManager.cancelAll()
        policyManager.cancelAll()

        policyManager.stub {
            on { getRequestsPolicyAsync(anyOrNull(), any()) } doAnswer {
                it.getArgument<(kidsMode: Boolean, ageLimit: Int?) -> Unit>(1)?.invoke(false, 0)
                println("D PolicyManager: stub getRequestsPolicyAsync")
            }
        }

        httpRequestManager.stub {
            on { waitAccount() } doReturn Completable.complete()
        }

        httpRequestManager.stub {
            onGeneric { submit(any<HttpRequestTask<*>>(), anyOrNull()) } doAnswer {
                it.getArgument<HttpRequestTask<*>>(0).run()
                println("D HttpRequestManager: stub submit")
            }
        }

        repository = createRepository()
    }

    @After
    fun tearDown() {
        repository.destroy()
        get<HttpRequestManager>().cancelAll()
        get<PolicyManager>().cancelAll()
        callsExecutor.shutdown()
        Schedulers.shutdown()
        stopKoin()
    }

    @Test
    fun `get categories, local empty, categories obtained from remote and saved`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_categories.json"
        )
        var obtainedCategories: List<Category> = emptyList()
        var operationResult = false

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(
                    callback = callback
                )
            },
            onSuccess = {
                obtainedCategories = it
                assertThat(it.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("$it: categories should be obtained", false)
            }
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(
                    callback = callback,
                    force = false,
                    tag = "my tag"
                )
            },
            onSuccess = {
                obtainedCategories = it
                assertThat(it.isNotEmpty(), equalTo(true))
                operationResult = true
            },
            onError = {
                operationResult = false
            })


        assertThat("Failed to obtain categories", operationResult)

        val inOrder = inOrder(repository.remoteRepository, repository.localRepository)

        inOrder.verify(repository.localRepository, times(1))
            .getCategoryList(
                callback = any(),
                force = eq(false),
                tag = anyOrNull()
            )
        inOrder.verify(repository.remoteRepository, times(1))
            .getCategoryList(
                callback = any(),
                force = eq(false),
                tag = anyOrNull()
            )
        inOrder.verify(repository.localRepository, times(1))
            .addOrUpdateCategoryList(
                callback = any(),
                categoryList = eq(obtainedCategories),
                tag = anyOrNull(),
                expireTimestamp = anyOrNull()
            )
    }

    @Test
    fun `get categories, local not empty, categories obtained from local and not changed`() {
        val item = Category(
            TEST_CATEGORY_ID,
            persistentId = null,
            title = TEST_CAROUSEL_TITLE,
            rank = 0,
            icon = null
        )
        var operationResult = false
        val insertCountDownLatch = CountDownLatch(1)

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback,
                    listOf(item)
                )
            },
            onSuccess = {
                operationResult = true
                insertCountDownLatch.countDown()
            },
            onError = {
                operationResult = false
                insertCountDownLatch.countDown()
            }
        )

        insertCountDownLatch.await()

        assertThat("Failed to update categories", operationResult)

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(callback)
            },
            onSuccess = {
                assertThat(it.size, equalTo(1))
                assertThat(it[0], equalTo(item))
                operationResult = true
            },
            onError = {
                operationResult = false
            }
        )

        assertThat("Failed to obtain categories", operationResult)

        verify(repository.localRepository, times(1))
            .getCategoryList(
                callback = any(),
                force = eq(false),
                tag = anyOrNull()
            )
        verifyNoInteractions(repository.remoteRepository)
    }

    @Test
    fun `get categories from remote, outdated content deleted`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_categories.json"
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(
                    callback = callback
                )
            },
            onSuccess = {
                assertThat(it.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("$it: categories should be obtained", false)
            }
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(
                    callback = callback,
                    force = false,
                    tag = "my tag"
                )
            },
            onSuccess = {
                assertThat(it.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("Failed to obtain categories", false)
            }
        )

        val inOrder = inOrder(repository.remoteRepository, repository.localRepository)
        inOrder.verify(repository.localRepository, times(1))
            .getCategoryList(
                callback = any(),
                force = eq(false),
                tag = anyOrNull()
            )
        inOrder.verify(repository.remoteRepository, times(1))
            .getCategoryList(
                callback = any(),
                force = eq(false),
                tag = anyOrNull()
            )
        inOrder.verify(repository.localRepository, times(1))
            .deleteOutdatedMediaContent(
                timestamp = any()
            )
    }

    @Test
    fun `get categories force, categories obtained from remote`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_categories.json"
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(
                    callback = callback,
                    force = true
                )
            },
            onSuccess = {
                assertThat(it.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("$it: categories should be obtained", false)
            }
        )

        verify(repository.remoteRepository, times(1))
            .getCategoryList(
                callback = any(),
                force = eq(true),
                tag = anyOrNull()
            )
        verify(repository.localRepository, never())
            .getCategoryList(
                callback = any(),
                force = any(),
                tag = anyOrNull()
            )
    }

    @Test
    fun `get carousels, local empty, carousels obtained from remote and saved`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousels_main.json",
        )

        val actualPagingInfo = MediaContentRepository.PagingInfoImpl("main", "more_url")

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.localRepository.persistPagingInfo(actualPagingInfo, callback)
            }
        )

        reset(repository.localRepository)

        val initialPagingInfo = MediaContentRepository.EmptyPagingInfo("main")
        val carouselOffset = 0
        var obtainedCarousels: List<Carousel>? = null

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    pagingInfo = initialPagingInfo,
                    callback = callback,
                    carouselOffset = carouselOffset
                )
            },
            onSuccess = {
                obtainedCarousels = it.items
                assertThat(it.items.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("$it: Request should succeed", false)
            }
        )

        val savedCarouselsWithOffsetCaptor = argumentCaptor<List<Pair<Carousel, Int>>>()
        val inOrder = inOrder(repository.remoteRepository, repository.localRepository)
        inOrder.verify(repository.localRepository, times(1))
            .getCarouselList(
                pagingInfo = eq(initialPagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                filters = any(),
                allowEmptyCarousels = any(),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        inOrder.verify(repository.remoteRepository, times(1))
            .getCarouselList(
                pagingInfo = eq(actualPagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                filters = any(),
                allowEmptyCarousels = any(),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        inOrder.verify(repository.localRepository, times(1))
            .addOrUpdateCarouselList(
                callback = any(),
                carouselList = savedCarouselsWithOffsetCaptor.capture(),
                tag = anyOrNull(),
                contentExpireTimestamp = anyOrNull(),
                carouselExpireTimestamp = anyOrNull()
            )
        val savedCarouselsWithOffset = savedCarouselsWithOffsetCaptor.firstValue
        assertThat(savedCarouselsWithOffset.map { it.first }, equalTo(obtainedCarousels))
        assertThat(savedCarouselsWithOffset.all { it.second == carouselOffset }, equalTo(true))
    }

    @Test
    fun `get carousels, local empty, paging info persisted`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousels_main.json",
        )

        val actualPagingInfo = MediaContentRepository.PagingInfoImpl("main", "more_url")

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.localRepository.persistPagingInfo(actualPagingInfo, callback)
            }
        )

        reset(repository.localRepository)

        val initialPagingInfo = MediaContentRepository.EmptyPagingInfo("main")

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            repositoryCall = { callback ->
                repository.getCarouselList(
                    pagingInfo = initialPagingInfo,
                    callback = callback
                )
            }
        )

        verify(repository.localRepository, times(1))
            .persistPagingInfo(
                pagingInfo = eq(
                    MediaContentRepository.PagingInfoImpl(
                        "main",
                        "$DROIDEKA_HOST$CAROUSELS_MAIN_MORE_PATH",
                        CAROUSELS_MAIN_CACHE_HASH
                    )
                ),
                callback = any(),
                tag = anyOrNull()
            )
    }

    @Test
    fun `get carousels, local not empty, carousels obtained from local and not changed`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )
        val carousel = Carousel(
            TEST_CAROUSEL_ID,
            TEST_CAROUSEL_TITLE,
            categoryId = TEST_CATEGORY_ID,
            items = listOf(contentItem),
            rank = 1
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    listOf(Pair(carousel, 0))
                )
            }
        )

        val initialPagingInfo = MediaContentRepository.EmptyPagingInfo("main")

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    pagingInfo = initialPagingInfo,
                    callback = callback
                )
            },
            onSuccess = {
                assertThat(it.items.size, equalTo(1))
                assertThat(it.items[0].carouselId, equalTo(carousel.carouselId))
                assertThat(it.items[0].items[0].id, equalTo(contentItem.id))
            },
            onError = {
                assertThat("$it: Request should succeed", false)
            }
        )

        verify(repository.localRepository, times(1))
            .getCarouselList(
                pagingInfo = eq(initialPagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                filters = any(),
                allowEmptyCarousels = any(),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        verifyNoInteractions(repository.remoteRepository)
    }

    @Test
    fun `get carousels from remote, outdated content deleted`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousels_main.json",
        )

        val initialPagingInfo = MediaContentRepository.EmptyPagingInfo("main")

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    pagingInfo = initialPagingInfo,
                    callback = callback
                )
            }
        )

        verify(repository.localRepository, times(1))
            .deleteOutdatedMediaContent(
                timestamp = any()
            )
    }

    @Test
    fun `get carousels force, carousels obtained from remote`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousels_main.json",
        )

        val initialPagingInfo = MediaContentRepository.PagingInfoImpl("main", null)

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    pagingInfo = initialPagingInfo,
                    callback = callback,
                    force = true
                )
            }
        )

        verify(repository.remoteRepository, times(1))
            .getCarouselList(
                pagingInfo = eq(initialPagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                filters = any(),
                allowEmptyCarousels = any(),
                force = eq(true),
                tag = anyOrNull(),
                screenId = any()
            )
        verify(repository.localRepository, times(1))
            .getCarouselList(
                pagingInfo = eq(initialPagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                filters = any(),
                allowEmptyCarousels = any(),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        verify(repository.localRepository, times(1))
            .deleteCarouselsForPage(
                pagingInfo = eq(initialPagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                filters = any(),
                allowEmptyCarousels = any(),
                force = any(),
                tag = anyOrNull()
            )
    }

    @Test
    fun `get carousels, local empty, remote empty, get NoDataException`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousels_empty.json",
        )

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    pagingInfo = MediaContentRepository.EmptyPagingInfo("invalid"),
                    callback = callback,
                )
            },
            onSuccess = {
                assertThat("Request should fail on empty response", false)
            },
            onError = {
                assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
            }
        )

    }

    @Test
    fun `get carousel part, local empty, carousel part obtained from remote and saved`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_no_offset.json",
        )

        val offset = 0
        val requestedCarousel = Carousel.createEmpty(
            carouselId = TEST_CAROUSEL_ID,
            categoryId = TEST_CATEGORY_ID,
            title = TEST_CAROUSEL_TITLE,
            rank = 0,
        )
        var obtainedCarousel: Carousel? = null

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselPart(
                    carousel = requestedCarousel,
                    callback = callback,
                    offset = offset
                )
            },
            onSuccess = {
                obtainedCarousel = it
                assertThat(it.items.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("$it: Carousels should be obtained", false)
            }
        )

        val requestedCarouselCaptor = argumentCaptor<Carousel>()
        val savedCarouselsWithOffsetCaptor = argumentCaptor<List<Pair<Carousel, Int>>>()
        val inOrder = inOrder(repository.remoteRepository, repository.localRepository)

        inOrder.verify(repository.localRepository, times(1))
            .getCarouselPart(
                carousel = requestedCarouselCaptor.capture(),
                callback = any(),
                offset = any(),
                limit = any(),
                filters = eq(emptyList()),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        inOrder.verify(repository.remoteRepository, times(1))
            .getCarouselPart(
                carousel = requestedCarouselCaptor.capture(),
                callback = any(),
                offset = any(),
                limit = any(),
                filters = eq(emptyList()),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        inOrder.verify(repository.localRepository, times(1))
            .addOrUpdateCarouselList(
                callback = any(),
                carouselList = savedCarouselsWithOffsetCaptor.capture(),
                tag = anyOrNull(),
                contentExpireTimestamp = anyOrNull(),
                carouselExpireTimestamp = anyOrNull()
            )

        assertThat(
            requestedCarouselCaptor.firstValue.carouselId,
            equalTo(requestedCarousel.carouselId)
        )
        assertThat(
            requestedCarouselCaptor.secondValue.carouselId,
            equalTo(requestedCarousel.carouselId)
        )
        val savedCarouselsWithOffset = savedCarouselsWithOffsetCaptor.firstValue
        assertThat(savedCarouselsWithOffset.size, equalTo(1))
        assertThat(
            savedCarouselsWithOffset[0].first.carouselId,
            equalTo(obtainedCarousel!!.carouselId)
        )
        assertThat(savedCarouselsWithOffset[0].second, equalTo(offset))
    }

    @Test
    fun `get carousel part, local empty, filters not empty, filtered carousel obtained and saved`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_no_offset_filters.json",
        )

        val filters = listOf(FilterInfo("filter1", "value1", 0))
        val offset = 0
        val requestedCarousel = Carousel.createEmpty(
            carouselId = TEST_CAROUSEL_ID,
            categoryId = TEST_CATEGORY_ID,
            title = TEST_CAROUSEL_TITLE,
            rank = 0,
            moreInfo = Carousel.MoreInfo(testFiltersMoreUrl)
        )
        val filteredCarouselId = Carousel.generateFilteredId(requestedCarousel.carouselId, filters)
        var obtainedCarousel: Carousel? = null

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselPart(
                    carousel = requestedCarousel,
                    callback = callback,
                    offset = offset,
                    filters = filters
                )
            },
            onSuccess = {
                obtainedCarousel = it
                assertThat(it.items.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("$it: Carousels should be obtained", true)
            }
        )

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselPart(
                    carousel = requestedCarousel,
                    callback = callback,
                    offset = offset,
                    filters = filters
                )
            },
            onSuccess = {
                obtainedCarousel = it
                assertThat(it.items.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("$it: Carousels should be obtained", false)
            }
        )

        val requestedCarouselCaptor = argumentCaptor<Carousel>()
        val savedCarouselsWithOffsetCaptor = argumentCaptor<List<Pair<Carousel, Int>>>()
        val inOrder = inOrder(repository.remoteRepository, repository.localRepository)
        inOrder.verify(repository.localRepository, times(1))
            .getCarouselPart(
                carousel = requestedCarouselCaptor.capture(),
                callback = any(),
                offset = any(),
                limit = any(),
                filters = eq(filters),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        inOrder.verify(repository.remoteRepository, times(1))
            .getCarouselPart(
                carousel = requestedCarouselCaptor.capture(),
                callback = any(),
                offset = any(),
                limit = any(),
                filters = eq(filters),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        inOrder.verify(repository.localRepository, times(1))
            .addOrUpdateCarouselList(
                callback = any(),
                carouselList = savedCarouselsWithOffsetCaptor.capture(),
                tag = anyOrNull(),
                contentExpireTimestamp = anyOrNull(),
                carouselExpireTimestamp = anyOrNull()
            )

        assertThat(
            requestedCarouselCaptor.firstValue.carouselId,
            equalTo(requestedCarousel.carouselId)
        )
        assertThat(
            requestedCarouselCaptor.secondValue.carouselId,
            equalTo(requestedCarousel.carouselId)
        )
        val savedCarouselsWithOffset = savedCarouselsWithOffsetCaptor.firstValue
        assertThat(savedCarouselsWithOffset.size, equalTo(1))
        assertThat(
            savedCarouselsWithOffset[0].first.carouselId,
            equalTo(obtainedCarousel!!.carouselId)
        )
        assertThat(savedCarouselsWithOffset[0].second, equalTo(offset))

        assertThat(obtainedCarousel!!.carouselId, equalTo(filteredCarouselId))
    }

    @Test
    fun `get carousel part, local not empty, carousel part obtained from local and not changed`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )
        val carousel = Carousel(
            TEST_CAROUSEL_ID,
            TEST_CAROUSEL_TITLE,
            categoryId = TEST_CATEGORY_ID,
            items = listOf(contentItem),
            rank = 1
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    listOf(Pair(carousel, 0))
                )
            }
        )

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselPart(
                    carousel = carousel,
                    callback = callback
                )
            },
            onSuccess = {
                assertThat(it.items.isNotEmpty(), equalTo(true))
                assertThat(it.carouselId, equalTo(carousel.carouselId))
            },
            onError = {
                assertThat("$it: Carousels should be obtained", false)
            }
        )

        val requestedCarouselCaptor = argumentCaptor<Carousel>()
        verify(repository.localRepository, times(1))
            .getCarouselPart(
                carousel = requestedCarouselCaptor.capture(),
                callback = any(),
                offset = any(),
                limit = any(),
                filters = eq(emptyList()),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        verifyNoInteractions(repository.remoteRepository)

        assertThat(requestedCarouselCaptor.firstValue.carouselId, equalTo(carousel.carouselId))
    }

    @Test
    fun `get carousel part from remote, outdated content deleted`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_no_offset.json",
        )

        val offset = 0
        val requestedCarousel = Carousel.createEmpty(
            carouselId = TEST_CAROUSEL_ID,
            categoryId = TEST_CATEGORY_ID,
            title = TEST_CAROUSEL_TITLE,
            rank = 0,
        )

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselPart(
                    carousel = requestedCarousel,
                    callback = callback,
                    offset = offset
                )
            }
        )

        verify(repository.localRepository, times(1))
            .deleteOutdatedMediaContent(
                timestamp = any()
            )
    }

    @Test
    fun `get carousel part force, carousel part obtained from remote`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_no_offset.json",
        )

        val offset = 0
        val requestedCarousel = Carousel.createEmpty(
            carouselId = TEST_CAROUSEL_ID,
            categoryId = TEST_CATEGORY_ID,
            title = TEST_CAROUSEL_TITLE,
            rank = 0
        )

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselPart(
                    carousel = requestedCarousel,
                    callback = callback,
                    offset = offset,
                    force = true
                )
            }
        )

        val requestedCarouselCaptor = argumentCaptor<Carousel>()
        verify(repository.remoteRepository, times(1))
            .getCarouselPart(
                carousel = requestedCarouselCaptor.capture(),
                callback = any(),
                offset = any(),
                limit = any(),
                filters = eq(emptyList()),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        verify(repository.localRepository, never())
            .getCarouselPart(
                carousel = any(),
                callback = any(),
                offset = any(),
                limit = any(),
                filters = any(),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )

        assertThat(
            requestedCarouselCaptor.firstValue.carouselId,
            equalTo(requestedCarousel.carouselId)
        )
    }

    @Test
    fun `get carousel part, local empty, remote empty, get NoDataException`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_invalid.json",
        )

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselPart(
                    carousel = Carousel.createEmpty(
                        carouselId = TEST_FILTERS_CAROUSEL_ID,
                        categoryId = TEST_FILTERS_CATEGORY_ID,
                        title = TEST_FILTERS_CAROUSEL_TITLE,
                        rank = 0,
                    ),
                    callback = callback,
                    offset = 0,
                    filters = TEST_FILTERS
                )
            },
            onSuccess = {
                assertThat("Carousel should not be obtained", false)
            },
            onError = {
                assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
            }
        )
    }

    @Test
    fun `get card details, local empty, card details obtained from remote and saved`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_card_detail.json",
        )

        repositoryExecuteBlocking<ContentItem>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCardDetails(
                    contentItem = VhEpisodeItem.createEmpty(
                        episodeId = TEST_CONTENT_ID,
                        episodeType = TEST_CONTENT_TYPE
                    ),
                    callback = callback
                )
            },
            onSuccess = {
                assertThat(it, instanceOf(VhEpisodeItem::class.java))
                assertThat(it.id, equalTo(TEST_CONTENT_ID))
                assertThat(it.contentType, equalTo(TEST_CONTENT_TYPE))
            },
            onError = {
                assertThat("$it: Card details should be obtained", false)
            }
        )

        val contentItemCaptor = argumentCaptor<ContentItem>()
        val updatedContentItemCaptor = argumentCaptor<List<ContentItem>>()
        val inOrder = inOrder(repository.localRepository, repository.remoteRepository)

        inOrder.verify(repository.localRepository, times(1))
            .getCardDetails(
                contentItem = contentItemCaptor.capture(),
                callback = any(),
                force = any(),
                tag = anyOrNull()
            )
        inOrder.verify(repository.remoteRepository, times(1))
            .getCardDetails(
                contentItem = contentItemCaptor.capture(),
                callback = any(),
                force = any(),
                tag = anyOrNull()
            )
        inOrder.verify(repository.localRepository, times(1))
            .addOrUpdateContentItems(
                callback = any(),
                contentItems = updatedContentItemCaptor.capture(),
                tag = anyOrNull()
            )

        assertThat(contentItemCaptor.firstValue.id, equalTo(TEST_CONTENT_ID))
        assertThat(contentItemCaptor.secondValue.id, equalTo(TEST_CONTENT_ID))
        assertThat(updatedContentItemCaptor.firstValue.size, equalTo(1))
        assertThat(updatedContentItemCaptor.firstValue[0].id, equalTo(TEST_CONTENT_ID))
    }

    @Test
    fun `get card details, local empty, card marked detailed`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_card_detail.json",
        )

        repositoryExecuteBlocking<ContentItem>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCardDetails(
                    contentItem = VhEpisodeItem.createEmpty(
                        episodeId = TEST_CONTENT_ID,
                        episodeType = TEST_CONTENT_TYPE
                    ),
                    callback = callback
                )
            },
            onSuccess = {
                assertThat(it, instanceOf(VhEpisodeItem::class.java))
                assertThat(it.id, equalTo(TEST_CONTENT_ID))
                assertThat(it.contentType, equalTo(TEST_CONTENT_TYPE))
            },
            onError = {
                assertThat("$it: Card details should be obtained", false)
            }
        )

        val updatedContentItemCaptor = argumentCaptor<List<ContentItem>>()
        verify(repository.localRepository, times(1))
            .markDetailed(
                contentItems = updatedContentItemCaptor.capture(),
                callback = any(),
                tag = anyOrNull()
            )

        assertThat(updatedContentItemCaptor.firstValue.size, equalTo(1))
        assertThat(updatedContentItemCaptor.firstValue[0].id, equalTo(TEST_CONTENT_ID))
    }

    @Test
    fun `get card details, local not empty, card details obtained from local and not changed`() {
        val item = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE

        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateContentItems(
                    callback,
                    listOf(item)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.localRepository.markDetailed(listOf(item), callback)
            }
        )


        repositoryExecuteBlocking<ContentItem>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCardDetails(
                    contentItem = item,
                    callback = callback,
                )
            },
            onSuccess = {
                assertThat(it, instanceOf(VhEpisodeItem::class.java))
                assertThat(it.id, equalTo(TEST_CONTENT_ID))
                assertThat(it.contentType, equalTo(TEST_CONTENT_TYPE))
            },
            onError = {
                assertThat("$it: Card details should be obtained", false)
            }
        )

        val contentItemCaptor = argumentCaptor<ContentItem>()
        verify(repository.localRepository, times(1))
            .getCardDetails(
                contentItem = contentItemCaptor.capture(),
                callback = any(),
                force = any(),
                tag = anyOrNull()
            )
        verifyNoInteractions(repository.remoteRepository)

        assertThat(contentItemCaptor.firstValue.id, equalTo(TEST_CONTENT_ID))
    }

    @Test
    fun `get card details force, categories obtained from remote`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_card_detail.json",
        )

        repositoryExecuteBlocking<ContentItem>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCardDetails(
                    contentItem = VhEpisodeItem.createEmpty(
                        episodeId = TEST_CONTENT_ID,
                        episodeType = TEST_CONTENT_TYPE
                    ),
                    callback = callback,
                    force = true
                )
            }
        )

        val contentItemCaptor = argumentCaptor<ContentItem>()
        verify(repository.remoteRepository, times(1))
            .getCardDetails(
                contentItem = contentItemCaptor.capture(),
                callback = any(),
                force = any(),
                tag = anyOrNull()
            )
        verify(repository.localRepository, never())
            .getCardDetails(
                contentItem = any(),
                callback = any(),
                force = any(),
                tag = anyOrNull()
            )

        assertThat(contentItemCaptor.firstValue.id, equalTo(TEST_CONTENT_ID))
    }

    @Test
    fun `get section details, local empty, section details obtained from remote and saved`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_section_details.json"
        )

        var obtainedSectionItems: Carousel? = null
        val offset = 0

        repositoryExecuteBlocking<MediaContentRepository.SectionDetails>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSectionDetails(
                    sectionItem = SectionItem(TEST_SECTION_ID, TEST_SECTION_TYPE),
                    callback = callback,
                    offset = offset
                )
            },
            onSuccess = {
                obtainedSectionItems = it.items
                assertThat(it.items.items.isNotEmpty(), equalTo(true))
                assertThat(
                    (it.items as? CarouselWithFilters)?.filters?.baseUrl.isNullOrEmpty(),
                    equalTo(false)
                )
                assertThat(
                    (it.items as? CarouselWithFilters)?.filters?.filterCategories.isNullOrEmpty(),
                    equalTo(false)
                )
            },
            onError = {
                assertThat("Section should be obtained", false)
            }
        )

        val sectionItemCaptor = argumentCaptor<SectionItem>()
        val updatedContentItemCaptor = argumentCaptor<List<ContentItem>>()
        val updatedCarouselOffsetListCaptor = argumentCaptor<List<Pair<Carousel, Int>>>()
        val inOrder = inOrder(repository.localRepository, repository.remoteRepository)
        inOrder.verify(repository.localRepository, times(1))
            .getSectionDetails(
                sectionItem = sectionItemCaptor.capture(),
                callback = any(),
                offset = any(),
                limit = any(),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        inOrder.verify(repository.remoteRepository, times(1))
            .getSectionDetails(
                sectionItem = sectionItemCaptor.capture(),
                callback = any(),
                offset = any(),
                limit = any(),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        inOrder.verify(repository.localRepository, times(1))
            .addOrUpdateContentItems(
                callback = any(),
                contentItems = updatedContentItemCaptor.capture(),
                tag = anyOrNull()
            )
        inOrder.verify(repository.localRepository, times(1))
            .addOrUpdateCarouselList(
                callback = any(),
                carouselList = updatedCarouselOffsetListCaptor.capture(),
                tag = anyOrNull(),
                contentExpireTimestamp = anyOrNull(),
                carouselExpireTimestamp = anyOrNull()
            )

        assertThat(sectionItemCaptor.firstValue.id, equalTo(TEST_SECTION_ID))
        assertThat(sectionItemCaptor.secondValue.id, equalTo(TEST_SECTION_ID))
        assertThat(updatedContentItemCaptor.firstValue.size, equalTo(1))
        assertThat(updatedContentItemCaptor.firstValue[0].id, equalTo(TEST_SECTION_ID))
        val updatedCarouselOffsetList = updatedCarouselOffsetListCaptor.firstValue
        assertThat(updatedCarouselOffsetList.size, equalTo(1))
        assertThat(
            updatedCarouselOffsetList[0].first.carouselId,
            equalTo(obtainedSectionItems!!.carouselId)
        )
        assertThat(updatedCarouselOffsetList[0].second, equalTo(offset))
    }

    @Test
    fun `get section details, local not empty, section details obtained from local and not changed`() {
        val filterBundle = FilterBundle(
            "test_filter_base_url",
            listOf(FilterCategory("test_filter_category", TEST_FILTERS))
        )
        val sectionItem = SectionItem(TEST_SECTION_ID, TEST_SECTION_TYPE, filterBundle)
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )
        val carousel = Carousel(
            carouselId = SectionItem.makeCarouselIdFromId(sectionItem.id),
            categoryId = sectionItem.id,
            title = "",
            items = listOf(contentItem),
            rank = 1
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateContentItems(
                    callback,
                    listOf(sectionItem)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback = callback,
                    listOf(carousel to 0)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.SectionDetails>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSectionDetails(
                    sectionItem = sectionItem,
                    callback = callback
                )
            },
            onSuccess = {
                assertThat(it.items.items.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("Section should be obtained", false)
            }
        )

        val sectionItemCaptor = argumentCaptor<SectionItem>()
        verify(repository.localRepository, times(1))
            .getSectionDetails(
                sectionItem = sectionItemCaptor.capture(),
                callback = any(),
                offset = any(),
                limit = any(),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        verifyNoInteractions(repository.remoteRepository)

        assertThat(sectionItemCaptor.firstValue.id, equalTo(sectionItem.id))
    }

    @Test
    fun `get section details force, categories obtained from remote`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_section_details.json"
        )

        val offset = 0

        repositoryExecuteBlocking<MediaContentRepository.SectionDetails>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSectionDetails(
                    sectionItem = SectionItem(TEST_SECTION_ID, TEST_SECTION_TYPE),
                    callback = callback,
                    offset = offset,
                    force = true
                )

            }
        )

        val sectionItemCaptor = argumentCaptor<SectionItem>()
        verify(repository.localRepository, never())
            .getSectionDetails(
                sectionItem = any(),
                callback = any(),
                offset = any(),
                limit = any(),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )
        verify(repository.remoteRepository, times(1))
            .getSectionDetails(
                sectionItem = sectionItemCaptor.capture(),
                callback = any(),
                offset = any(),
                limit = any(),
                force = any(),
                tag = anyOrNull(),
                screenId = any()
            )

        assertThat(sectionItemCaptor.firstValue.id, equalTo(TEST_SECTION_ID))
    }

    @Test
    fun `get section details, local empty, remote empty, get NoDataException`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_invalid.json",
        )

        repositoryExecuteBlocking<MediaContentRepository.SectionDetails>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSectionDetails(
                    sectionItem = SectionItem(TEST_SECTION_ID, TEST_SECTION_TYPE),
                    callback = callback,
                    offset = 0,
                    force = true
                )
            },
            onSuccess = {
                assertThat("Carousel should not be obtained", false)
            },
            onError = {
                assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
            }
        )
    }

    @Test
    fun `get seasons, local empty, seasons obtained from remote and saved`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_seasons_no_offset.json")
            enqueueServerResponse(responseFileName = "raw/response_episodes_no_offset.json")
        }
        val pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_LIBRARY_ID)

        val actualPagingInfo = MediaContentRepository.PagingInfoImpl(TEST_LIBRARY_ID, "more_url")

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.localRepository.persistPagingInfo(actualPagingInfo, callback)
            }
        )

        var obtainedCarousels: List<Carousel>? = null
        val carouselOffset = 0

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasons(
                    pagingInfo = pagingInfo,
                    callback = callback,
                    carouselOffset = carouselOffset
                )
            },
            onSuccess = {
                obtainedCarousels = it.items
                assertThat(it.items.isNotEmpty(), equalTo(true))
                assertThat(it.items[0].items.size, Matchers.greaterThan(1))
            },
            onError = {
                assertThat("$it: Seasons should be obtained", false)
            }
        )

        val savedCarouselsWithOffsetCaptor = argumentCaptor<List<Pair<Carousel, Int>>>()
        val inOrder = inOrder(repository.localRepository, repository.remoteRepository)
        inOrder.verify(repository.localRepository, times(1))
            .getSeasons(
                pagingInfo = eq(pagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                force = any(),
                tag = anyOrNull()
            )
        inOrder.verify(repository.remoteRepository, times(1))
            .getSeasons(
                pagingInfo = eq(actualPagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                force = any(),
                tag = anyOrNull()
            )
        inOrder.verify(repository.localRepository, times(1))
            .addOrUpdateCarouselList(
                callback = any(),
                carouselList = savedCarouselsWithOffsetCaptor.capture(),
                tag = anyOrNull(),
                contentExpireTimestamp = anyOrNull(),
                carouselExpireTimestamp = anyOrNull()
            )

        val savedCarouselsWithOffset = savedCarouselsWithOffsetCaptor.firstValue
        assertThat(savedCarouselsWithOffset.map { it.first }, equalTo(obtainedCarousels))
        assertThat(savedCarouselsWithOffset.all { it.second == carouselOffset }, equalTo(true))
    }

    @Test
    fun `get seasons, local empty, seasons obtained, paging info persisted`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_seasons_no_offset.json")
            enqueueServerResponse(responseFileName = "raw/response_episodes_no_offset.json")
        }
        val pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_LIBRARY_ID)

        val actualPagingInfo = MediaContentRepository.PagingInfoImpl(TEST_LIBRARY_ID, "more_url")

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.localRepository.persistPagingInfo(actualPagingInfo, callback)
            }
        )

        reset(repository.localRepository)

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasons(
                    pagingInfo = pagingInfo,
                    callback = callback,
                )
            },
            onSuccess = {
                assertThat(it.items.isNotEmpty(), equalTo(true))
                assertThat(it.items[0].items.size, Matchers.greaterThan(1))
            },
            onError = {
                assertThat("$it: Seasons should be obtained", false)
            }
        )

        val inOrder = inOrder(repository.localRepository, repository.remoteRepository)
        inOrder.verify(repository.localRepository, times(1))
            .getSeasons(
                pagingInfo = eq(pagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                force = any(),
                tag = anyOrNull()
            )
        inOrder.verify(repository.remoteRepository, times(1))
            .getSeasons(
                pagingInfo = eq(actualPagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                force = any(),
                tag = anyOrNull()
            )
        inOrder.verify(repository.localRepository, times(1))
            .persistPagingInfo(
                pagingInfo = eq(MediaContentRepository.PagingInfoImpl(TEST_LIBRARY_ID, null)),
                callback = any(),
                tag = anyOrNull()
            )
    }

    @Test
    fun `get seasons, local not empty, seasons obtained from local and not changed`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )
        val carousel = Carousel(
            TEST_CAROUSEL_ID,
            TEST_CAROUSEL_TITLE,
            categoryId = TEST_LIBRARY_ID,
            items = listOf(contentItem),
            rank = 1
        )

        val pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_LIBRARY_ID)

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    listOf(Pair(carousel, 0))
                )
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasons(
                    pagingInfo = pagingInfo,
                    callback = callback,
                )
            },
            onSuccess = {
                assertThat(it.items.isNotEmpty(), equalTo(true))
                assertThat(it.items[0].items.size, equalTo(1))
            },
            onError = {
                assertThat("$it: Seasons should be obtained", false)
            }
        )

        verifyNoInteractions(repository.remoteRepository)
        verify(repository.localRepository, times(1))
            .getSeasons(
                pagingInfo = eq(pagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                force = any(),
                tag = anyOrNull()
            )
    }

    @Test
    fun `get seasons from remote, outdated content deleted`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_seasons_no_offset.json")
            enqueueServerResponse(responseFileName = "raw/response_episodes_no_offset.json")
        }
        val pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_LIBRARY_ID)

        val actualPagingInfo = MediaContentRepository.PagingInfoImpl(TEST_LIBRARY_ID, "more_url")

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.localRepository.persistPagingInfo(actualPagingInfo, callback)
            }
        )

        reset(repository.localRepository)

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasons(
                    pagingInfo = pagingInfo,
                    callback = callback,
                )
            }
        )

        verify(repository.localRepository, times(1))
            .deleteOutdatedMediaContent(
                timestamp = any()
            )
    }

    @Test
    fun `get seasons force, seasons obtained from remote`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_seasons_no_offset.json")
            enqueueServerResponse(responseFileName = "raw/response_episodes_no_offset.json")
        }
        val pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_LIBRARY_ID)

        val actualPagingInfo = MediaContentRepository.PagingInfoImpl(TEST_LIBRARY_ID, "more_url")

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.localRepository.persistPagingInfo(actualPagingInfo, callback)
            }
        )

        reset(repository.localRepository)

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasons(
                    pagingInfo = pagingInfo,
                    callback = callback,
                    force = true
                )
            }
        )

        verify(repository.localRepository, never())
            .getSeasons(
                pagingInfo = any(),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                force = any(),
                tag = anyOrNull()
            )
        verify(repository.remoteRepository, times(1))
            .getSeasons(
                pagingInfo = eq(actualPagingInfo),
                callback = any(),
                offset = any(),
                limit = any(),
                carouselOffset = any(),
                carouselLimit = any(),
                force = any(),
                tag = anyOrNull()
            )
    }

    @Test
    fun `get seasons, local empty, remote empty, get NoDataException`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_seasons_empty.json")
        }

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasons(
                    pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_LIBRARY_ID),
                    callback = callback
                )
            },
            onSuccess = {
                assertThat("$it: Seasons should not be obtained", false)
            },
            onError = {
                assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
            }
        )
    }

    @Test
    fun `get season part, local empty, season part obtained from remote and saved`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_episodes_no_offset.json")
        }

        var obtainedSeason: Carousel? = null
        val season = Carousel.createEmpty(TEST_SEASON_ID, TEST_LIBRARY_ID, "", 1)
        val offset = 0

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasonPart(
                    season = season,
                    callback = callback,
                    offset = offset
                )
            },
            onSuccess = {
                obtainedSeason = it
                assertThat(it.items.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("$it: Season should be obtained", false)
            }
        )

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasonPart(
                    season = season,
                    callback = callback,
                    offset = offset
                )
            },
            onSuccess = {
                obtainedSeason = it
                assertThat(it.items.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("$it: Season should be obtained", false)
            }
        )

        val updatedCarouselOffsetListCaptor = argumentCaptor<List<Pair<Carousel, Int>>>()
        val inOrder = inOrder(repository.localRepository, repository.remoteRepository)
        inOrder.verify(repository.localRepository, times(1))
            .getSeasonPart(
                season = eq(season),
                callback = any(),
                offset = any(),
                limit = any(),
                force = any(),
                tag = anyOrNull(),
                useMoreUrl = any()
            )
        inOrder.verify(repository.remoteRepository, times(1))
            .getSeasonPart(
                season = eq(season),
                callback = any(),
                offset = any(),
                limit = any(),
                force = any(),
                tag = anyOrNull(),
                useMoreUrl = any()
            )
        inOrder.verify(repository.localRepository, times(1))
            .addOrUpdateCarouselList(
                callback = any(),
                carouselList = updatedCarouselOffsetListCaptor.capture(),
                tag = anyOrNull(),
                contentExpireTimestamp = anyOrNull(),
                carouselExpireTimestamp = anyOrNull()
            )

        val updatedCarouselOffsetList = updatedCarouselOffsetListCaptor.firstValue
        assertThat(updatedCarouselOffsetList.size, equalTo(1))
        assertThat(
            updatedCarouselOffsetList[0].first.carouselId,
            equalTo(obtainedSeason!!.carouselId)
        )
        assertThat(updatedCarouselOffsetList[0].second, equalTo(offset))
    }

    @Test
    fun `get season part, local not empty, season part obtained from local and not changed`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )
        val carousel = Carousel(
            TEST_SEASON_ID,
            TEST_CAROUSEL_TITLE,
            categoryId = TEST_LIBRARY_ID,
            items = listOf(contentItem),
            rank = 1
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    listOf(Pair(carousel, 0))
                )
            }
        )

        val season = Carousel.createEmpty(TEST_SEASON_ID, TEST_LIBRARY_ID, "", 1)
        val offset = 0

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasonPart(
                    season = season,
                    callback = callback,
                    offset = offset
                )
            },
            onSuccess = {
                assertThat(it.items.isNotEmpty(), equalTo(true))
            },
            onError = {
                assertThat("$it: Season should be obtained", false)

            }
        )

        verifyNoInteractions(repository.remoteRepository)
        verify(repository.localRepository, times(1))
            .getSeasonPart(
                season = eq(season),
                callback = any(),
                offset = any(),
                limit = any(),
                force = any(),
                tag = anyOrNull(),
                useMoreUrl = any()
            )
    }

    @Test
    fun `get season part from remote, outdated content deleted`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_episodes_no_offset.json")
        }

        val season = Carousel.createEmpty(TEST_SEASON_ID, TEST_LIBRARY_ID, "", 1)
        val offset = 0

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasonPart(
                    season = season,
                    callback = callback,
                    offset = offset
                )
            }
        )

        verify(repository.localRepository, times(1))
            .deleteOutdatedMediaContent(
                timestamp = any()
            )
    }

    @Test
    fun `get season part force, season part obtained from remote`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_episodes_no_offset.json")
        }

        val season = Carousel.createEmpty(TEST_SEASON_ID, TEST_LIBRARY_ID, "", 1)
        val offset = 0

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasonPart(
                    season = season,
                    callback = callback,
                    offset = offset,
                    force = true
                )
            }
        )

        verify(repository.localRepository, never())
            .getSeasonPart(
                season = any(),
                callback = any(),
                offset = any(),
                limit = any(),
                force = any(),
                tag = anyOrNull(),
                useMoreUrl = any()
            )
        verify(repository.remoteRepository, times(1))
            .getSeasonPart(
                season = eq(season),
                callback = any(),
                offset = any(),
                limit = any(),
                force = any(),
                tag = anyOrNull(),
                useMoreUrl = any()
            )
    }

    @Test
    fun `get season part, local empty, remote unresponsive, get NoDataException`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_episodes_empty.json",
        )

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasonPart(
                    season = Carousel.createEmpty(TEST_SEASON_ID, TEST_LIBRARY_ID, "", 1),
                    callback = callback
                )
            },
            onSuccess = {
                assertThat("Season should not be obtained", false)
            },
            onError = {
                assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
            }
        )
    }

    @Test
    fun `add or update categories, local category update called`() {
        val categoryList: List<Category> = mock()

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback = callback,
                    categoryList = categoryList
                )
            }
        )

        verifyNoInteractions(repository.remoteRepository)
        verify(repository.localRepository, times(1))
            .addOrUpdateCategoryList(
                callback = any(),
                categoryList = eq(categoryList),
                tag = anyOrNull(),
                expireTimestamp = anyOrNull()
            )
    }

    @Test
    fun `add or update carousels, local carousel update called`() {
        val carouselOffsetList: List<Pair<Carousel, Int>> = listOf(
            Carousel.createEmpty(TEST_CAROUSEL_ID, TEST_CATEGORY_ID, "", 1) to 0
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback = callback,
                    carouselList = carouselOffsetList
                )
            }
        )

        val captor = argumentCaptor<List<Pair<Carousel, Int>>>()
        verifyNoInteractions(repository.remoteRepository)
        verify(repository.localRepository, times(1))
            .addOrUpdateCarouselList(
                callback = any(),
                carouselList = captor.capture(),
                tag = anyOrNull(),
                contentExpireTimestamp = anyOrNull(),
                carouselExpireTimestamp = anyOrNull()
            )

        assertThat(captor.firstValue.size, equalTo(carouselOffsetList.size))
        assertThat(
            captor.firstValue[0].first.carouselId,
            equalTo(carouselOffsetList[0].first.carouselId)
        )
        assertThat(captor.firstValue[0].second, equalTo(carouselOffsetList[0].second))
    }

    @Test
    fun `add or update content items, local content items update called`() {
        val contentItems = listOf(
            VhEpisodeItem.createEmpty(
                episodeId = TEST_CONTENT_ID,
                episodeType = TEST_CONTENT_TYPE
            )
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateContentItems(
                    callback = callback,
                    contentItems = contentItems
                )
            }
        )

        val captor = argumentCaptor<List<ContentItem>>()
        verifyNoInteractions(repository.remoteRepository)
        verify(repository.localRepository, times(1))
            .addOrUpdateContentItems(
                callback = any(),
                contentItems = captor.capture(),
                tag = anyOrNull()
            )

        assertThat(captor.firstValue.size, equalTo(contentItems.size))
        assertThat(captor.firstValue[0].id, equalTo(contentItems[0].id))
    }

    @Test
    fun `clear repository, local cleared`() {
        repository.deleteAllMediaContent()

        verifyNoInteractions(repository.remoteRepository)
        verify(repository.localRepository, times(1))
            .deleteAllMediaContent()
    }

    @Test
    fun `clear outdated, local clear outdated called`() {
        val timestamp = 12345L

        repository.deleteOutdatedMediaContent(
            timestamp = timestamp
        )

        verifyNoInteractions(repository.remoteRepository)
        verify(repository.localRepository, times(1))
            .deleteOutdatedMediaContent(
                timestamp = eq(timestamp)
            )
    }

    @Test
    fun `cancel requests, local and remote cancel request called`() {
        val tag = Any()

        repository.cancelRequests(
            tag = tag
        )

        verify(repository.remoteRepository, times(1))
            .cancelRequests(
                tag = eq(tag)
            )
        verify(repository.localRepository, times(1))
            .cancelRequests(
                tag = eq(tag)
            )
    }
}
