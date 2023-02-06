package com.yandex.tv.home.repository

import android.os.Build
import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.common.utility.CancellableWorker
import com.yandex.tv.common.utility.test.RxImmediateSchedulerRule
import com.yandex.tv.home.content.MediaContentRepository
import com.yandex.tv.home.content.local.LocalMediaContentRepositoryImpl
import com.yandex.tv.home.di.homeAppModule
import com.yandex.tv.home.model.Carousel
import com.yandex.tv.home.model.Category
import com.yandex.tv.home.model.ContentItem
import com.yandex.tv.home.model.FilterBundle
import com.yandex.tv.home.model.FilterCategory
import com.yandex.tv.home.model.FilterInfo
import com.yandex.tv.home.model.SectionItem
import com.yandex.tv.home.model.vh.VhEpisodeItem
import com.yandex.tv.home.network.HttpRequestTask
import com.yandex.tv.home.policy.PolicyManager
import com.yandex.tv.home.utils.HttpRequestManager
import com.yandex.tv.home.utils.commonTestModule
import io.reactivex.rxjava3.core.Completable
import io.reactivex.rxjava3.schedulers.Schedulers
import org.hamcrest.MatcherAssert.assertThat
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
import org.mockito.kotlin.doAnswer
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.spy
import org.mockito.kotlin.stub
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException

private const val TEST_CAROUSEL_ID =
    "ChJoaGhkbmxtb2FqeWl6eW5kaGgSCXR2YW5kcm9pZBoibW92aWUmZ2VucmVfdGhyaWxsZXImcG9zdGVyX2V4aXN0cyABKAA="
private const val TEST_CATEGORY_ID = "main"
private const val TEST_CAROUSEL_TITLE = "Триллеры"

private const val ANOTHER_TEST_CAROUSEL_ID =
    "GhJoaGhkbmxtb2FqeWl6eW5kaGgSCXR2YW5kcm9pZBoibW92aWUmZ2VucmVfdGhyaWxsZXImcG9zdGVyX2V4aXN0cyABKAA="
private const val ANOTHER_TEST_CAROUSEL_TITLE = "Комедии"

private const val TEST_CONTENT_ID = "493e50ee9414369a86b073e29c81d030"
private const val TEST_CONTENT_TYPE = "vod-episode"

private const val TEST_SECTION_ID = "CATEG_FILM"
private const val TEST_SECTION_TYPE = "embedded_carousel"
private val TEST_FILTERS = listOf(
    FilterInfo("2010-2020", "year=ge:2010,lt:2020", 0),
    FilterInfo("Биография", "genre=ruw267584", 1)
)
private const val TEST_LIBRARY_ID = "4dbe3685655d2e7e99ea665f4b23ab29"
private const val TEST_SEASON_ID = "4b49cd710f76e67f9871889f1b48823c"


@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], application = RepositoryTestApp::class)
class LocalMediaContentRepositoryTest : KoinTest {

    @Rule
    @JvmField
    val schedulerRule = RxImmediateSchedulerRule()

    @Rule
    @JvmField
    val taskExecutorRule = InstantTaskExecutorRule()

    @Rule
    @JvmField
    var timeout: Timeout = Timeout(60000, TimeUnit.MILLISECONDS)

    private var callsExecutor = Executors.newSingleThreadExecutor()

    private lateinit var repository: LocalMediaContentRepositoryImpl

    private fun createRepository(): LocalMediaContentRepositoryImpl {
        return LocalMediaContentRepositoryImpl().also {
            it.init(ApplicationProvider.getApplicationContext())
            it.deleteAllMediaContent()
            it.resolver = spy(it.resolver)
            it.worker = CancellableWorker(spy(it.threadPolicy).databaseExecutor)
        }
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
    fun `addOrUpdateCarouselList on empty list, no throw`() {
        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    emptyList()
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )
    }

