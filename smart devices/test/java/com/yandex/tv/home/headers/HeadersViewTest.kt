package com.yandex.tv.home.headers

import android.os.Build
import android.view.View
import android.widget.ImageView
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.common.ui.views.HeaderButtonView
import com.yandex.tv.home.contract.HomeAppContractTestApp
import com.yandex.tv.home.contract.deeplinkTestModule
import com.yandex.tv.home.di.homeAppModule
import com.yandex.tv.home.ui.headers.ProfileHeaderButtonContainer
import com.yandex.tv.home.ui.headers.SearchFocusForHeaders
import com.yandex.tv.home.utils.commonTestModule
import org.hamcrest.MatcherAssert
import org.hamcrest.Matchers
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.koin.android.ext.koin.androidContext
import org.koin.core.context.startKoin
import org.koin.core.context.stopKoin
import org.koin.test.KoinTest
import org.mockito.Mockito
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], application = HomeAppContractTestApp::class)
class HeadersViewTest : KoinTest {

    private val search = SearchFocusForHeaders()
    private var direction: Int = 0
    private var marketVisibility: Int = 0
    private val alice = Mockito.mock(ImageView::class.java)
    private val profile = Mockito.mock(ProfileHeaderButtonContainer::class.java)
    private val settings = Mockito.mock(HeaderButtonView::class.java)
    private val market = Mockito.mock(HeaderButtonView::class.java)

    @Before
    fun setUp() {
        startKoin {
            androidContext(ApplicationProvider.getApplicationContext())
            modules(listOf(homeAppModule, commonTestModule, deeplinkTestModule))
        }
    }

    @After
    fun clear() {
        stopKoin()
    }

    @Test
    fun `searchFocus up to null for header buttons test`() {
        direction = View.FOCUS_UP
        MatcherAssert.assertThat(
            search.searchFocusForHeadersButtons(direction, marketVisibility, alice, profile, settings, market) { null },
            Matchers.equalTo(null)
        )
    }

    @Test
    fun `searchFocus down to null for header buttons test`() {
        direction = View.FOCUS_DOWN
        MatcherAssert.assertThat(
            search.searchFocusForHeadersButtons(direction, marketVisibility, alice, profile, settings, market) { null },
            Matchers.equalTo(null)
        )
    }

    @Test
    fun `searchFocus right from alice to profile for header buttons test`() {
        direction = View.FOCUS_RIGHT
        whenever(alice.isFocused).doReturn(true)
        MatcherAssert.assertThat(
            search.searchFocusForHeadersButtons(direction, marketVisibility, alice, profile, settings, market) { null },
            Matchers.equalTo(profile)
        )
    }

    @Test
    fun `searchFocus right from profile to market for header buttons test`() {
        marketVisibility = View.VISIBLE
        direction = View.FOCUS_RIGHT
        whenever(alice.isFocused).doReturn(false)
        whenever(profile.isFocused).doReturn(true)
        MatcherAssert.assertThat(
            search.searchFocusForHeadersButtons(direction, marketVisibility, alice, profile, settings, market) { null },
            Matchers.equalTo(market)
        )
    }

    @Test
    fun `searchFocus right from market to settings for header buttons test`() {
        marketVisibility = View.VISIBLE
        direction = View.FOCUS_RIGHT
        whenever(alice.isFocused).doReturn(false)
        whenever(profile.isFocused).doReturn(false)
        whenever(market.isFocused).doReturn(true)
        MatcherAssert.assertThat(
            search.searchFocusForHeadersButtons(direction, marketVisibility, alice, profile, settings, market) { null },
            Matchers.equalTo(settings)
        )
    }

    @Test
    fun `searchFocus left from settings to market for header buttons test`() {
        marketVisibility = View.VISIBLE
        direction = View.FOCUS_LEFT
        whenever(settings.isFocused).doReturn(true)
        MatcherAssert.assertThat(
            search.searchFocusForHeadersButtons(direction, marketVisibility, alice, profile, settings, market) { null },
            Matchers.equalTo(market)
        )
    }

    @Test
    fun `searchFocus left from market to profile for header buttons test`() {
        marketVisibility = View.VISIBLE
        direction = View.FOCUS_LEFT
        whenever(settings.isFocused).doReturn(false)
        whenever(market.isFocused).doReturn(true)
        MatcherAssert.assertThat(
            search.searchFocusForHeadersButtons(direction, marketVisibility, alice, profile, settings, market) { null },
            Matchers.equalTo(profile)
        )
    }

    @Test
    fun `searchFocus left from profile to alice for header buttons test`() {
        direction = View.FOCUS_LEFT
        whenever(settings.isFocused).doReturn(false)
        whenever(market.isFocused).doReturn(false)
        whenever(profile.isFocused).doReturn(true)
        MatcherAssert.assertThat(
            search.searchFocusForHeadersButtons(direction, marketVisibility, alice, profile, settings, market) { null },
            Matchers.equalTo(alice)
        )
    }

    @Test
    fun `searchFocus right from profile to settings for header buttons test`() {
        marketVisibility = View.GONE
        direction = View.FOCUS_RIGHT
        whenever(alice.isFocused).doReturn(false)
        whenever(profile.isFocused).doReturn(true)
        MatcherAssert.assertThat(
            search.searchFocusForHeadersButtons(direction, marketVisibility, alice, profile, settings, market) { null },
            Matchers.equalTo(settings)
        )
    }

    @Test
    fun `searchFocus left from settings to profile for header buttons test`() {
        marketVisibility = View.GONE
        direction = View.FOCUS_LEFT
        whenever(settings.isFocused).doReturn(true)
        MatcherAssert.assertThat(
            search.searchFocusForHeadersButtons(direction, marketVisibility, alice, profile, settings, market) { null },
            Matchers.equalTo(profile)
        )
    }
}