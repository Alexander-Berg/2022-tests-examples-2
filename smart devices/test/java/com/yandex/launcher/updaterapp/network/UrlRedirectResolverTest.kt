package com.yandex.launcher.updaterapp.network

import com.yandex.launcher.updaterapp.BaseRobolectricTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.hamcrest.Matchers.`is`
import org.hamcrest.MatcherAssert.assertThat
import org.junit.After
import org.junit.Before
import org.junit.Test
import java.net.HttpURLConnection.HTTP_MOVED_TEMP
import java.net.HttpURLConnection.HTTP_OK

class UrlRedirectResolverTest : BaseRobolectricTest() {

    private lateinit var mockWebServer: MockWebServer

    @Before
    @Throws(Exception::class)
    override fun setUp() {
        super.setUp()
        mockWebServer = MockWebServer()
    }

    @After
    @Throws(Exception::class)
    fun tearDown() {
        mockWebServer.shutdown()
    }

    private fun getWebServer(): MockWebServer {
        return mockWebServer
    }

    @Test
    fun shouldResolveUrlSuccessfully() {
        val expectedReferrer = "adjust_reftag%3DcRpEBezdRtfjo%26utm_source%3DYandex%2BInstalls_test"

        getWebServer().enqueue(
            MockResponse().setResponseCode(HTTP_MOVED_TEMP)
                .setHeader(
                    "Location",
                    "https://play.google.com/store/apps/details?id=com.lingualeo.android&referrer=$expectedReferrer"
                )
        )
        getWebServer().enqueue(MockResponse().setResponseCode(HTTP_OK))
        getWebServer().start()

        val resolved = UrlRedirectResolver().findResolvedReferrer(
            updateContext.context,
            updateContext.systemInfoProvider,
            "http://" + getWebServer().hostName + ":" + getWebServer().port + "/api/v2/on_click/?" +
                "ad_id=8a058582-4840-4aa3-ba10-09f8fcddb2d5&package_name=com.lingualeo.android" +
                "&view_type=setup_wizard&offer_id=direct-test_191&impression_id=app_installer%3Asetup_wizard%3" +
                "Bwizard_recommender%3A5bbba8efa2694100be5b482c%3A1%3B1%3B2%3A0%3B0%3B0%3A0%3A2.79.0%3B2.88.0%3A2322587%3A1.0.0-RC11.dev.21" +
                "%3ARU%3BRU%3Aapps&clid=2322587&android_id=e9130c3f33c36e5e&device_id=70ace7795a842dfb3435e781f2d006e3&uuid=" +
                "92fb664c27bc9c64cc3732b456739c36&country=RU&experiment=setup_wizard&place=setup_wizard&fallback=1"
        )
        assertThat(resolved, `is`(expectedReferrer))
    }
}
