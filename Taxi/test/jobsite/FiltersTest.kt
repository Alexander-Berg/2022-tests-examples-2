package jobsite

import io.ktor.client.request.HttpRequestBuilder
import io.mockk.clearAllMocks
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.dictionary.Dictionary
import ru.yandex.taxi.crm.masshire.search.dictionary.JobSiteFilter
import ru.yandex.taxi.crm.masshire.search.jobsite.addCommaSeparatedIdFilter
import ru.yandex.taxi.crm.masshire.search.jobsite.addMultipleIdFilter
import ru.yandex.taxi.crm.masshire.search.jobsite.addRangeFilter
import ru.yandex.taxi.proto.crm.masshire.IdFilter
import ru.yandex.taxi.proto.crm.masshire.JobSite
import ru.yandex.taxi.proto.crm.masshire.RangeFilter

internal class AddCommaSeparatedIdFilterTest {
    private val idFilter = IdFilter.newBuilder()
    private val dictionary = mockk<Dictionary>()

    @AfterEach
    fun teardown() {
        idFilter.clear()
        clearAllMocks()
    }

    private fun verifyFilter(block: (HttpRequestBuilder) -> Unit) {
        val builder = HttpRequestBuilder()
        builder.addCommaSeparatedIdFilter(dictionary, JobSite.JOB_SITE_SUPER_JOB, idFilter.build())
        block(builder)
    }

    @Test
    fun `when dictionary returns filter with several ids sets them comma separated`() {
        idFilter.addAllIds(listOf("id1", "id2"))

        every { dictionary.jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "filter_id", ids = listOf("1", "2", "3")))

        verifyFilter { assertEquals(listOf("1,2,3"), it.url.parameters.getAll("filter_id")) }

        verify { dictionary.jobSiteFilters(any(), idFilter.idsList) }
    }

    @Test
    fun `when dictionary returns filter with same ids deduplicates them`() {
        every { dictionary.jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "filter_id", ids = listOf("1", "1", "1")))

        verifyFilter { assertEquals(listOf("1"), it.url.parameters.getAll("filter_id")) }
    }
}

internal class AddMultipleIdFilterTest {
    private val idFilter = IdFilter.newBuilder()
    private val dictionary = mockk<Dictionary>()

    @AfterEach
    fun teardown() {
        idFilter.clear()
        clearAllMocks()
    }

    private fun verifyFilter(block: (HttpRequestBuilder) -> Unit) {
        val builder = HttpRequestBuilder()
        builder.addMultipleIdFilter(dictionary, JobSite.JOB_SITE_HEAD_HUNTER, idFilter.build())
        block(builder)
    }

    @Test
    fun `when dictionary returns filter with several ids sets them separate`() {
        idFilter.addAllIds(listOf("id1", "id2"))
        every { dictionary.jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "filter_id", ids = listOf("1", "2")))

        verifyFilter { assertEquals(listOf("1", "2"), it.url.parameters.getAll("filter_id")) }
        verify { dictionary.jobSiteFilters(any(), idFilter.idsList) }
    }

    @Test
    fun `when dictionary returns filter with same ids deduplicates them`() {
        every { dictionary.jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "filter_id", ids = listOf("1", "1", "1")))

        verifyFilter { assertEquals(listOf("1"), it.url.parameters.getAll("filter_id")) }
    }
}

internal class AddRangeFilterTest {
    private val range = RangeFilter.newBuilder()

    @AfterEach
    fun teardown() {
        range.clear()
    }

    private fun verifyFilter(block: (HttpRequestBuilder) -> Unit) {
        val builder = HttpRequestBuilder()
        builder.addRangeFilter(range.build(), filterFrom = "from", filterTo = "to")
        block(builder)
    }

    @Test
    fun `given non zero from value sets it`() {
        range.from = 222

        verifyFilter { assertEquals(listOf("222"), it.url.parameters.getAll("from")) }
    }

    @Test
    fun `given zero from value won't set it`() {
        range.from = 0

        verifyFilter { assertTrue(it.url.parameters.isEmpty()) }
    }

    @Test
    fun `given non zero to value sets it`() {
        range.to = 222

        verifyFilter { assertEquals(listOf("222"), it.url.parameters.getAll("to")) }
    }

    @Test
    fun `given zero to value won't set it`() {
        range.to = 0

        verifyFilter { assertTrue(it.url.parameters.isEmpty()) }
    }

    @Test
    fun `when range filter is not set won't set filters`() {
        range.clear()

        verifyFilter { assertTrue(it.url.parameters.isEmpty()) }
    }
}
