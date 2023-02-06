package ru.yandex.quasar.app.services.watchedvideoservice

import com.fasterxml.jackson.databind.ObjectMapper
import com.google.common.collect.Collections2
import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.mock
import org.mockito.kotlin.reset
import org.mockito.kotlin.verify
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.auth.AuthObservable
import ru.yandex.quasar.app.configs.ExternalConfigObservable
import ru.yandex.quasar.app.configs.StationConfig
import ru.yandex.quasar.fakes.FakeConfiguration
import ru.yandex.quasar.fakes.InMemoryDataSource
import ru.yandex.quasar.app.services.WatchedVideoService
import ru.yandex.quasar.app.utils.waiting.Bootstrap
import ru.yandex.quasar.data.DataSource
import ru.yandex.quasar.fakes.FakeExecutorService
import ru.yandex.quasar.protobuf.ModelObjects
import ru.yandex.quasar.protobuf.QuasarProto
import ru.yandex.quasar.transport.QuasarServer
import ru.yandex.quasar.core.utils.Observable

@RunWith(RobolectricTestRunner::class)
class WatchedVideoServiceTest {

    private lateinit var server: QuasarServer
    private lateinit var fakeConfiguration: FakeConfiguration
    private lateinit var service: WatchedVideoService
    private lateinit var authObservable: AuthObservable
    private lateinit var externalConfigObservable: ExternalConfigObservable
    private lateinit var bootstrapAuthObservable: Observable<AuthObservable.AuthInformation>
    private lateinit var executorExecutorService: FakeExecutorService
    private lateinit var completeVideoState: ModelObjects.CompleteVideoState
    private lateinit var watchedVideoState: ModelObjects.WatchedVideoState
    private lateinit var dataSource: DataSource<ModelObjects.CompleteVideoState>

    private val authInformation = AuthObservable.AuthInformation("auth", "xtoken", "yandexuid")
    private val authInformation2 = AuthObservable.AuthInformation("auth2", "xtoken2", "yandexuid2")

    @Before
    fun setUp() {
        fakeConfiguration = FakeConfiguration()
        fakeConfiguration.initialize("""
            {
              "videod": {
                "stateSendIntervalMs": 1
              },
              "mediad": {
                "port": 9000
              },
              "syncd": {
                "port": 9001
              },
              "aliced": {
                "port": 9002
              }
            }
            """)
    }

    fun init() {
        server = mock()
        authObservable = mock()
        externalConfigObservable = mock()
        bootstrapAuthObservable = Observable()
        executorExecutorService = FakeExecutorService()
        dataSource = InMemoryDataSource()

        val mediaItem = ModelObjects.MediaItem.newBuilder().setItemId("itemId").setPlayUri("playUri").build()
        val video = ModelObjects.Video.newBuilder().setItem(mediaItem).build()
        val progress = ModelObjects.Progress.newBuilder().setPlayed(42).setDuration(100).build()
        val videoState = ModelObjects.VideoState.newBuilder().setVideo(video).setProgress(progress).build()
        watchedVideoState = ModelObjects.WatchedVideoState.newBuilder().addVideo(videoState).build()
        val userWatchedVideoState = ModelObjects.UserWatchedVideoState.newBuilder().putUserState("medium", watchedVideoState).build()
        completeVideoState = ModelObjects.CompleteVideoState.getDefaultInstance().toBuilder()
                .putState("yandexuid", userWatchedVideoState).build()

        dataSource.store(completeVideoState)

        val authBootstrap = Bootstrap(bootstrapAuthObservable)
        service = WatchedVideoService(
            mock(),
            executorExecutorService,
            authObservable,
            externalConfigObservable,
            authBootstrap,
            dataSource,
            fakeConfiguration,
            server,
            mock(),
            mock())
    }

    private fun invokeAuthBootstrap() {
        bootstrapAuthObservable.receiveValue(mock())
    }

    private fun setUser() {
        this.invokeAuthObservable(authInformation)
    }

    private fun changeUser() {
        this.invokeAuthObservable(authInformation2)
    }

