package jobsite.headhunter

import io.ktor.client.request.HttpRequestBuilder
import io.mockk.clearAllMocks
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.dictionary.DictionaryStorage
import ru.yandex.taxi.crm.masshire.search.dictionary.JobSiteFilter
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.addQueryFilters
import ru.yandex.taxi.proto.crm.masshire.Currency
import ru.yandex.taxi.proto.crm.masshire.ExperienceLevel
import ru.yandex.taxi.proto.crm.masshire.JobSite
import ru.yandex.taxi.proto.crm.masshire.PublicationTime
import ru.yandex.taxi.proto.crm.masshire.ResumeQuery
import ru.yandex.taxi.proto.crm.masshire.SearchLogic
import ru.yandex.taxi.proto.crm.masshire.SearchScope
import ru.yandex.taxi.proto.crm.masshire.SortType

internal class AddQueryFiltersTest {
    private val query = ResumeQuery.newBuilder()
    private val storage = mockk<DictionaryStorage>()

    @AfterEach
    fun teardown() {
        query.clear()
        clearAllMocks()
    }

    private fun verifyFilter(block: HttpRequestBuilder.() -> Unit) {
        val builder = HttpRequestBuilder()
        builder.addQueryFilters(query.build(), storage, JobSite.JOB_SITE_HEAD_HUNTER)
        builder.block()
    }

    private val assertOnlySortType: HttpRequestBuilder.() -> Unit = {
        assertEquals(setOf("order_by"), url.parameters.names())
    }

    @Test
    fun `given several keywordQueries adds all`() {
        query.addKeywordQueriesBuilder().text = "грузчик"
        val keyword = query.addKeywordQueriesBuilder()
        keyword.text = "оператор"
        keyword.searchLogic = SearchLogic.SEARCH_LOGIC_NONE
        keyword.searchScope = SearchScope.SEARCH_SCOPE_TITLE

        verifyFilter {
            assertEquals(listOf("грузчик", "оператор"), url.parameters.getAll("text"))
            assertEquals(listOf("all", "except"), url.parameters.getAll("text.logic"))
            assertEquals(listOf("everywhere", "title"), url.parameters.getAll("text.field"))
            assertEquals(listOf("", ""), url.parameters.getAll("text.period"))
        }
    }

    @Test
    fun `given no keywordQueries won't add them`() {
        query.clearKeywordQueries()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given age from adds it and won't add label`() {
        query.ageBuilder.from = 30

        verifyFilter {
            assertEquals(listOf("30"), url.parameters.getAll("age_from"))
            assertFalse(url.parameters.contains("label"))
        }
    }

    @Test
    fun `given age to adds it and won't add label`() {
        query.ageBuilder.to = 50

        verifyFilter {
            assertEquals(listOf("50"), url.parameters.getAll("age_to"))
            assertFalse(url.parameters.contains("label"))
        }
    }

    @Test
    fun `given both age from and age to also adds only_with_age label`() {
        query.ageBuilder.from = 30
        query.ageBuilder.to = 50

        verifyFilter {
            assertEquals(listOf("30"), url.parameters.getAll("age_from"))
            assertEquals(listOf("50"), url.parameters.getAll("age_to"))
            assertEquals(listOf("only_with_age"), url.parameters.getAll("label"))
        }
    }

    @Test
    fun `given no age won't add filter`() {
        query.clearAge()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given salary from adds it and won't add label`() {
        query.salaryBuilder.rangeBuilder.from = 30000

        verifyFilter {
            assertEquals(listOf("30000"), url.parameters.getAll("salary_from"))
            assertFalse(url.parameters.contains("label"))
        }
    }

    @Test
    fun `given salary to adds it and won't add label`() {
        query.salaryBuilder.rangeBuilder.to = 50000

        verifyFilter {
            assertEquals(listOf("50000"), url.parameters.getAll("salary_to"))
            assertFalse(url.parameters.contains("label"))
        }
    }

    @Test
    fun `given both salary from and salary to adds them and adds only_with_salary label`() {
        query.salaryBuilder.rangeBuilder.from = 30000
        query.salaryBuilder.rangeBuilder.to = 50000

        verifyFilter {
            assertEquals(listOf("30000"), url.parameters.getAll("salary_from"))
            assertEquals(listOf("50000"), url.parameters.getAll("salary_to"))
            assertEquals(listOf("only_with_salary"), url.parameters.getAll("label"))
        }
    }

    @Test
    fun `given range and CURRENCY_RUB adds currency`() {
        query.salaryBuilder.rangeBuilder.from = 10000
        query.salaryBuilder.currency = Currency.CURRENCY_RUB

        verifyFilter { assertEquals(listOf("RUR"), url.parameters.getAll("currency")) }
    }

