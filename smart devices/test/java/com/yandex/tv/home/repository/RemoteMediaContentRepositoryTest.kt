package com.yandex.tv.home.repository

import android.os.Build
import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.common.utility.test.RxImmediateSchedulerRule
import com.yandex.tv.home.content.MediaContentRepository
import com.yandex.tv.home.content.remote.RemoteMediaContentRepositoryImpl
import com.yandex.tv.home.di.homeAppModule
import com.yandex.tv.home.model.Carousel
import com.yandex.tv.home.model.CarouselWithFilters
import com.yandex.tv.home.model.FilterInfo
import com.yandex.tv.home.model.SectionItem
import com.yandex.tv.home.model.vh.VhEpisodeItem
import com.yandex.tv.home.network.HttpRequestTask
import com.yandex.tv.home.network.ResponseException
import com.yandex.tv.home.network.RestApi
import com.yandex.tv.home.policy.PolicyManager
import com.yandex.tv.home.utils.HttpRequestManager
import com.yandex.tv.home.utils.commonTestModule
import io.reactivex.rxjava3.core.Completable
import io.reactivex.rxjava3.schedulers.Schedulers
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.greaterThan
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
import org.mockito.kotlin.argThat
import org.mockito.kotlin.doAnswer
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.spy
import org.mockito.kotlin.stub
import org.mockito.kotlin.verify
import org.mockito.kotlin.verifyNoInteractions
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException

//from response_carousels.json
private const val CAROUSELS_MAIN_MORE_PATH =
    "api/v7/carousels?category_id=main&limit=10&offset=10&cache_hash=egEAAAAAAAAotS_9YHoAzQQAYkwfFoAHYEAYk1lKfRjEZDdpOW_wdlYaaHBjxowZIzBjxowJmCRLqnOdLH3_J0RJF8m-O9ra8CSkaku_L_2vWroopDbXttDOPtuyqhD8855_0a1q5wiietfKbvcMb3ZC7ElJqPejTcs2IXQ1vR-t3rSmuhADhIOBoZBAUFAYACQJmBDq_f8dBxB-Smz5yWPxcEG_vV1ny7kU&max_items_count=10&external_carousel_offset=1"

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
class RemoteMediaContentRepositoryTest : KoinTest {

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

    private lateinit var repository: RemoteMediaContentRepositoryImpl

