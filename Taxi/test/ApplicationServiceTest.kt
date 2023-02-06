import io.grpc.Status
import io.grpc.stub.StreamObserver
import io.mockk.clearAllMocks
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.justRun
import io.mockk.mockk
import io.mockk.mockkConstructor
import io.mockk.mockkStatic
import io.mockk.unmockkStatic
import io.mockk.verify
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.postgresql.util.PSQLException
import ru.yandex.taxi.crm.masshire.search.ApplicationService
import ru.yandex.taxi.crm.masshire.search.amocrm.AmoCrmAdapter
import ru.yandex.taxi.crm.masshire.search.amocrm.AmoCrmUserIdProvider
import ru.yandex.taxi.crm.masshire.search.asFailure
import ru.yandex.taxi.crm.masshire.search.checkExternalId
import ru.yandex.taxi.crm.masshire.search.db.ApplicationInfoDAO
import ru.yandex.taxi.crm.masshire.search.db.PersonalInfo
import ru.yandex.taxi.crm.masshire.search.db.PersonalInfoDAO
import ru.yandex.taxi.crm.masshire.search.idempotency.getIdempotencyToken
import ru.yandex.taxi.crm.masshire.search.jobsite.JobSiteAdapter
import ru.yandex.taxi.crm.masshire.search.jobsite.JobSiteResult
import ru.yandex.taxi.proto.crm.masshire.CreateApplicationRequest
import ru.yandex.taxi.proto.crm.masshire.CreateApplicationResponse
import ru.yandex.taxi.proto.crm.masshire.JobSite
import ru.yandex.taxi.proto.crm.masshire.Resume

internal class ApplicationServiceTest {
    private val externalId = "urn:sj:resume-id-1"
    private val resume = Resume.newBuilder()
    private val jobSiteAdapter =
        mockk<JobSiteAdapter>(relaxed = true) {
            every { jobSite } returns JobSite.JOB_SITE_SUPER_JOB
        }

    private val amoAdapter = mockk<AmoCrmAdapter>()
    private val userIdProvider = mockk<AmoCrmUserIdProvider>()
    private val service =
        ApplicationService(
            hashMapOf(jobSiteAdapter.jobSite to jobSiteAdapter),
            amoAdapter,
            userIdProvider
        )

    private val responseObserver =
        mockk<StreamObserver<CreateApplicationResponse>>(relaxUnitFun = true)
    private val request = CreateApplicationRequest.newBuilder()

    @BeforeEach
    fun setup() {
        mockkStatic(::getIdempotencyToken)
        every { getIdempotencyToken() } returns "idempotency-token"

        mockkConstructor(ApplicationInfoDAO::class)
        justRun { anyConstructed<ApplicationInfoDAO>().create(any(), any()) }
        justRun { anyConstructed<ApplicationInfoDAO>().update(any(), any()) }
        justRun { anyConstructed<ApplicationInfoDAO>().remove(any()) }

        mockkConstructor(PersonalInfoDAO::class)
        every { anyConstructed<PersonalInfoDAO>().read(externalId) } returns null

        request.externalId = externalId
        request.subsystemBuilder.amoCrmBuilder.pipeline = "12345"

        coEvery { jobSiteAdapter.getResume(externalId) } returns
            JobSiteResult.Ok(Pair(resume.build(), ""))

        coEvery { amoAdapter.createApplication(any(), any(), any()) } returns
            Result.success("lead-url")

        coEvery { userIdProvider.userId() } returns Result.success(222)
    }

    @AfterEach
    fun teardown() {
        clearAllMocks()
        request.clear()
        resume.clear()
    }

    private fun createApplication() {
        service.createApplication(request.build(), responseObserver)
    }

    @Test
    fun `given no pipeline id returns invalid argument error`() {
        mockkStatic(::checkExternalId)
        request.clearSubsystem()

        responseObserver.verifyError(Status.INVALID_ARGUMENT) { createApplication() }

        verify(exactly = 0) { checkExternalId(any()) }
    }

    @Test
    fun `given invalid pipeline id returns invalid argument error`() {
        mockkStatic(::checkExternalId)
        request.subsystemBuilder.amoCrmBuilder.pipeline = "invalid-id"

        responseObserver.verifyError(Status.INVALID_ARGUMENT) { createApplication() }

        verify(exactly = 0) { checkExternalId(any()) }
    }