    private fun invokeAuthObservable(authInfo: AuthObservable.AuthInformation = this.authInformation) {
        argumentCaptor<Observable.Observer<AuthObservable.AuthInformation>>().apply {
            verify(authObservable).addObserver(capture())
            val authObserver = firstValue
            authObserver.update(authInfo)
        }
    }

    private fun sendAccountConfig() {
        sendAccountConfigImpl("yandexuid", false)
    }

    private fun sendAccountConfigThroughObservable() {
        sendAccountConfigImpl("yandexuid", true)
    }

    private fun sendAccountConfigImpl(yandexUid: String, useConfigObservable: Boolean) {
        if (useConfigObservable) {
            invokeExternalConfigObservable(yandexUid)
            return
        }
        val configMessage = QuasarProto.QuasarMessage.newBuilder()
            .setUserConfigUpdate(makeUserConfig(yandexUid))
            .build()
        service.handleQuasarMessage(configMessage, mock())
    }

    private fun invokeExternalConfigObservable(yandexUid: String) {
        val stationConfig = StationConfig.fromUserConfigUpdate(
            makeUserConfig(yandexUid),
            ObjectMapper(),
            fakeConfiguration
        )
        argumentCaptor<Observable.Observer<StationConfig>>().apply {
            verify(externalConfigObservable).addObserver(capture())
            val authObserver = firstValue
            authObserver.update(stationConfig)
        }
    }

    private fun makeUserConfig(yandexUid: String): ModelObjects.UserConfig {
        return ModelObjects.UserConfig.newBuilder().setPassportUid(yandexUid).setConfig(
        """
        {
            "account_config": { "contentAccess": "medium", "spotter": "alisa" },
            "system_config": {},
            "device_config": {}
        }
        """
        ).build()
    }

    @Test
    fun given_everythingIsOk_when_started_then_sendsOutState() {
        runCheck { events ->
            // Arrange
            init()
            service.start()

            // Act
            for (e in events) {
                e()
            }

            executorExecutorService.runAllJobs()

            // Assert
            argumentCaptor<QuasarProto.QuasarMessage>().apply {
                verify(server).sendToAll(capture())
                val quasarMessage = firstValue
                Assert.assertTrue(quasarMessage.hasWatchedVideo())
                Assert.assertEquals(watchedVideoState, quasarMessage.watchedVideo)
                Assert.assertEquals(completeVideoState, dataSource.loadData())
            }
            service.stop()
        }
    }

    @Test
    fun given_serviceHasAlreadyStartedForUserA_when_userChangestoUserB_then_storesAndSendsEmptyState() {
        runCheck { events ->
            // Arrange
            init()
            service.start()

            // Act
            for (e in events) {
                e()
            }

            executorExecutorService.runAllJobs()
            reset(server)

            this.changeUser()
            this.sendAccountConfigImpl("yandexuid2", true)

            // Assert
            argumentCaptor<QuasarProto.QuasarMessage>().apply {
                verify(server).sendToAll(capture())
                val quasarMessage = firstValue
                Assert.assertTrue(quasarMessage.hasWatchedVideo())
                Assert.assertEquals(
                    ModelObjects.WatchedVideoState.getDefaultInstance(),
                    quasarMessage.watchedVideo
                )
                Assert.assertEquals(
                    ModelObjects.CompleteVideoState.newBuilder().putState(
                        "yandexuid2",
                        ModelObjects.UserWatchedVideoState.getDefaultInstance()
                    ).build(), dataSource.loadData()
                )
            }

            service.stop()
        }
    }

    private fun runCheck(check: (Collection<() -> Unit>) -> Unit) {
        for (actionSet in getTestActionSets()) {
            @Suppress("UnstableApiUsage")
            Collections2.permutations(actionSet).forEach(check)
        }
    }

    private fun getTestActionSets(): List<List<() -> Unit>> {
        val legacyConfigTest = listOf(this::invokeAuthBootstrap, this::setUser, this::sendAccountConfig)
        val observableConfigTest = listOf(this::invokeAuthBootstrap, this::setUser, this::sendAccountConfigThroughObservable)
        val bothConfigTest = listOf(this::invokeAuthBootstrap, this::setUser, this::sendAccountConfig, this::sendAccountConfigThroughObservable)
        return listOf(legacyConfigTest, observableConfigTest, bothConfigTest)
    }
}
