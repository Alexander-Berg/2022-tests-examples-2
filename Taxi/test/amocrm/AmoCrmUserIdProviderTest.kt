package amocrm

import io.grpc.Status
import io.mockk.clearAllMocks
import io.mockk.coEvery
import io.mockk.every
import io.mockk.justRun
import io.mockk.mockk
import io.mockk.mockkConstructor
import io.mockk.mockkObject
import io.mockk.verify
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.BlackboxClient
import ru.yandex.taxi.crm.masshire.search.UserCredentials
import ru.yandex.taxi.crm.masshire.search.amocrm.AmoCrmUserIdProvider
import ru.yandex.taxi.crm.masshire.search.db.AmocrmUsersDAO
import ru.yandex.taxi.crm.masshire.search.db.TokenInfoDAO

internal class AmoCrmUserIdProviderTest {
    private val blackbox = mockk<BlackboxClient>()
    private val provider = AmoCrmUserIdProvider(blackbox)

    @BeforeEach
    fun setup() {
        mockkObject(UserCredentials)
        every { UserCredentials.get() } returns
            UserCredentials(userUid = "123", userTicket = "user-ticket")

        mockkConstructor(AmocrmUsersDAO::class)
        mockkConstructor(TokenInfoDAO::class)
    }

    @AfterEach fun teardown() = clearAllMocks()

    private fun userId() = runBlocking { provider.userId() }

    @Test
    fun `when login and user id in db returns user id`() {
        every { anyConstructed<TokenInfoDAO>().readLogin(any()) } returns "user"
        every { anyConstructed<AmocrmUsersDAO>().read("user") } returns 222

        assertEquals(222, userId().getOrNull())
    }

    @Test
    fun `given no saved login fetches it from blackbox and saves to db`() {
        every { anyConstructed<TokenInfoDAO>().readLogin(any()) } returns null
        coEvery { blackbox.getUserLogin(any()) } returns "bb-user"
        every { anyConstructed<AmocrmUsersDAO>().read("bb-user") } returns 111
        justRun { anyConstructed<TokenInfoDAO>().updateLogin(any(), any()) }

        assertEquals(111, userId().getOrNull())

        verify { anyConstructed<TokenInfoDAO>().updateLogin(any(), "bb-user") }
    }

    @Test
    fun `when can't fetch login from db and blackbox returns internal error`() {
        every { anyConstructed<TokenInfoDAO>().readLogin(any()) } returns null
        coEvery { blackbox.getUserLogin(any()) } returns null

        assertError(Status.Code.INTERNAL, userId())
    }

    @Test
    fun `when can't get user id from db returns unauthenticated error`() {
        every { anyConstructed<TokenInfoDAO>().readLogin(any()) } returns "user"
        every { anyConstructed<AmocrmUsersDAO>().read(any()) } returns null

        assertError(Status.Code.UNAUTHENTICATED, userId())
    }
}
