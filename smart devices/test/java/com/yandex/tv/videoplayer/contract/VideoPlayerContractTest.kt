package com.yandex.tv.videoplayer.contract

import android.content.Intent
import android.os.Build
import android.os.Looper.getMainLooper
import org.mockito.kotlin.any
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.argThat
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.doAnswer
import org.mockito.kotlin.doNothing
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.spy
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.verifyBlocking
import com.yandex.tv.common.contract.videoplayer.VideoPlayerContract
import com.yandex.tv.common.contract.videoplayer.VideoPlayerContract.KEY_EXTRA_APPHOST_REQUEST_ID
import com.yandex.tv.common.contract.videoplayer.VideoPlayerContract.KEY_EXTRA_CONTENT_ID
import com.yandex.tv.common.contract.videoplayer.VideoPlayerContract.KEY_EXTRA_ONTO_ID
import com.yandex.tv.common.contract.videoplayer.VideoPlayerContract.KEY_EXTRA_PLAYLIST_CONTENT_IDS
import com.yandex.tv.common.contract.videoplayer.VideoPlayerContract.KEY_EXTRA_PLAYLIST_TITLES
import com.yandex.tv.common.contract.videoplayer.VideoPlayerContract.KEY_EXTRA_POSITION_SECONDS
import com.yandex.tv.common.contract.videoplayer.VideoPlayerContract.KEY_EXTRA_REQUEST_ID
import com.yandex.tv.common.contract.videoplayer.VideoPlayerContract.KEY_EXTRA_VIDEO_THUMBNAIL_URL
import com.yandex.tv.common.contract.videoplayer.VideoPlayerContract.PLAYER_ACTIVITY
import com.yandex.tv.common.utility.test.EmptyMetricaServiceSdk2
import com.yandex.tv.common.utility.test.EmptyPolicyManagerServiceSdk2
import com.yandex.tv.common.utility.test.injectActivitySpy
import com.yandex.tv.services.metrica.MetricaServiceSdk2
import com.yandex.tv.services.policymanagerservice.PolicyManagerServiceSdk2
import com.yandex.tv.videoplayer.PlayerActivity
import com.yandex.tv.videoplayer.PlayerContract
import com.yandex.tv.videoplayer.PlayerParams
import com.yandex.tv.videoplayer.common.model.AdditionalParams
import com.yandex.tv.videoplayer.common.model.VhVideo
import com.yandex.tv.videoplayer.common.utils.TextUtils
import com.yandex.tv.videoplayer.model.PlayerModel
import com.yandex.tv.videoplayer.presenter.PlayerPresenter
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.test.runBlockingTest
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.instanceOf
import org.hamcrest.MatcherAssert.assertThat
import org.junit.After
import org.junit.AfterClass
import org.junit.Assert.assertThrows
import org.junit.BeforeClass
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.MockedStatic
import org.mockito.Mockito
import org.mockito.Mockito.mockStatic
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.android.controller.ActivityController
import org.robolectric.annotation.Config
import java.lang.IllegalArgumentException
import java.util.concurrent.TimeUnit

private const val TEST_RESTRICTION_AGE = 0
private val TEST_RESTRICTION_AGE_TEXT: String? = TextUtils.getRestrictionAgeText(TEST_RESTRICTION_AGE.toString())
private const val TEST_DIRECT_URL = "https://strm.yandex.ru/vh-kp-converted/ott-content/395274521-4609c3cb682281eaad7dfafea7d7ceca/master.m3u8"
private const val TEST_CONTENT_ID = "47af493eb5604eb68ecf199113ad7756"
private const val TEST_START_POSITION = 42L
private const val TEST_THUMBNAIL_URL = "http://avatars.mds.yandex.net/get-ott/2385704/2a00000176523ea54f43c0008ba1cc6dd10e/orig"
private const val TEST_REQ_ID = "test_req_id"
private const val TEST_ONTO_ID = "test_onto_id"
private const val TEST_APPHOST_REQ_ID = "test_apphost_req_id"

