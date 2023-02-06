package com.yandex.tv.home.contract

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Looper.getMainLooper
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.common.contract.home.HomeAppDeeplinkContract
import com.yandex.tv.common.contract.home.HomeAppDeeplinkContract.FROM_ALICE_DIRECT
import com.yandex.tv.common.utility.test.injectActivitySpy
import com.yandex.tv.home.BaseHomeActivity
import com.yandex.tv.home.BrowsingActivity
import com.yandex.tv.home.HomeActivity
import com.yandex.tv.home.WebViewActivity
import com.yandex.tv.home.di.homeAppModule
import com.yandex.tv.home.model.vh.VhEpisodeItem
import com.yandex.tv.home.model.vh.VhLibraryItem
import com.yandex.tv.home.passport.HomeAccountManagerFacade
import com.yandex.tv.home.routing.DeeplinkSource
import com.yandex.tv.home.routing.HomeAppRouter
import com.yandex.tv.home.search.SearchFragment
import com.yandex.tv.home.ui.details.DetailsViewModel
import com.yandex.tv.home.ui.details.providers.EpisodeDataProvider
import com.yandex.tv.home.ui.details.providers.LibraryDataProvider
import com.yandex.tv.home.ui.fragments.CategoryFragment
import com.yandex.tv.home.ui.fragments.DetailsFragment
import com.yandex.tv.home.ui.fragments.HeadersContentFragment
import com.yandex.tv.home.ui.fragments.HomeFragment
import com.yandex.tv.home.ui.fragments.PlusPurchaseSuggestionFragment
import com.yandex.tv.home.ui.fragments.SeriesFragment
import com.yandex.tv.home.ui.fragments.WebViewFragment
import com.yandex.tv.home.utils.commonTestModule
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.instanceOf
import org.junit.After
import org.junit.Before
import org.junit.Ignore
import org.junit.Test
import org.junit.runner.RunWith
import org.koin.android.ext.koin.androidContext
import org.koin.core.context.startKoin
import org.koin.core.context.stopKoin
import org.koin.test.KoinTest
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.eq
import org.mockito.kotlin.never
import org.mockito.kotlin.spy
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.android.controller.ActivityController
import org.robolectric.annotation.Config
import java.util.concurrent.TimeUnit

private const val TEST_SEARCH_QUERY = "test query"
private const val TEST_EPISODE_ID = "4e618e9ed093491eb17650097198c56e"
private const val TEST_EPISODE_TYPE = "vod-episode"
private const val TEST_LIBRARY_ID = "a8ac855dd1bb769b157e38606324809"
private const val TEST_SEASON_ID = "4a00078db42c6f88934438fb9699f4a4f"
private const val TEST_SEASON_NUMBER = "2"
private const val TEST_LIBRARY_TYPE = "vod-library"
private const val TEST_ONTO_ID = "ruw2991697"
private const val TEST_REQUEST_ID = "some-request-id"
private const val TEST_URL = "https://ya.ru"

private const val TEST_SEARCH_BROKEN_URI = "home-app://search"
private const val TEST_BROWSE_BROKEN_URI = "home-app://browse"
private const val TEST_OPEN_URL_BROKEN_URI = "home-app://open_url"

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], application = HomeAppContractTestApp::class)
class DeeplinkHomeAppContractTest: KoinTest {

    private var controller: ActivityController<out BaseHomeActivity>? = null
    private var activitySpy: BaseHomeActivity? = null
    private var routerSpy: HomeAppRouter? = null

    private fun prepareActivity(clazz: Class<out BaseHomeActivity>, intent: Intent? = null) {
        controller = Robolectric.buildActivity(clazz, intent)
            .also { controller ->
                activitySpy = spy(controller.get())
                    .also { activity ->
                        injectActivitySpy(controller, activity)
                        routerSpy = activity.scope.get()
                    }
            }
    }

    private fun launchActivity() {
        controller?.apply {
            create()
            shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
            postCreate(null)
            shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
            start()
            shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
            resume()
            shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
            postResume()
            shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
            visible()
        }
        shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
    }

    private fun sendIntent(intent: Intent) {
        controller?.newIntent(intent)
        shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
    }