    private fun createRepository(): RemoteMediaContentRepositoryImpl {
        return RemoteMediaContentRepositoryImpl().also {
            it.init(ApplicationProvider.getApplicationContext())
            it.contentResolver = spy(it.contentResolver)
            it.policyManager = spy(it.policyManager)
            it.threadPolicy = spy(it.threadPolicy)
            it.requestManager = spy(it.requestManager)
        }
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
    fun `get categories, backend available, categories obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_categories.json"
        )
        repository.getCategoryList(
            callback = createCallback(
                onSuccess = {
                    assertThat(it.isEmpty(), equalTo(false))
                },
                onError = {
                    assertThat("$it: categories should be obtained", false)
                }
            )
        )
    }

    @Test
    fun `get categories, backend unavailable, categories not obtained`() {
        createServer().also {
            //to fail after retries
            it.enqueueServerResponse(responseCode = 500)
            it.enqueueServerResponse(responseCode = 500)
            it.enqueueServerResponse(responseCode = 500)
        }
        repository.getCategoryList(
            callback = createCallback(
                onSuccess = {
                    assertThat("Request should fail when server is unresponsive", false)
                },
                onError = {
                    assertThat(it, instanceOf(TimeoutException::class.java))
                }
            ),
        )
    }

    @Test
    fun `get carousels, category id invalid, carousels not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousels_invalid.json",
            responseCode = 404
        )
        repository.getCarouselList(
            pagingInfo = MediaContentRepository.EmptyPagingInfo("invalid"),
            callback = createCallback(
                onSuccess = {
                    assertThat("Request should fail when invalid id specified", false)
                },
                onError = {
                    assertThat(it, instanceOf(ResponseException::class.java))
                }
            )
        )
    }

    @Test
    fun `get carousels, category id valid, empty response, carousels not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousels_empty.json",
        )
        repository.getCarouselList(
            pagingInfo = MediaContentRepository.EmptyPagingInfo("invalid"),
            callback = createCallback(onSuccess = {
                assertThat("Request should fail on empty response", false)
            },
                onError = {
                    assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
                })
        )
    }

    @Test
    fun `get carousels, category id valid, offset 0, carousels obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousels_main.json",
        )

        repository.getCarouselList(
            pagingInfo = MediaContentRepository.EmptyPagingInfo("main"),
            callback = createCallback(
                onSuccess = {
                    assertThat(it.items.isEmpty(), equalTo(false))
                },
                onError = {
                    assertThat("$it: Request should succeed", false)
                }
            ),
            offset = 0
        )

        repository.getCarouselList(
            pagingInfo = MediaContentRepository.EmptyPagingInfo("main"),
            callback = createCallback(
                onSuccess = {
                    assertThat(it.items.isEmpty(), equalTo(false))
                },
                onError = {
                    assertThat("$it: Request should succeed", false)
                }
            ),
            offset = 0
        )
    }

    @Test
    fun `get carousels, category id valid, offset not 0, more url exists, carousels obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousels_main.json",
        )
        repository.getCarouselList(
            pagingInfo = MediaContentRepository.PagingInfoImpl(
                "main",
                carouselsMainMoreUrl
            ),
            callback = createCallback(
                onSuccess = {
                    assertThat(it.items.isEmpty(), equalTo(false))
                },
                onError = {
                    assertThat("$it: Carousels should be obtained", false)
                }),
            offset = 10
        )
    }

    @Test
    fun `get carousels, category id valid, offset not 0, more url missing, carousels not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousels_main.json",
        )
        repository.getCarouselList(
            pagingInfo = MediaContentRepository.EmptyPagingInfo("main"),
            callback = createCallback(
                onSuccess = {
                    assertThat("Should not succeed without more url", false)
                },
                onError = {
                    assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
                }
            ),
            offset = 10
        )
    }

    @Test
    fun `get carousel part, carousel invalid, carousel not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_invalid.json",
        )
        repository.getCarouselPart(
            carousel = Carousel.createEmpty("invalid", "", "", 0),
            callback = createCallback(onSuccess = {
                assertThat("Request should fail when invalid id specified", false)
            },
                onError = {
                    assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
                })
        )
    }

    @Test
    fun `get carousel part, carousel valid, offset 0, carousel part obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_no_offset.json",
        )
        repository.getCarouselPart(
            carousel = Carousel.createEmpty(
                carouselId = TEST_CAROUSEL_ID,
                categoryId = TEST_CATEGORY_ID,
                title = TEST_CAROUSEL_TITLE,
                rank = 0,
            ),
            callback = createCallback(
                onSuccess = {
                    assertThat(it.items.isEmpty(), equalTo(false))
                },
                onError = {
                    assertThat("$it: Carousels should be obtained", false)
                }
            )
        )
    }

    @Test
    fun `get carousel part, carousel valid, offset not 0, more url exists, carousel part obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_offset_10.json",
        )
        repository.getCarouselPart(
            carousel = Carousel.createEmpty(
                carouselId = TEST_CAROUSEL_ID,
                categoryId = TEST_CATEGORY_ID,
                title = TEST_CAROUSEL_TITLE,
                rank = 0,
                moreInfo = Carousel.MoreInfo(testCarouselMoreUrl10)
            ),
            callback = createCallback(
                onSuccess = {
                    assertThat(it.items.isEmpty(), equalTo(false))
                },
                onError = {
                    assertThat("$it: Carousel should be obtained", false)
                }
            ),
            offset = 10
        )
    }

    @Test
    fun `get carousel part, carousel valid, offset not 0, more url missing, carousel part not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_offset_10.json",
        )
        repository.getCarouselPart(
            carousel = Carousel.createEmpty(
                carouselId = TEST_CAROUSEL_ID,
                categoryId = TEST_CATEGORY_ID,
                title = TEST_CAROUSEL_TITLE,
                rank = 0,
            ),
            callback = createCallback(
                onSuccess = {
                    assertThat("Carousel should not be obtained", false)
                },
                onError = {
                    assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
                }
            ),
            offset = 10
        )
    }

    @Test
    fun `get carousel part, carousel valid, filters not empty, more url exists, carousel part obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_no_offset_filters.json",
        )
        repository.getCarouselPart(
            carousel = Carousel.createEmpty(
                carouselId = TEST_FILTERS_CAROUSEL_ID,
                categoryId = TEST_FILTERS_CATEGORY_ID,
                title = TEST_FILTERS_CAROUSEL_TITLE,
                rank = 0,
                moreInfo = Carousel.MoreInfo(testFiltersMoreUrl)
            ),
            callback = createCallback(
                onSuccess = {
                    assertThat(it.items.isEmpty(), equalTo(false))
                },
                onError = {
                    assertThat("$it: Carousel should be obtained", false)
                }
            ),
            offset = 0,
            filters = TEST_FILTERS
        )
    }

    @Test
    fun `get carousel part, carousel valid, filters not empty, more url missing, carousel part not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_no_offset_filters.json",
        )
        repository.getCarouselPart(
                    carousel = Carousel.createEmpty(
                        carouselId = TEST_FILTERS_CAROUSEL_ID,
                        categoryId = TEST_FILTERS_CATEGORY_ID,
                        title = TEST_FILTERS_CAROUSEL_TITLE,
                        rank = 0,
                    ),
                    callback = createCallback(
                        onSuccess = {
                            assertThat("Carousel should not be obtained", false)
                        },
                        onError = {
                            assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
                        }
                    ),
                    offset = 0,
                    filters = TEST_FILTERS
                )
    }

    @Test
    fun `get card details, content item invalid, card details not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_card_detail_invalid.json",
            responseCode = 404
        )
        repository.getCardDetails(
            contentItem = VhEpisodeItem.createEmpty(
                episodeId = "invalid",
                episodeType = TEST_CONTENT_TYPE
            ),
            callback = createCallback(
                onSuccess = {
                    assertThat("Card detail should not be obtained", false)
                },
                onError = {
                    assertThat(it, instanceOf(ResponseException::class.java))
                }
            ),
        )
    }

    @Test
    fun `get card details, content item valid, card details obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_card_detail.json",
        )
        repository.getCardDetails(
            contentItem = VhEpisodeItem.createEmpty(
                episodeId = TEST_CONTENT_ID,
                episodeType = TEST_CONTENT_TYPE
            ),
            callback = createCallback(
                onSuccess = {
                    assertThat(it, instanceOf(VhEpisodeItem::class.java))
                    assertThat(it.id, equalTo(TEST_CONTENT_ID))
                    assertThat(it.contentType, equalTo(TEST_CONTENT_TYPE))
                },
                onError = {
                    assertThat("$it: Card details should be obtained", false)
                }
            ),
        )
    }

    @Test
    fun `get section details, section item invalid, section details not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_carousel_invalid.json"
        )
        repository.getSectionDetails(
            sectionItem = SectionItem("invalid", TEST_SECTION_TYPE),
            callback = createCallback(
                onSuccess = {
                    assertThat("Section should not be obtained", false)
                },
                onError = {
                    assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
                }
            )
        )
    }

    @Test
    fun `get section details, section item valid, offset 0, section details obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_section_details.json"
        )
        repository.getSectionDetails(
            sectionItem = SectionItem(TEST_SECTION_ID, TEST_SECTION_TYPE),
            callback = createCallback(onSuccess = {
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
                })
        )
    }

    @Test
    fun `get season part, season invalid, carousels not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_episodes_invalid.json",
            responseCode = 404
        )

        repository.getSeasonPart(
            season = Carousel.createEmpty("invalid", "", "", 1),
            callback = createCallback(
                onSuccess = {
                    assertThat("Season should not be obtained", false)
                },
                onError = {
                    assertThat(it, instanceOf(ResponseException::class.java))
                }
            ),
            offset = 0
        )
    }

    @Test
    fun `get season part, season valid, offset 0, carousels part obtained`() {
        createServer().enqueueServerResponse(responseFileName = "raw/response_episodes_no_offset.json")
        repository.getSeasonPart(
            season = Carousel.createEmpty(TEST_SEASON_ID, TEST_LIBRARY_ID, "", 1),
            callback = createCallback(
                onSuccess = {
                    assertThat(it.items.isNotEmpty(), equalTo(true))
                },
                onError = {
                    assertThat("$it: Season should be obtained", false)
                }
            ),
            offset = 0
        )
    }

    @Test
    fun `get season part, season valid, offset not 0, more url missing, carousel part not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_episodes_offset_10.json",
        )
        repository.getSeasonPart(
            season = Carousel.createEmpty(TEST_SEASON_ID, TEST_LIBRARY_ID, "", 1),
            callback = createCallback(
                onSuccess = {
                    assertThat("Season should not be obtained", false)
                },
                onError = {
                    assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
                }
            ),
            offset = 10
        )
    }

    @Test
    fun `get season part, season valid, offset not 0, more url exists, carousel part obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_episodes_offset_10.json"
        )
        repository.getSeasonPart(
            season = Carousel.createEmpty(
                TEST_SEASON_ID,
                TEST_LIBRARY_ID,
                "",
                1,
                Carousel.MoreInfo(testSeasonMoreUrl)
            ),
            callback = createCallback(
                onSuccess = {
                    assertThat(it.items.isNotEmpty(), equalTo(true))
                },
                onError = {
                    assertThat("$it: Season should be obtained", false)
                }
            ),
            offset = 10
        )
    }

    @Test
    fun `get seasons, library id invalid, carousels not obtained`() {
        createServer().enqueueServerResponse(
            responseFileName = "raw/response_seasons_invalid.json",
            responseCode = 404
        )
        repository.getSeasons(
            pagingInfo = MediaContentRepository.EmptyPagingInfo("invalid"),
            callback = createCallback(
                onSuccess = {
                    assertThat("Season should not be obtained", false)
                },
                onError = {
                    assertThat(it, instanceOf(ResponseException::class.java))
                }
            )
        )
    }

    @Test
    fun `get seasons, library id valid, offset 0, carousels obtained with first not empty`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_seasons_no_offset.json")
            enqueueServerResponse(responseFileName = "raw/response_episodes_no_offset.json")
        }
        repository.getSeasons(
            pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_LIBRARY_ID),
            callback = createCallback(
                onSuccess = {
                    assertThat(it.items.isNotEmpty(), equalTo(true))
                    assertThat(it.items[0].items.size, greaterThan(1))
                },
                onError = {
                    assertThat("$it: Seasons should be obtained", false)
                }
            ),
            offset = 0
        )
    }

    @Test
    fun `get seasons, library id valid, offset not 0, more url exists, carousels obtained with first not empty`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_seasons_offset_10.json")
            enqueueServerResponse(responseFileName = "raw/response_episodes_offset_10.json")
        }
        repository.getSeasons(
            pagingInfo = MediaContentRepository.PagingInfoImpl(
                TEST_LIBRARY_ID,
                testSeasonsMoreUrl
            ),
            callback = createCallback(onSuccess = {
                assertThat(it.items.isNotEmpty(), equalTo(true))
                assertThat(it.items[0].items.size, greaterThan(1))
            },
                onError = {
                    assertThat("$it: Seasons should be obtained", false)
                }),
            offset = 10
        )
    }

    @Test
    fun `get seasons, library id valid, offset not 0, more url missing, carousels not obtained`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_seasons_offset_10.json")
            enqueueServerResponse(responseFileName = "raw/response_episodes_offset_10.json")
        }
        repository.getSeasons(
            pagingInfo = MediaContentRepository.EmptyPagingInfo(TEST_LIBRARY_ID),
            callback = createCallback(
                onSuccess = {
                    assertThat("$it: Seasons should not be obtained", false)
                },
                onError = {
                    assertThat(it, instanceOf(MediaContentRepository.NoDataException::class.java))
                }
            ),
            offset = 10
        )
    }

    @Test
    fun `add or update categories, nothing happens`() {
        repository.addOrUpdateCategoryList(
            createCallback(),
            mock()
        )

        verifyNoInteractions(
            repository.requestManager,
            repository.threadPolicy,
            repository.policyManager,
            repository.contentResolver
        )
    }

    @Test
    fun `add or update carousels, nothing happens`() {
        repositoryExecuteBlocking<Unit>(
            timeout = 5000,
            executor = callsExecutor,
            repositoryCall = { callback ->
                repository.addOrUpdateCarouselList(
                    callback,
                    mock()
                )
            }
        )

        verifyNoInteractions(
            repository.requestManager,
            repository.threadPolicy,
            repository.policyManager,
            repository.contentResolver
        )
    }

    @Test
    fun `add or update content items, nothing happens`() {
        repository.addOrUpdateContentItems(
            createCallback(),
            mock()
        )

        verifyNoInteractions(
            repository.requestManager,
            repository.threadPolicy,
            repository.policyManager,
            repository.contentResolver
        )
    }

    @Test
    fun `clear repository, nothing happens`() {
        repository.deleteAllMediaContent()

        verifyNoInteractions(
            repository.requestManager,
            repository.threadPolicy,
            repository.policyManager,
            repository.contentResolver
        )
    }

    @Test
    fun `clear outdated, nothing happens`() {
        repository.deleteOutdatedMediaContent(0)

        verifyNoInteractions(
            repository.requestManager,
            repository.threadPolicy,
            repository.policyManager,
            repository.contentResolver
        )
    }

    @Test
    fun `cancel requests, no callbacks called`() {
        createServer().apply {
            enqueueServerResponse(responseFileName = "raw/response_seasons_offset_10.json")
            enqueueServerResponse(responseFileName = "raw/response_episodes_offset_10.json")
        }
        val callback =
            mock<MediaContentRepository.Callback<MediaContentRepository.CarouselListWithMetadata>>()
        val tag = Any()

        //sample request
        repositoryExecuteBlocking<MediaContentRepository.CarouselListWithMetadata>(
            timeout = 5000,
            executor = callsExecutor,
            repositoryCall = { wrappedCallback ->
                repository.getSeasons(
                    pagingInfo = MediaContentRepository.PagingInfoImpl(
                        TEST_LIBRARY_ID,
                        testSeasonsMoreUrl
                    ),
                    callback = wrappedCallback,
                    offset = 10,
                    tag = tag
                )
                repository.cancelRequests(tag)
            },
            onSuccess = {
                callback.onSuccess(it)
            },
            onError = {
                callback.onError(it)
            }
        )

        verify(callback, never()).onError(argThat { it -> it !is TimeoutException })
        verify(callback, never()).onSuccess(anyOrNull())
    }
}