private val TEST_PLAYLIST_IDS = arrayOf("playlist_id_1", "playlist_id_2", "playlist_id_3")
private val TEST_PLAYLIST_TITLES = arrayOf("playlist_title_1", "playlist_title_2", "playlist_title_3")

@ExperimentalCoroutinesApi
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], application = VideoPlayerContractTestApp::class)
class VideoPlayerContractTest {

    private var controller: ActivityController<PlayerActivity>? = null
    private var activitySpy: PlayerActivity? = null
    private var playerPresenterSpy: PlayerContract.Presenter? = null
    private var playerModelSpy: PlayerContract.Model? = null

    private fun prepareActivity(intent: Intent) {
        controller = Robolectric.buildActivity(PlayerActivity::class.java, intent)
            .also { controller ->
                activitySpy = spy(controller.get())
                    .also { activity ->
                        injectActivitySpy(controller, activity)
                        injectPlayerPresenterAndModelSpy(activity)
                    }
            }
    }

    private fun injectPlayerPresenterAndModelSpy(playerActivity: PlayerActivity) {
        doAnswer {
            playerPresenterSpy = spy<PlayerPresenter>(it.getArgument<PlayerPresenter>(0))
                .also { presenterSpy ->
                    playerModelSpy = spy(EmptyPlayerModel()).also { playerModel->
                        doReturn(playerModel).`when`(presenterSpy).playerModel
                        doNothing().`when`(presenterSpy).onPlayerOpened(anyOrNull(), anyOrNull(), anyOrNull())
                    }
                    playerActivity.setPlayerPresenter(presenterSpy)
                }
        }.`when`(playerActivity).setPlayerPresenter(argThat { !Mockito.mockingDetails(this).isSpy })
    }

    private fun launchActivity() {
        controller?.apply {
            create()
            start()
            resume()
            visible()
        }
        shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
    }

    private fun destroyActivity() {
        controller?.apply {
            pause()
            stop()
            destroy()
        }
        shadowOf(getMainLooper()).idleFor(10, TimeUnit.SECONDS)
    }

    private fun createPlayerIntent(): Intent {
        return Intent().apply { component = PLAYER_ACTIVITY }
    }

    @After
    fun tearDown() {
        playerModelSpy = null
        playerPresenterSpy = null
        activitySpy = null
        controller = null
    }

    @Test
    fun `launch empty intent, launch failed`() {
        runBlockingTest {
            val intent = createPlayerIntent()
            prepareActivity(intent)
            assertThrows(IllegalArgumentException::class.java) {
                launchActivity()
            }
        }
    }

    @Test
    fun `launch with direct uri, launch successful`() {
        runBlockingTest {
            val intent = createPlayerIntent().apply {
                data = VideoPlayerContract.Deeplinks.videoUrl(TEST_DIRECT_URL, 0)
            }
            prepareActivity(intent)
            launchActivity()

            val activity = requireNotNull(activitySpy)
            val playerPresenter = requireNotNull(playerPresenterSpy)

            val launchParams = activity.activityComponent.launchParams
            assertThat(launchParams, instanceOf(PlayerParams.Local::class.java))

            assertThat(playerPresenter, instanceOf(PlayerPresenter::class.java))
            val videoIdCaptor = argumentCaptor<String>()
            verify(playerPresenter as PlayerPresenter, times(1))
                .playLocalVideo(videoIdCaptor.capture(), videoIdCaptor.capture())
            assertThat(videoIdCaptor.firstValue, equalTo(TEST_DIRECT_URL))
            assertThat(videoIdCaptor.secondValue, equalTo(TEST_RESTRICTION_AGE_TEXT))

            destroyActivity()
        }
    }