    private fun destroyActivity() {
        controller?.apply {
            pause()
            shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
            stop()
            shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
            destroy()
        }
       shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
    }

    @Before
    fun setUp() {
        startKoin {
            androidContext(ApplicationProvider.getApplicationContext())
            modules(listOf(homeAppModule, commonTestModule, deeplinkTestModule))
        }
        HomeAccountManagerFacade.onAppCreate(ApplicationProvider.getApplicationContext())
    }

    @After
    fun tearDown() {
        routerSpy = null
        activitySpy = null
        controller = null
        stopKoin()
    }

    @Test
    fun `home app not created, home requested, home launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = HomeAppDeeplinkContract.buildMainUri()
        }
        prepareActivity(HomeActivity::class.java, intent)
        launchActivity()

        verify(routerSpy, times(1))?.navigateToStart()
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(HeadersContentFragment::class.java))
        val rootContentFragment = (rootFragment as HeadersContentFragment).getCurrentFragment()
        assertThat(rootContentFragment, instanceOf(HomeFragment::class.java))

        destroyActivity()
    }

    @Test
    fun `home app created, home requested, home launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = HomeAppDeeplinkContract.buildMainUri()
        }
        prepareActivity(HomeActivity::class.java)
        launchActivity()
        sendIntent(intent)

        verify(routerSpy, times(1))?.navigateToStart()
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(HeadersContentFragment::class.java))
        val rootContentFragment = (rootFragment as HeadersContentFragment).getCurrentFragment()
        assertThat(rootContentFragment, instanceOf(HomeFragment::class.java))

        destroyActivity()
    }

    @Test
    fun `home app not created, plus purchase requested, plus purchase launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = HomeAppDeeplinkContract.buildPlusSuggestionUri()
        }
        prepareActivity(HomeActivity::class.java, intent)
        launchActivity()

        verify(routerSpy, times(1))?.openPurchasePlus()
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(PlusPurchaseSuggestionFragment::class.java))

        destroyActivity()
    }

    @Test
    fun `home app created, plus purchase requested, plus purchase launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = HomeAppDeeplinkContract.buildPlusSuggestionUri()
        }
        prepareActivity(HomeActivity::class.java)
        launchActivity()
        sendIntent(intent)

        verify(routerSpy, times(1))?.openPurchasePlus()
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(PlusPurchaseSuggestionFragment::class.java))

        destroyActivity()
    }

    @Test
    fun `home not app created, profile requested, profile launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = HomeAppDeeplinkContract.buildProfileUri()
        }
        prepareActivity(HomeActivity::class.java, intent)
        launchActivity()

        verify(routerSpy, times(1))?.openProfile()

        destroyActivity()
    }

    @Test
    fun `home app created, profile requested, profile launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = HomeAppDeeplinkContract.buildProfileUri()
        }
        prepareActivity(HomeActivity::class.java)
        launchActivity()
        sendIntent(intent)

        verify(routerSpy, times(1))?.openProfile()

        destroyActivity()
    }

    @Test
    fun `home app not launched, broken search url requested, search not opened`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = Uri.parse(TEST_SEARCH_BROKEN_URI)
        }
        prepareActivity(HomeActivity::class.java, intent)
        launchActivity()

        verify(routerSpy, never())?.openSearch(anyOrNull(), anyOrNull())
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(HeadersContentFragment::class.java))
        val rootContentFragment = (rootFragment as HeadersContentFragment).getCurrentFragment()
        assertThat(rootContentFragment, instanceOf(HomeFragment::class.java))
    }

    @Test
    @Ignore("will be fixed in https://st.yandex-team.ru/TVANDROID-3485")
    fun `home app not created, search requested, search launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.SearchUriArgs(TEST_SEARCH_QUERY, null, null)
            data = HomeAppDeeplinkContract.buildSearchUri(args)
        }
        prepareActivity(HomeActivity::class.java, intent)
        launchActivity()

        verify(routerSpy, times(1))?.openSearch(eq(TEST_SEARCH_QUERY), null)
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(HeadersContentFragment::class.java))
        val rootContentFragment = (rootFragment as HeadersContentFragment).getCurrentFragment()
        assertThat(rootContentFragment, instanceOf(SearchFragment::class.java))

        destroyActivity()
    }

    @Test
    fun `home app created, search requested, search launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.SearchUriArgs(TEST_SEARCH_QUERY, null, null)
            data = HomeAppDeeplinkContract.buildSearchUri(args)
        }
        prepareActivity(HomeActivity::class.java)
        launchActivity()
        sendIntent(intent)

        verify(routerSpy, times(1))?.openSearch(eq(TEST_SEARCH_QUERY), anyOrNull())
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(HeadersContentFragment::class.java))
        val rootContentFragment = (rootFragment as HeadersContentFragment).getCurrentFragment()
        assertThat(rootContentFragment, instanceOf(SearchFragment::class.java))

        destroyActivity()
    }

    @Test
    fun `search requested with source, search launched with appropriate source`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.SearchUriArgs(TEST_SEARCH_QUERY, FROM_ALICE_DIRECT, TEST_REQUEST_ID)
            data = HomeAppDeeplinkContract.buildSearchUri(args)
        }
        prepareActivity(HomeActivity::class.java)
        launchActivity()
        sendIntent(intent)

        verify(routerSpy, times(1))?.openSearch(eq(TEST_SEARCH_QUERY), eq(DeeplinkSource(FROM_ALICE_DIRECT, TEST_REQUEST_ID)))
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(HeadersContentFragment::class.java))
        val rootContentFragment = (rootFragment as HeadersContentFragment).getCurrentFragment()
        assertThat(rootContentFragment, instanceOf(SearchFragment::class.java))

        destroyActivity()
    }

    @Test
    @Ignore("flaky test") //TODO belenkom resolve in TVANDROID-3485
    fun `home app not launched, broken browse url requested, browse not opened`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = Uri.parse(TEST_BROWSE_BROKEN_URI)
        }
        prepareActivity(HomeActivity::class.java, intent)
        launchActivity()

        verify(routerSpy, never())?.openEpisodeDetails(anyOrNull(), anyOrNull(), anyOrNull())
        verify(routerSpy, never())?.openLibraryDetails(anyOrNull(), anyOrNull())
        verify(routerSpy, never())?.openLibrarySeries(anyOrNull(), anyOrNull(), anyOrNull())

        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(HeadersContentFragment::class.java))
        val rootContentFragment = (rootFragment as HeadersContentFragment).getCurrentFragment()
        assertThat(rootContentFragment, instanceOf(HomeFragment::class.java))
    }

    @Test
    fun `home app not started, browse film requested, browse launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.BrowseUriArgs(TEST_EPISODE_ID, TEST_EPISODE_TYPE)
            data = HomeAppDeeplinkContract.buildBrowseUri(args)
        }
        prepareActivity(BrowsingActivity::class.java, intent)
        launchActivity()

        val episodeCaptor = argumentCaptor<VhEpisodeItem>()
        verify(routerSpy, times(1))?.openEpisodeDetails(episodeCaptor.capture(), anyOrNull(), anyOrNull())
        assertThat(episodeCaptor.firstValue.id, equalTo(TEST_EPISODE_ID))
        assertThat(episodeCaptor.firstValue.contentType, equalTo(TEST_EPISODE_TYPE))
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(DetailsFragment::class.java))
        assertThat(((rootFragment as DetailsFragment).viewModel as DetailsViewModel).detailsDataProvider.get(), instanceOf(EpisodeDataProvider::class.java))

        destroyActivity()
    }

    @Test
    fun `home app started, browse film requested, browse launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.BrowseUriArgs(TEST_EPISODE_ID, TEST_EPISODE_TYPE)
            data = HomeAppDeeplinkContract.buildBrowseUri(args)
        }
        prepareActivity(BrowsingActivity::class.java)
        launchActivity()
        sendIntent(intent)

        val episodeCaptor = argumentCaptor<VhEpisodeItem>()
        verify(routerSpy, times(1))?.openEpisodeDetails(episodeCaptor.capture(), anyOrNull(), anyOrNull())
        assertThat(episodeCaptor.firstValue.id, equalTo(TEST_EPISODE_ID))
        assertThat(episodeCaptor.firstValue.contentType, equalTo(TEST_EPISODE_TYPE))
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(DetailsFragment::class.java))
        assertThat(((rootFragment as DetailsFragment).viewModel as DetailsViewModel).detailsDataProvider.get(), instanceOf(EpisodeDataProvider::class.java))

        destroyActivity()
    }

    @Test
    fun `browse film requested with source, browse launched, source respected`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.BrowseUriArgs(TEST_EPISODE_ID, TEST_EPISODE_TYPE).apply {
                from = FROM_ALICE_DIRECT
            }
            data = HomeAppDeeplinkContract.buildBrowseUri(args)
        }
        prepareActivity(BrowsingActivity::class.java)
        launchActivity()
        sendIntent(intent)

        val episodeCaptor = argumentCaptor<VhEpisodeItem>()
        verify(routerSpy, times(1))?.openEpisodeDetails(episodeCaptor.capture(), anyOrNull(), eq(true))
        assertThat(episodeCaptor.firstValue.id, equalTo(TEST_EPISODE_ID))
        assertThat(episodeCaptor.firstValue.contentType, equalTo(TEST_EPISODE_TYPE))
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(DetailsFragment::class.java))
        assertThat(((rootFragment as DetailsFragment).viewModel as DetailsViewModel).detailsDataProvider.get(), instanceOf(EpisodeDataProvider::class.java))

        destroyActivity()
    }

    @Test
    fun `browse library requested, browse launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.BrowseUriArgs(TEST_LIBRARY_ID, TEST_LIBRARY_TYPE)
            data = HomeAppDeeplinkContract.buildBrowseUri(args)
        }
        prepareActivity(BrowsingActivity::class.java)
        launchActivity()
        sendIntent(intent)

        val libraryCaptor = argumentCaptor<VhLibraryItem>()
        verify(routerSpy, times(1))?.openLibraryDetails(libraryCaptor.capture(), anyOrNull())
        assertThat(libraryCaptor.firstValue.id, equalTo(TEST_LIBRARY_ID))
        assertThat(libraryCaptor.firstValue.contentType, equalTo(TEST_LIBRARY_TYPE))
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(DetailsFragment::class.java))
        assertThat(((rootFragment as DetailsFragment).viewModel as DetailsViewModel).detailsDataProvider.get(), instanceOf(LibraryDataProvider::class.java))

        destroyActivity()
    }

    @Test
    fun `browse requested with onto id, browse launched with appropriate handling`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.BrowseUriArgs(TEST_EPISODE_ID, TEST_EPISODE_TYPE).apply {
                ontoId = TEST_ONTO_ID
            }
            data = HomeAppDeeplinkContract.buildBrowseUri(args)
        }
        prepareActivity(BrowsingActivity::class.java)
        launchActivity()
        sendIntent(intent)

        val episodeCaptor = argumentCaptor<VhEpisodeItem>()
        verify(routerSpy, times(1))?.openEpisodeDetails(episodeCaptor.capture(), anyOrNull(), anyOrNull())
        assertThat(episodeCaptor.firstValue.id, equalTo(TEST_EPISODE_ID))
        assertThat(episodeCaptor.firstValue.contentType, equalTo(TEST_EPISODE_TYPE))
        assertThat(episodeCaptor.firstValue.ontoId, equalTo(TEST_ONTO_ID))
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(DetailsFragment::class.java))
        assertThat(((rootFragment as DetailsFragment).viewModel as DetailsViewModel).detailsDataProvider.get(), instanceOf(EpisodeDataProvider::class.java))

        destroyActivity()
    }

    @Test
    fun `browse season by id requested, browse launched`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.BrowseSeasonUriArgs(TEST_LIBRARY_ID, TEST_LIBRARY_TYPE).apply {
                seasonId = TEST_SEASON_ID
            }
            data = HomeAppDeeplinkContract.buildBrowseSeasonUri(args)
        }
        prepareActivity(BrowsingActivity::class.java)
        launchActivity()
        sendIntent(intent)

        val libraryCaptor = argumentCaptor<VhLibraryItem>()
        verify(routerSpy, times(1))?.openLibrarySeries(libraryCaptor.capture(), eq(TEST_SEASON_ID), anyOrNull())
        assertThat(libraryCaptor.firstValue.id, equalTo(TEST_LIBRARY_ID))
        assertThat(libraryCaptor.firstValue.contentType, equalTo(TEST_LIBRARY_TYPE))
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(SeriesFragment::class.java))

        destroyActivity()
    }

    @Test
    fun `browse season by number requested, library details opened`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.BrowseSeasonUriArgs(TEST_LIBRARY_ID, TEST_LIBRARY_TYPE).apply {
                seasonNumber = TEST_SEASON_NUMBER
            }
            data = HomeAppDeeplinkContract.buildBrowseSeasonUri(args)
        }
        prepareActivity(BrowsingActivity::class.java)
        launchActivity()
        sendIntent(intent)

        val libraryCaptor = argumentCaptor<VhLibraryItem>()
        verify(routerSpy, times(1))?.openLibraryDetails(libraryCaptor.capture(), anyOrNull())
        assertThat(libraryCaptor.firstValue.id, equalTo(TEST_LIBRARY_ID))
        assertThat(libraryCaptor.firstValue.contentType, equalTo(TEST_LIBRARY_TYPE))
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(DetailsFragment::class.java))
        assertThat(((rootFragment as DetailsFragment).viewModel as DetailsViewModel).detailsDataProvider.get(), instanceOf(LibraryDataProvider::class.java))

        destroyActivity()
    }

    @Test
    fun `home app not launched, broken open url requested, open url not opened`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = Uri.parse(TEST_OPEN_URL_BROKEN_URI)
        }
        prepareActivity(HomeActivity::class.java, intent)
        launchActivity()

        verify(routerSpy, never())?.openUrl(anyOrNull())
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(HeadersContentFragment::class.java))
        val rootContentFragment = (rootFragment as HeadersContentFragment).getCurrentFragment()
        assertThat(rootContentFragment, instanceOf(HomeFragment::class.java))

        destroyActivity()
    }

    @Test
    fun `open custom url, web view activity started`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            val args = HomeAppDeeplinkContract.OpenUrlUriArgs(TEST_URL)
            data = HomeAppDeeplinkContract.buildOpenUrlUri(args)
        }
        prepareActivity(WebViewActivity::class.java)
        launchActivity()
        sendIntent(intent)

        verify(routerSpy)?.openUrl(TEST_URL)
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(WebViewFragment::class.java))

        destroyActivity()
    }

    @Test
    fun `home app launched, open category by name requested, category opened`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = HomeAppDeeplinkContract.buildCategoryUri(TEST_REMOTE_CATEGORY.title)
        }
        prepareActivity(HomeActivity::class.java)
        launchActivity()
        sendIntent(intent)

        verify(routerSpy, times(1))?.openCategoryFragmentByName(eq(TEST_REMOTE_CATEGORY.title))
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(HeadersContentFragment::class.java))
        val rootContentFragment = (rootFragment as HeadersContentFragment).getCurrentFragment()
        assertThat(rootContentFragment, instanceOf(CategoryFragment::class.java))

        destroyActivity()
    }

    @Test
    fun `home app launched, open category by id requested, category opened`() {
        val intent = Intent().apply {
            action = Intent.ACTION_VIEW
            data = HomeAppDeeplinkContract.buildCategoryByIdUri(TEST_REMOTE_CATEGORY.categoryId)
        }
        prepareActivity(HomeActivity::class.java)
        launchActivity()
        sendIntent(intent)

        verify(routerSpy, times(1))?.openCategoryFragmentById(eq(TEST_REMOTE_CATEGORY.categoryId))
        val rootFragment = routerSpy?.getCurrentFragment()
        assertThat(rootFragment, instanceOf(HeadersContentFragment::class.java))
        val rootContentFragment = (rootFragment as HeadersContentFragment).getCurrentFragment()
        assertThat(rootContentFragment, instanceOf(CategoryFragment::class.java))

        destroyActivity()
    }
}