    @Test
    fun `given CURRENCY_RUB without range won't add currency`() {
        query.salaryBuilder.clearRange()
        query.salaryBuilder.currency = Currency.CURRENCY_RUB

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given range and some other currency won't add it`() {
        query.salaryBuilder.rangeBuilder.from = 10000
        query.salaryBuilder.currency = Currency.CURRENCY_UNSPECIFIED

        verifyFilter { assertFalse(url.parameters.contains("currency")) }
    }

    @Test
    fun `given no salary won't add filters`() {
        query.clearSalary()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given publicationTime adds it`() {
        query.publicationTime = PublicationTime.PUBLICATION_TIME_MONTH

        verifyFilter { assertEquals(listOf("30"), url.parameters.getAll("period")) }
    }

    @Test
    fun `given no publicationTime won't add it`() {
        query.clearPublicationTime()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given several experience levels adds them`() {
        query.experienceBuilder.addLevels(ExperienceLevel.EXPERIENCE_LEVEL_NO_EXPERIENCE)
        query.experienceBuilder.addLevels(ExperienceLevel.EXPERIENCE_LEVEL_JUNIOR)

        verifyFilter {
            assertEquals(
                listOf("noExperience", "between1And3"),
                url.parameters.getAll("experience")
            )
        }
    }

    @Test
    fun `given no experience won't add it`() {
        query.clearExperience()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given locations adds them`() {
        query.locationsBuilder.addAllIds(listOf("1", "2"))
        every { storage.locationDictionary().jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "filter_id", ids = listOf("a", "b")))

        verifyFilter { assertEquals(listOf("a", "b"), url.parameters.getAll("filter_id")) }
    }

    @Test
    fun `given no locations won't add them`() {
        query.clearLocations()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given gender adds it`() {
        query.gendersBuilder.addIds("male")
        every { storage.genderDictionary().jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "gender", ids = listOf("male")))

        verifyFilter { assertEquals(listOf("male"), url.parameters.getAll("gender")) }
    }

    @Test
    fun `given several genders won't add them`() {
        query.gendersBuilder.addAllIds(listOf("male", "female"))
        every { storage.genderDictionary().jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "gender", ids = listOf("male", "female")))

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `when gender dictionary returns several filter ids won't add them`() {
        query.gendersBuilder.addAllIds(listOf("male", "female"))
        every { storage.genderDictionary().jobSiteFilters(any(), any()) } returns
            listOf(
                JobSiteFilter(filterId = "gender1", ids = listOf("male")),
                JobSiteFilter(filterId = "gender2", ids = listOf("female")),
            )

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given no gender won't add it`() {
        query.clearGenders()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given specializations adds them`() {
        query.specializationsBuilder.addAllIds(listOf("1", "2"))
        every { storage.specializationDictionary().jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "roles", ids = listOf("222", "333")))

        verifyFilter { assertEquals(listOf("222", "333"), url.parameters.getAll("roles")) }
    }

    @Test
    fun `given no specializations won't add them`() {
        query.clearSpecializations()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given citizenships adds them`() {
        query.citizenshipsBuilder.addAllIds(listOf("1", "2"))
        every { storage.citizenshipDictionary().jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "citizenship", ids = listOf("222", "333")))

        verifyFilter { assertEquals(listOf("222", "333"), url.parameters.getAll("citizenship")) }
    }

    @Test
    fun `given no citizenships won't add them`() {
        query.clearCitizenships()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given schedules adds them`() {
        query.schedulesBuilder.addAllIds(listOf("1", "2"))
        every { storage.scheduleDictionary().jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "schedule", ids = listOf("222", "333")))

        verifyFilter { assertEquals(listOf("222", "333"), url.parameters.getAll("schedule")) }
    }

    @Test
    fun `given no schedules won't add them`() {
        query.clearSchedules()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given driver licences adds them`() {
        query.driverLicencesBuilder.addAllIds(listOf("1", "2"))
        every { storage.driverLicenceDictionary().jobSiteFilters(any(), any()) } returns
            listOf(JobSiteFilter(filterId = "licence", ids = listOf("222", "333")))

        verifyFilter { assertEquals(listOf("222", "333"), url.parameters.getAll("licence")) }
    }

    @Test
    fun `given no driver licences won't add them`() {
        query.clearDriverLicences()

        verifyFilter(assertOnlySortType)
    }

    @Test
    fun `given some specific sort type adds it`() {
        query.sort = SortType.SORT_TYPE_SALARY_DESCENDING

        verifyFilter { assertEquals(listOf("salary_desc"), url.parameters.getAll("order_by")) }
    }

    @Test
    fun `given no sort type adds default`() {
        query.clearSort()

        verifyFilter { assertEquals(listOf("publication_time"), url.parameters.getAll("order_by")) }
    }
}