    @Test
    fun `addOrUpdateCategoryList on empty list, no throw`() {
        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback,
                    emptyList()
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )
    }

    @Test
    fun `addOrUpdateContentItems on empty list, no throw`() {
        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateContentItems(
                    callback,
                    emptyList()
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )
    }

    @Test
    fun `addOrUpdateCarouselList add item, no throw`() {
        val item = Carousel(
            TEST_CAROUSEL_ID,
            TEST_CAROUSEL_TITLE,
            categoryId = TEST_CATEGORY_ID,
            rank = 0
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    listOf(Pair(item, 0))
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )
    }

    @Test
    fun `addOrUpdateCategoryList add item, no throw`() {
        val item = Category(
            TEST_CATEGORY_ID,
            persistentId = null,
            title = TEST_CAROUSEL_TITLE,
            rank = 0,
            icon = null
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback,
                    listOf(item)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )
    }

    @Test
    fun `addOrUpdateContentItems add item, no throw`() {
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
    }

    @Test
    fun `addOrUpdateCarouselList updates item, getCarouselList gets item, no throw`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )
        val initialItem = Carousel(
            TEST_CAROUSEL_ID,
            TEST_CAROUSEL_TITLE,
            categoryId = TEST_CATEGORY_ID,
            items = listOf(contentItem),
            rank = 1
        )
        val finalItem = Carousel(
            TEST_CAROUSEL_ID,
            TEST_CAROUSEL_TITLE + "Test",
            categoryId = TEST_CATEGORY_ID,
            items = listOf(contentItem),
            rank = 1
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    listOf(Pair(initialItem, 0))
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback
                )
            },
            onSuccess = {
                assertThat(
                    "Initial items should be identical",
                    it.items.first().carouselId == initialItem.carouselId && it.items.first().title == initialItem.title
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
                    callback,
                    listOf(Pair(finalItem, 0))
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback
                )
            },
            onSuccess = {
                assertThat(
                    "Final items should be identical",
                    it.items.first().carouselId == finalItem.carouselId && it.items.first().title == finalItem.title
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )
    }

    @Test
    fun `addOrUpdateCategoryList updates item, getCategoryList gets item, item no throw`() {
        val initialItem = Category(
            TEST_CATEGORY_ID,
            persistentId = null,
            title = TEST_CAROUSEL_TITLE,
            rank = 1,
            icon = null
        )
        val finalItem = Category(
            TEST_CATEGORY_ID,
            persistentId = null,
            title = TEST_CAROUSEL_TITLE + "Test",
            rank = 1,
            icon = null
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback,
                    listOf(initialItem)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(callback)
            },
            onSuccess = {
                assertThat(
                    "Initial items should be identical",
                    it.first().categoryId == initialItem.categoryId && it.first().title == initialItem.title
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback,
                    listOf(finalItem)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(callback)
            },
            onSuccess = {
                assertThat(
                    "Final items should be identical",
                    it.first().categoryId == finalItem.categoryId && it.first().title == finalItem.title
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )
    }

    @Test
    fun `addOrUpdateContentItems updates item, getCardDetails gets item, no throw`() {
        val initialItem = VhEpisodeItem.createEmpty(
            playerId = "Test1",
            episodeId = TEST_CONTENT_ID

        )
        val finalItem = VhEpisodeItem.createEmpty(
            playerId = "Test2",
            episodeId = TEST_CONTENT_ID
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateContentItems(
                    callback,
                    listOf(initialItem)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }

        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.markDetailed(listOf(initialItem), callback)
            }
        )

        repositoryExecuteBlocking<ContentItem>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCardDetails(initialItem, callback)
            },
            onSuccess = {
                assertThat(
                    "Initial items should be identical",
                    it is VhEpisodeItem && it.id == initialItem.id && it.playerId == initialItem.playerId
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateContentItems(
                    callback,
                    listOf(finalItem)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<ContentItem>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCardDetails(initialItem, callback)
            },
            onSuccess = {
                assertThat(
                    "Final items should be identical",
                    it is VhEpisodeItem && it.id == finalItem.id && it.playerId == finalItem.playerId
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )
    }

    @Test
    fun `getActualPagingInfo empty data, no throw`() {
        repositoryExecuteBlocking<MediaContentRepository.PagingInfo>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getActualPagingInfo(TEST_CONTENT_ID, callback, null)
            },
            onSuccess = {
                assertThat(
                    "Should return empty PagingInfo",
                    it.id == TEST_CONTENT_ID && it.moreUrl == null
                )
            },
            onError = {
                assertThat("Should return empty PagingInfo", false)
            }
        )
    }

    @Test
    fun `persistPagingInfo, getActualPagingInfo, data not changed`() {
        val testPagingId = "test_paging_info"
        val pagingInfo = MediaContentRepository.PagingInfoImpl(testPagingId, "test_more_url")

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.persistPagingInfo(pagingInfo, callback)
            },
            onError = {
                assertThat("$it: Should persist paging info", false)
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.PagingInfo>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getActualPagingInfo(
                    pagingItemId = testPagingId,
                    callback = callback,
                    tag = null
                )
            },
            onSuccess = {
                assertThat(it.id, equalTo(pagingInfo.id))
                assertThat(it.moreUrl, equalTo(pagingInfo.moreUrl))
            },
            onError = {
                assertThat("$it: Should return PagingInfo", false)
            }
        )
    }

    @Test
    fun `getCardDetails no data, throw NoDataException`() {
        repositoryExecuteBlocking<ContentItem>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCardDetails(
                    VhEpisodeItem.createEmpty(TEST_CONTENT_ID, "test"),
                    callback
                )
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )
    }

    @Test
    fun `getCarouselList no data, throw NoDataException`() {
        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback
                )
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )
    }

    @Test
    fun `getCarouselPart no data, throw NoDataException`() {
        val carousel = Carousel(
            TEST_CAROUSEL_ID,
            TEST_CAROUSEL_TITLE,
            categoryId = TEST_CATEGORY_ID,
            rank = 1
        )

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselPart(carousel, callback)
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )
    }

    @Test
    fun `getCarouselPart with data, data obtained`() {
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
                    callback = callback,
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
    }

    @Test
    fun `getCategoryList no data, throw NoDataException`() {
        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(callback)
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )
    }

    @Test
    fun `getSeasonPart no data, throw NoDataException`() {
        val season = Carousel(
            TEST_CAROUSEL_ID,
            TEST_CAROUSEL_TITLE,
            categoryId = TEST_CATEGORY_ID,
            rank = 1
        )

        repositoryExecuteBlocking<Carousel>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasonPart(season, callback)
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )
    }

    @Test
    fun `getSeasonPart with data, data obtained`() {
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
    }

    @Test
    fun `getSeasons no data, throw NoDataException`() {
        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasons(MediaContentRepository.EmptyPagingInfo("main"), callback)
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )
    }

    @Test
    fun `getSeasons with data, data obtained`() {
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

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    listOf(Pair(carousel, 0))
                )
            }
        )

        val pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_LIBRARY_ID)

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
    }

    @Test
    fun `getSectionDetails no data, throw NoDataException`() {
        val section = SectionItem("", "")

        repositoryExecuteBlocking<MediaContentRepository.SectionDetails>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSectionDetails(section, callback)
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )
    }

    @Test
    fun `getSectionDetails with data, data obtained`() {
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
                    callback,
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
    }

    @Test
    fun `getCarouselList expired data, throw DataExpiredException`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )

        val initialItem = Carousel(
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
                    listOf(Pair(initialItem, 0)),
                    contentExpireTimestamp = 0,
                    carouselExpireTimestamp = 0
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback
                )
            },
            onSuccess = {
                assertThat("Should throw DataExpiredException, not $it", false)
            },
            onError = {
                assertThat(
                    "$it is DataExpiredException",
                    it is MediaContentRepository.DataExpiredException
                )
            }
        )
    }

    @Test
    fun `getCategoryList expired data, throw DataExpiredException`() {
        val item = Category(
            TEST_CATEGORY_ID,
            persistentId = null,
            title = TEST_CAROUSEL_TITLE,
            rank = 0,
            icon = null
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback,
                    listOf(item),
                    expireTimestamp = 0
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(callback)
            },
            onSuccess = {
                assertThat("Should throw DataExpiredException, not $it", false)
            },
            onError = {
                assertThat(
                    "$it is DataExpiredException",
                    it is MediaContentRepository.DataExpiredException
                )
            }
        )
    }

    @Test
    fun `deleteOutdatedMediaContent deletes outdated content`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )

        val categoryItem = Category(
            TEST_CATEGORY_ID,
            persistentId = null,
            title = TEST_CAROUSEL_TITLE,
            rank = 0,
            icon = null
        )

        val carouselItem = Carousel(
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
                    listOf(Pair(carouselItem, 0)),
                    contentExpireTimestamp = 0,
                    carouselExpireTimestamp = 0
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback,
                    listOf(categoryItem),
                    expireTimestamp = 0
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repository.deleteOutdatedMediaContent(System.currentTimeMillis())

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback
                )
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(callback)
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )
    }

    @Test
    fun `deleteOutdatedMediaContent deletes only outdated content`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )

        val categoryItem = Category(
            TEST_CATEGORY_ID,
            persistentId = null,
            title = TEST_CAROUSEL_TITLE,
            rank = 0,
            icon = null
        )

        val carouselItem = Carousel(
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
                    listOf(Pair(carouselItem, 0))
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback,
                    listOf(categoryItem)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repository.deleteOutdatedMediaContent(System.currentTimeMillis())

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback
                )
            },
            onError = {
                assertThat("Should not throw exceptions, but got $it", false)
            }
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(callback)
            },
            onError = {
                assertThat("Should not throw exceptions, but got $it", false)
            }
        )
    }

    @Test
    fun `deleteAllMediaContent deletes all media content`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )

        val categoryItem = Category(
            TEST_CATEGORY_ID,
            persistentId = null,
            title = TEST_CAROUSEL_TITLE,
            rank = 0,
            icon = null
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
                repository.addOrUpdateContentItems(
                    callback,
                    listOf(contentItem)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.markDetailed(listOf(contentItem), callback)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    listOf(Pair(carousel, 0))
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback,
                    listOf(categoryItem)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repository.deleteAllMediaContent()

        repositoryExecuteBlocking<ContentItem>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCardDetails(contentItem, callback)
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback
                )
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(callback)
            },
            onSuccess = {
                assertThat("Should throw NoDataException, not $it", false)
            },
            onError = {
                assertThat("$it is NoDataException", it is MediaContentRepository.NoDataException)
            }
        )
    }

    @Test
    fun `deleteCarouselsForPage deletes only carousels for page`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )

        val categoryItem = Category(
            TEST_CATEGORY_ID,
            persistentId = null,
            title = TEST_CAROUSEL_TITLE,
            rank = 0,
            icon = null
        )

        val carouselItem = Carousel(
            TEST_CAROUSEL_ID,
            TEST_CAROUSEL_TITLE,
            categoryId = TEST_CATEGORY_ID,
            items = listOf(contentItem),
            rank = 1
        )
        val anotherCarouselItem = Carousel(
            ANOTHER_TEST_CAROUSEL_ID,
            ANOTHER_TEST_CAROUSEL_TITLE,
            categoryId = TEST_CATEGORY_ID,
            items = listOf(contentItem),
            rank = 2
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    listOf(Pair(carouselItem, 0), Pair(anotherCarouselItem, 0))
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCategoryList(
                    callback,
                    listOf(categoryItem)
                )
            },
            onError = {
                assertThat("Got $it, but should not throw exceptions", false)
            }
        )

        repositoryExecuteBlocking<Unit>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.deleteCarouselsForPage(
                    pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback = callback,
                    offset = 0,
                    limit = 1,
                    carouselOffset = 0,
                    carouselLimit = -1,
                    filters = emptyList(),
                    allowEmptyCarousels = true,
                    force = false,
                    tag = null
                )
            },
            onError = {
                assertThat("Should not throw exceptions, but got $it", false)
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback = callback,
                    offset = 0,
                    limit = 1
                )
            },
            onError = {
                assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback = callback,
                    offset = 1,
                    limit = 1
                )
            },
            onError = {
                assertThat("Should not throw exceptions, but got $it", false)
            }
        )

        repositoryExecuteBlocking<List<Category>>(
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(callback)
            },
            onError = {
                assertThat("Should not throw exceptions, but got $it", false)
            }
        )
    }

    @Test
    fun `cancelRequests cancels all requests`() {
        val contentItem = VhEpisodeItem.createEmpty(
            episodeId = TEST_CONTENT_ID,
            episodeType = TEST_CONTENT_TYPE
        )

        val tag = "TAG"

        val section = SectionItem("", "")

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
                repository.markDetailed(listOf(contentItem), callback)
            }
        )

        repositoryExecuteBlocking<ContentItem>(
            timeout = 5000,
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCardDetails(contentItem, callback, tag = tag)
                repository.cancelRequests(tag)
            },
            onSuccess = {
                assertThat("Should throw TimeoutException, not $it", false)
            },
            onError = {
                assertThat("$it is TimeoutException", it is TimeoutException)
            }
        )

        repositoryExecuteBlocking<Carousel>(
            timeout = 5000,
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselPart(carousel, callback, tag = tag)
                repository.cancelRequests(tag)
            },
            onSuccess = {
                assertThat("Should throw TimeoutException, not $it", false)
            },
            onError = {
                assertThat("$it is TimeoutException", it is TimeoutException)
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.SectionDetails>(
            timeout = 5000,
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSectionDetails(section, callback, tag = tag)
                repository.cancelRequests(tag)
            },
            onSuccess = {
                assertThat("Should throw TimeoutException, not $it", false)
            },
            onError = {
                assertThat("$it is TimeoutException", it is TimeoutException)
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            timeout = 5000,
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasons(
                    MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback,
                    tag = tag
                )
                repository.cancelRequests(tag)
            },
            onSuccess = {
                assertThat("Should throw TimeoutException, not $it", false)
            },
            onError = {
                assertThat("$it is TimeoutException", it is TimeoutException)
            }
        )

        repositoryExecuteBlocking<Carousel>(
            timeout = 5000,
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getSeasonPart(carousel, callback, tag = tag)
                repository.cancelRequests(tag)
            },
            onSuccess = {
                assertThat("Should throw TimeoutException, not $it", false)
            },
            onError = {
                assertThat("$it is TimeoutException", it is TimeoutException)
            }
        )

        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            timeout = 5000,
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCarouselList(
                    MediaContentRepository.EmptyPagingInfo(TEST_CATEGORY_ID),
                    callback,
                    tag = tag
                )
                repository.cancelRequests(tag)
            },
            onSuccess = {
                assertThat("Should throw TimeoutException, not $it", false)
            },
            onError = {
                assertThat("$it is TimeoutException", it is TimeoutException)
            }
        )

        repositoryExecuteBlocking<List<Category>>(
            timeout = 5000,
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.getCategoryList(callback, tag = tag)
                repository.cancelRequests(tag)
            },
            onSuccess = {
                assertThat("Should throw TimeoutException, not $it", false)
            },
            onError = {
                assertThat("$it is TimeoutException", it is TimeoutException)
            }
        )
    }
}
