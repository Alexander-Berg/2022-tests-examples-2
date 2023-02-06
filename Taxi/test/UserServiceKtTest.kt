import com.google.protobuf.Empty
import io.grpc.Status
import io.grpc.StatusException
import io.grpc.stub.StreamObserver
import io.mockk.MockKAnnotations
import io.mockk.clearAllMocks
import io.mockk.coEvery
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.justRun
import io.mockk.mockk
import io.mockk.mockkConstructor
import io.mockk.mockkObject
import io.mockk.verify
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.Config
import ru.yandex.taxi.crm.masshire.search.UserCredentials
import ru.yandex.taxi.crm.masshire.search.UserService
import ru.yandex.taxi.crm.masshire.search.db.TokenInfo
import ru.yandex.taxi.crm.masshire.search.db.TokenInfoDAO
import ru.yandex.taxi.crm.masshire.search.jobsite.JobSiteAdapter
import ru.yandex.taxi.proto.crm.masshire.ApplicationSubsystemStatus
import ru.yandex.taxi.proto.crm.masshire.ApplicationSubsystemStatus.AmoCrm
import ru.yandex.taxi.proto.crm.masshire.ApplicationSubsystemStatus.AmoCrm.Pipeline
import ru.yandex.taxi.proto.crm.masshire.GetCurrentUserResponse
import ru.yandex.taxi.proto.crm.masshire.JobSite
import ru.yandex.taxi.proto.crm.masshire.JobSiteStatus
import ru.yandex.taxi.proto.crm.masshire.LoginToJobSiteRequest
import ru.yandex.taxi.proto.crm.masshire.LogoutFromJobSiteRequest

internal fun <R> StreamObserver<R>.verifyError(expected: Status, block: () -> Unit) {
    block()
    verify { onError(match { (it as? StatusException)?.status?.code == expected.code }) }
}

internal class UserServiceKtTest {
    private val adapter =
        mockk<JobSiteAdapter>(relaxed = true) {
            every { jobSite } returns JobSite.JOB_SITE_SUPER_JOB
        }
    private val userService = UserService(hashMapOf(adapter.jobSite to adapter))
    private val credentials = UserCredentials(userTicket = "", userUid = "11")

    @BeforeEach
    fun setup() {
        mockkObject(UserCredentials)
        every { UserCredentials.get() } returns credentials

        mockkObject(Config)
        every { Config.amoCrmPipelines } returns listOf()

        mockkConstructor(TokenInfoDAO::class)
    }

    @AfterEach fun teardown() = clearAllMocks()

    @Nested
    inner class GetCurrentUserTest {
        @MockK(relaxUnitFun = true)
        private lateinit var responseObserver: StreamObserver<GetCurrentUserResponse>

        @BeforeEach
        private fun setup() {
            MockKAnnotations.init(this)
            every { anyConstructed<TokenInfoDAO>().exists(any(), any()) } returns true
        }

        @Test
        fun `for logged in user returns isLoggedIn`() {
            every { anyConstructed<TokenInfoDAO>().exists(any(), any()) } returns true

            userService.getCurrentUser(Empty.getDefaultInstance(), responseObserver)

            verify(exactly = 0) { responseObserver.onError(any()) }
            verify(exactly = 1) {
                responseObserver.onNext(
                    GetCurrentUserResponse.newBuilder()
                        .addJobSiteStatuses(
                            JobSiteStatus.newBuilder()
                                .setJobSite(JobSite.JOB_SITE_SUPER_JOB)
                                .setIsLoggedIn(true)
                                .build()
                        )
                        .build()
                )
            }
        }

        @Test
        fun `for not logged in user returns authorizationUrl`() {
            val authUrl = "https://superjob.ru/authorize"
            every { adapter.getAuthorizationUrl() } returns authUrl
            every { anyConstructed<TokenInfoDAO>().exists(any(), any()) } returns false

            userService.getCurrentUser(Empty.getDefaultInstance(), responseObserver)

            verify(exactly = 0) { responseObserver.onError(any()) }
            verify(exactly = 1) {
                responseObserver.onNext(
                    GetCurrentUserResponse.newBuilder()
                        .addJobSiteStatuses(
                            JobSiteStatus.newBuilder()
                                .setJobSite(JobSite.JOB_SITE_SUPER_JOB)
                                .setAuthorizationUrl(authUrl)
                                .build()
                        )
                        .build()
                )
            }
        }

        @Test
        fun `given empty amocrm pipelines won't fill application_subsystem_statuses`() {
            every { Config.amoCrmPipelines } returns listOf()

            userService.getCurrentUser(Empty.getDefaultInstance(), responseObserver)

            verify(exactly = 0) { responseObserver.onError(any()) }
            verify(exactly = 1) {
                responseObserver.onNext(match { it.applicationSubsystemStatusesList.isEmpty() })
            }
        }

        @Test
        fun `given amocrm pipelines returns them`() {
            val pipeline = Pipeline.newBuilder().setId("1234").setName("Taxi").build()
            every { Config.amoCrmPipelines } returns listOf(pipeline)

            userService.getCurrentUser(Empty.getDefaultInstance(), responseObserver)

            verify(exactly = 0) { responseObserver.onError(any()) }
            verify(exactly = 1) {
                responseObserver.onNext(
                    match {
                        it.applicationSubsystemStatusesList ==
                            listOf(
                                ApplicationSubsystemStatus.newBuilder()
                                    .setAmoCrm(AmoCrm.newBuilder().addPipelines(pipeline))
                                    .build()
                            )
                    }
                )
            }
        }
    }