    @Test
    fun `launch with vh uri, launch successful`() {
        runBlockingTest {
            val intent = createPlayerIntent().apply {
                data = VideoPlayerContract.Deeplinks.vhVideoUri(TEST_CONTENT_ID)
            }
            prepareActivity(intent)
            launchActivity()

            val activity = requireNotNull(activitySpy)
            val playerPresenter = requireNotNull(playerPresenterSpy)

            val launchParams = activity.activityComponent.launchParams
            assertThat(launchParams, instanceOf(PlayerParams.Yandex::class.java))

            val videoIdCaptor = argumentCaptor<String>()
            verify(playerPresenter, times(1)).play(videoIdCaptor.capture(), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull())
            assertThat(videoIdCaptor.firstValue, equalTo(TEST_CONTENT_ID))

            destroyActivity()
        }
    }

    @Test
    fun `launch with content id, launch successful`() {
        runBlockingTest {
            val intent = createPlayerIntent().apply {
                putExtra(KEY_EXTRA_CONTENT_ID, TEST_CONTENT_ID)
            }
            prepareActivity(intent)
            launchActivity()

            val activity = requireNotNull(activitySpy)
            val playerPresenter = requireNotNull(playerPresenterSpy)

            val launchParams = activity.activityComponent.launchParams
            assertThat(launchParams, instanceOf(PlayerParams.Yandex::class.java))

            val videoIdCaptor = argumentCaptor<String>()
            verify(playerPresenter, times(1)).play(videoIdCaptor.capture(), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull())
            assertThat(videoIdCaptor.firstValue, equalTo(TEST_CONTENT_ID))

            destroyActivity()
        }

    }

    @Test
    fun `launch with content id and start position, launch successful, position set`() {
        runBlockingTest {
            val intent = createPlayerIntent().apply {
                putExtra(KEY_EXTRA_CONTENT_ID, TEST_CONTENT_ID)
                putExtra(KEY_EXTRA_POSITION_SECONDS, TEST_START_POSITION)
            }
            prepareActivity(intent)
            launchActivity()

            val playerPresenter = requireNotNull(playerPresenterSpy)

            val startPositionCaptor = argumentCaptor<Long>()
            verify(playerPresenter, times(1)).play(any(), startPositionCaptor.capture(), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull())
            assertThat(startPositionCaptor.firstValue, equalTo(TEST_START_POSITION))

            destroyActivity()
        }

    }

    @Test
    fun `launch with content id and thumbnail, launch successful, thumbnail set`() {
        runBlockingTest {
            val intent = createPlayerIntent().apply {
                putExtra(KEY_EXTRA_CONTENT_ID, TEST_CONTENT_ID)
                putExtra(KEY_EXTRA_VIDEO_THUMBNAIL_URL, TEST_THUMBNAIL_URL)
            }
            prepareActivity(intent)
            launchActivity()

            val playerPresenter = requireNotNull(playerPresenterSpy)

            val thumbnailUrlCaptor = argumentCaptor<String>()
            verify(playerPresenter, times(1)).play(any(), anyOrNull(), thumbnailUrlCaptor.capture(), anyOrNull(), anyOrNull(), anyOrNull())
            assertThat(thumbnailUrlCaptor.firstValue, equalTo(TEST_THUMBNAIL_URL))

            destroyActivity()
        }
    }

    @Test
    fun `launch with content id and onto_id, launch successful, onto_id set`() {
        runBlockingTest {
            val intent = createPlayerIntent().apply {
                putExtra(KEY_EXTRA_CONTENT_ID, TEST_CONTENT_ID)
                putExtra(KEY_EXTRA_ONTO_ID, TEST_ONTO_ID)
            }
            prepareActivity(intent)
            launchActivity()

            val playerPresenter = requireNotNull(playerPresenterSpy)

            val ontoIdCaptor = argumentCaptor<String>()
            verify(playerPresenter, times(1)).play(any(), anyOrNull(), anyOrNull(), ontoIdCaptor.capture(), anyOrNull(), anyOrNull())
            assertThat(ontoIdCaptor.firstValue, equalTo(TEST_ONTO_ID))

            destroyActivity()
        }
    }