    @Test
    fun `when checkExternalId fails returns error`() {
        request.externalId = "invalid-resume-id"

        responseObserver.verifyError(Status.INVALID_ARGUMENT) { createApplication() }

        verify(exactly = 0) { getIdempotencyToken() }
    }

    @Test
    fun `when checkExternalId returns unsupported job site returns invalid argument`() {
        request.externalId = "urn:hh:resume-id"

        responseObserver.verifyError(Status.INVALID_ARGUMENT) { createApplication() }

        verify(exactly = 0) { getIdempotencyToken() }
    }

    @Test
    fun `when no user id is found returns error`() {
        coEvery { userIdProvider.userId() } returns Status.UNAUTHENTICATED.asFailure("")

        responseObserver.verifyError(Status.UNAUTHENTICATED) { createApplication() }

        verify(exactly = 0) { getIdempotencyToken() }
    }

    @Test
    fun `given no idempotency token returns error`() {
        unmockkStatic(::getIdempotencyToken)

        responseObserver.verifyError(Status.INVALID_ARGUMENT) { createApplication() }
    }

    @Test
    fun `when idemp token insertion failed and lead was already created returns it`() {
        every { anyConstructed<ApplicationInfoDAO>().create(any(), any()) } throws
            PSQLException(null, null)
        every { anyConstructed<ApplicationInfoDAO>().read(any()) } returns "lead-url-created"

        createApplication()

        verify(exactly = 1) {
            responseObserver.onNext(match { it.applicationUrl == "lead-url-created" })
        }
    }

    @Test
    fun `when idemp token insertion failed and lead was not created returns already exists`() {
        every { anyConstructed<ApplicationInfoDAO>().create(any(), any()) } throws
            PSQLException(null, null)
        every { anyConstructed<ApplicationInfoDAO>().read(any()) } returns null

        responseObserver.verifyError(Status.ALREADY_EXISTS) { createApplication() }

        verify(exactly = 1) { anyConstructed<ApplicationInfoDAO>().read(any()) }
    }

    @Test
    fun `when job site returns error removes idemp token and returns error`() {
        coEvery { jobSiteAdapter.getResume(externalId) } returns
            JobSiteResult.Error(Status.Code.UNAVAILABLE, "")

        responseObserver.verifyError(Status.UNAVAILABLE) { createApplication() }

        coVerify(exactly = 1) { jobSiteAdapter.getResume(any()) }
        verify(exactly = 1) { anyConstructed<ApplicationInfoDAO>().remove(any()) }
    }

    @Test
    fun `when job site returns null removes idemp token and returns not_found error`() {
        coEvery { jobSiteAdapter.getResume(externalId) } returns JobSiteResult.Ok(Pair(null, ""))

        responseObserver.verifyError(Status.NOT_FOUND) { createApplication() }

        coVerify(exactly = 1) { jobSiteAdapter.getResume(any()) }
        verify(exactly = 1) { anyConstructed<ApplicationInfoDAO>().remove(any()) }
    }

    @Test
    fun `when resume without contacts is found patches it with personal info from db`() {
        resume.clearContacts()
        val info = PersonalInfo(email = "email@email.ru")
        every { anyConstructed<PersonalInfoDAO>().read(externalId) } returns info
        coEvery { amoAdapter.createApplication(any(), any(), any()) } returns
            Result.success("lead-url")

        createApplication()

        coVerify(exactly = 1) {
            amoAdapter.createApplication(
                pipelineId = 12345,
                userId = 222,
                match { it.contacts.emailsList.singleOrNull() == "email@email.ru" }
            )
        }
    }

    @Test
    fun `when application creation fails removes idempotency token and returns error`() {
        coEvery { amoAdapter.createApplication(any(), any(), any()) } returns
            Status.UNAVAILABLE.asFailure("")

        responseObserver.verifyError(Status.UNAVAILABLE) { createApplication() }

        verify(exactly = 1) { anyConstructed<ApplicationInfoDAO>().remove(any()) }
    }

    @Test
    fun `when application creation succeeded updates lead url in db and returns it`() {
        createApplication()

        verify(exactly = 1) { responseObserver.onNext(match { it.applicationUrl == "lead-url" }) }
        verify(exactly = 1) {
            anyConstructed<ApplicationInfoDAO>().update("idempotency-token", "lead-url")
        }
    }
}