    @Nested
    inner class LoginToJobSiteTest {
        @MockK(relaxUnitFun = true) private lateinit var responseObserver: StreamObserver<Empty>

        @BeforeEach
        private fun setup() {
            MockKAnnotations.init(this)
        }

        @Test
        fun `given unknown jobSite returns invalid argument error`() {
            val request =
                LoginToJobSiteRequest.newBuilder().setJobSite(JobSite.JOB_SITE_UNSPECIFIED).build()

            responseObserver.verifyError(Status.INVALID_ARGUMENT) {
                userService.loginToJobSite(request, responseObserver)
            }
        }

        @Test
        fun `when adapter can't fetch access token returns internal error`() {
            coEvery { adapter.requestAccessToken("code") } returns null
            val request =
                LoginToJobSiteRequest.newBuilder()
                    .setJobSite(adapter.jobSite)
                    .setAuthorizationCode("code")
                    .build()

            responseObserver.verifyError(Status.INTERNAL) {
                userService.loginToJobSite(request, responseObserver)
            }
        }

        @Test
        fun `when adapter throws returns internal error`() {
            coEvery { adapter.requestAccessToken("code") } throws Throwable()
            val request =
                LoginToJobSiteRequest.newBuilder()
                    .setJobSite(adapter.jobSite)
                    .setAuthorizationCode("code")
                    .build()

            responseObserver.verifyError(Status.INTERNAL) {
                userService.loginToJobSite(request, responseObserver)
            }
        }

        @Test
        fun `when access token is fetched saves it to db`() {
            val request =
                LoginToJobSiteRequest.newBuilder()
                    .setJobSite(adapter.jobSite)
                    .setAuthorizationCode("code")
                    .build()

            val tokenInfo =
                TokenInfo(
                    accessToken = "access_token",
                    refreshToken = "refresh_token",
                    expiresIn = 100000
                )
            coEvery { adapter.requestAccessToken("code") } returns tokenInfo
            justRun { anyConstructed<TokenInfoDAO>().upsert(any(), any(), any()) }

            userService.loginToJobSite(request, responseObserver)

            verify(exactly = 0) { responseObserver.onError(any()) }
            verify(exactly = 1) {
                anyConstructed<TokenInfoDAO>()
                    .upsert(credentials.userUid, JobSite.JOB_SITE_SUPER_JOB, tokenInfo)
            }
        }
    }

    @Nested
    inner class LogoutFromJobSiteTest {
        @MockK(relaxUnitFun = true) private lateinit var responseObserver: StreamObserver<Empty>

        @BeforeEach
        private fun setup() {
            MockKAnnotations.init(this)
        }

        @Test
        fun `given unknown jobSite returns invalid argument error`() {
            val request =
                LogoutFromJobSiteRequest.newBuilder()
                    .setJobSite(JobSite.JOB_SITE_UNSPECIFIED)
                    .build()

            responseObserver.verifyError(Status.INVALID_ARGUMENT) {
                userService.logoutFromJobSite(request, responseObserver)
            }
        }

        @Test
        fun `on logout deletes user token from db`() {
            val request = LogoutFromJobSiteRequest.newBuilder().setJobSite(adapter.jobSite).build()

            justRun { anyConstructed<TokenInfoDAO>().remove(any(), any()) }

            userService.logoutFromJobSite(request, responseObserver)

            verify(exactly = 0) { responseObserver.onError(any()) }
            verify(exactly = 1) {
                anyConstructed<TokenInfoDAO>()
                    .remove(credentials.userUid, JobSite.JOB_SITE_SUPER_JOB)
            }
        }
    }
}