    @Test
    fun `launch with content id and reqids, launch successful, reqids set`() {
        runBlockingTest {
            val intent = createPlayerIntent().apply {
                putExtra(KEY_EXTRA_CONTENT_ID, TEST_CONTENT_ID)
                putExtra(KEY_EXTRA_REQUEST_ID, TEST_REQ_ID)
                putExtra(KEY_EXTRA_APPHOST_REQUEST_ID, TEST_APPHOST_REQ_ID)
            }
            prepareActivity(intent)
            launchActivity()

            val playerPresenter = requireNotNull(playerPresenterSpy)

            val additionalParamsCaptor = argumentCaptor<AdditionalParams>()
            verify(playerPresenter, times(1)).play(any(), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull(), additionalParamsCaptor.capture())
            val reqId = additionalParamsCaptor.firstValue.getIfValid()?.get(AdditionalParams.KEY_REQ_ID)
            val apphostReqId = additionalParamsCaptor.firstValue.getIfValid()?.get(AdditionalParams.KEY_APP_HOST_REQ_ID)
            assertThat(reqId, instanceOf(String::class.java))
            assertThat(reqId as String, equalTo(TEST_REQ_ID))
            assertThat(apphostReqId, instanceOf(String::class.java))
            assertThat(apphostReqId as String, equalTo(TEST_APPHOST_REQ_ID))

            destroyActivity()
        }
    }

    @Test
    fun `launch with playlist, launch successful, playlist set`() {
        runBlockingTest {
            val intent = createPlayerIntent().apply {
                putExtra(KEY_EXTRA_CONTENT_ID, TEST_CONTENT_ID)
                putExtra(KEY_EXTRA_PLAYLIST_CONTENT_IDS, TEST_PLAYLIST_IDS)
                putExtra(KEY_EXTRA_PLAYLIST_TITLES, TEST_PLAYLIST_TITLES)
            }
            prepareActivity(intent)
            launchActivity()

            val activity = requireNotNull(activitySpy)
            val playerPresenter = requireNotNull(playerPresenterSpy)
            val playerModel = requireNotNull(playerModelSpy)

            val launchParams = activity.activityComponent.launchParams
            assertThat(launchParams, instanceOf(PlayerParams.Yandex::class.java))

            val yandexLaunchParams = launchParams as PlayerParams.Yandex
            yandexLaunchParams.playlist.forEachIndexed { i, video ->
                assertThat(video.contentId, equalTo(TEST_PLAYLIST_IDS[i]))
                assertThat(video.title, equalTo(TEST_PLAYLIST_TITLES[i]))
            }

            verify(playerPresenter, times(1)).play(any(), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull())
            val playlistCaptor = argumentCaptor<List<VhVideo>>()
            verifyBlocking(playerModel, times(1)) { setNextVideos(playlistCaptor.capture()) }
            playlistCaptor.firstValue.forEachIndexed { i, video ->
                assertThat(video.contentId, equalTo(TEST_PLAYLIST_IDS[i]))
                assertThat(video.title, equalTo(TEST_PLAYLIST_TITLES[i]))
            }

            destroyActivity()
        }
    }

    companion object {

        private var mockedPolicyManagerServiceSdk: MockedStatic<PolicyManagerServiceSdk2.Factory>? = null
        private var mockedMetricaServiceSdk: MockedStatic<MetricaServiceSdk2.Factory>? = null

        @BeforeClass
        @JvmStatic
        fun mockSdk() {
            mockedMetricaServiceSdk = mockStatic(MetricaServiceSdk2.Factory::class.java).apply {
                `when`<MetricaServiceSdk2> { MetricaServiceSdk2.Factory.create(any()) }.thenReturn(EmptyMetricaServiceSdk2())
            }
            mockedPolicyManagerServiceSdk = mockStatic(PolicyManagerServiceSdk2.Factory::class.java).apply {
                `when`<PolicyManagerServiceSdk2> { PolicyManagerServiceSdk2.Factory.create(any()) }.thenReturn(EmptyPolicyManagerServiceSdk2())
            }
        }

        @AfterClass
        @JvmStatic
        fun unmockSdk() {
            mockedPolicyManagerServiceSdk?.close()
            mockedMetricaServiceSdk?.close()
        }
    }
}
