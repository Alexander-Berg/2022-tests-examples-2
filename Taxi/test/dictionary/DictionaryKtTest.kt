package dictionary

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource
import ru.yandex.taxi.crm.masshire.search.dictionary.Dictionary
import ru.yandex.taxi.crm.masshire.search.dictionary.DictionaryItem
import ru.yandex.taxi.crm.masshire.search.dictionary.DictionaryType
import ru.yandex.taxi.crm.masshire.search.dictionary.JobSiteFilter
import ru.yandex.taxi.proto.crm.masshire.JobSite

private fun item(name: String, filterId: String, ids: List<String>) =
    DictionaryItem(
        name = name,
        mapping = hashMapOf(JobSite.JOB_SITE_SUPER_JOB to JobSiteFilter(filterId, ids)),
    )

internal class DictionaryKtTest {
    private val schedules =
        Dictionary(
            DictionaryType.SCHEDULES,
            hashMapOf(
                "shift" to item("Сменный график", filterId = "type_of_work", ids = listOf("1")),
                "full_day" to item("Полный день", filterId = "type_of_work", ids = listOf("2")),
                "remote" to item("Удаленно", filterId = "place_of_work", ids = listOf("3")),
            )
        )

    @Test
    fun `always converts to sorted pb`() {
        val dict = schedules.toPb()

        assertEquals(3, dict.entriesList.size)
        assertEquals("full_day", dict.entriesList[0].id)
        assertEquals("Полный день", dict.entriesList[0].value)
        assertEquals("shift", dict.entriesList[1].id)
        assertEquals("Сменный график", dict.entriesList[1].value)
        assertEquals("remote", dict.entriesList[2].id)
        assertEquals("Удаленно", dict.entriesList[2].value)
    }

    @Nested
    inner class IsValidIdTest {
        @Test
        fun `given valid job site and id returns true`() {
            assertTrue(schedules.isValidId(JobSite.JOB_SITE_SUPER_JOB, "remote"))
        }

        @Test
        fun `given non existent id returns false`() {
            assertFalse(schedules.isValidId(JobSite.JOB_SITE_SUPER_JOB, "invalid-id"))
        }

        @Test
        fun `given job site without mapping returns false`() {
            assertFalse(schedules.isValidId(JobSite.JOB_SITE_UNSPECIFIED, "remote"))
        }
    }

    @Nested
    inner class JobSiteFilterTest {
        @Test
        fun `given valid job site and id returns filter`() {
            val filter = schedules.jobSiteFilter(JobSite.JOB_SITE_SUPER_JOB, "shift")

            assertEquals("type_of_work", filter.filterId)
            assertEquals(listOf("1"), filter.ids)
        }

        @Test
        fun `given non existent id throws`() {
            assertThrows(Throwable::class.java) {
                schedules.jobSiteFilter(JobSite.JOB_SITE_SUPER_JOB, "invalid-id")
            }
        }

        @Test
        fun `given job site without mapping throws`() {
            assertThrows(Throwable::class.java) {
                schedules.jobSiteFilter(JobSite.JOB_SITE_UNSPECIFIED, "shift")
            }
        }
    }

    @Nested
    inner class JobSiteFiltersTest {
        @Test
        fun `when ids map to one filter id returns aggregated filter`() {
            val filters =
                schedules.jobSiteFilters(JobSite.JOB_SITE_SUPER_JOB, listOf("shift", "full_day"))

            assertEquals(1, filters.size)
            assertEquals("type_of_work", filters[0].filterId)
            assertEquals(listOf("1", "2"), filters[0].ids)
        }

        @Test
        fun `when ids map to different filter ids returns separate filters`() {
            val filters =
                schedules.jobSiteFilters(JobSite.JOB_SITE_SUPER_JOB, listOf("shift", "remote"))

            assertEquals(2, filters.size)
            assertEquals(JobSiteFilter(filterId = "type_of_work", ids = listOf("1")), filters[0])
            assertEquals(JobSiteFilter(filterId = "place_of_work", ids = listOf("3")), filters[1])
        }
    }

    @ParameterizedTest
    @EnumSource(DictionaryType::class)
    fun `given dictionary type loads dictionary`(dictionaryType: DictionaryType) {
        val result = Dictionary.load(dictionaryType)

        assertTrue(result.toPb().entriesCount > 0)
    }
}
