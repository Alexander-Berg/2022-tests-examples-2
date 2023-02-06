package amocrm

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import ru.yandex.taxi.crm.masshire.search.amocrm.buildExperienceString
import ru.yandex.taxi.proto.crm.masshire.WorkExperience

internal class BuildExperienceStringTest {
    private val experience = WorkExperience.newBuilder()

    @AfterEach
    fun teardown() {
        experience.clear()
    }

    private fun buildExperience() = buildExperienceString(experience.build())

    @Test
    fun `given empty work experience returns null`() {
        experience.clear()

        assertNull(buildExperience())
    }

    @ParameterizedTest
    @CsvSource(
        value =
            [
                "13,1 год 1 месяц",
                "26,2 года 2 месяца",
                "65,5 лет 5 месяцев",
                "78,6 лет 6 месяцев",
            ]
    )
    fun `given totalMonths returns formatted`(totalMonths: Int, expected: String) {
        experience.totalMonths = totalMonths

        assertEquals("Опыт работы: $expected", buildExperience())
    }

    @Test
    fun `given totalMonths as full years returns only years`() {
        experience.totalMonths = 12

        assertEquals("Опыт работы: 1 год", buildExperience())
    }

    @Test
    fun `given totalMonths less than one year returns only months`() {
        experience.totalMonths = 11

        assertEquals("Опыт работы: 11 месяцев", buildExperience())
    }

    @Test
    fun `given entry returns formatted`() {
        val entry = experience.addEntriesBuilder()
        entry.startedBuilder.day = 10
        entry.startedBuilder.month = 11
        entry.startedBuilder.year = 2020

        entry.finishedBuilder.day = 12
        entry.finishedBuilder.month = 5
        entry.finishedBuilder.year = 2021

        entry.company = "Yandex"
        entry.description = "Calls"
        entry.position = "Operator"

        assertEquals("10.11.2020 - 12.05.2021:\nYandex\nOperator\nCalls", buildExperience())
    }

    @Test
    fun `given entry only with dates skips it`() {
        val entry = experience.addEntriesBuilder()
        entry.startedBuilder.year = 2020

        assertNull(buildExperience())
    }

    @Test
    fun `given date without month doesn't add day`() {
        val entry = experience.addEntriesBuilder()
        entry.startedBuilder.year = 2020
        entry.startedBuilder.day = 15
        entry.company = "Yandex"

        assertEquals("2020 - н.в.:\nYandex", buildExperience())
    }

    @Test
    fun `given date without year doesn't add month and day`() {
        val entry = experience.addEntriesBuilder()
        entry.startedBuilder.day = 15
        entry.startedBuilder.month = 10
        entry.company = "Yandex"

        assertEquals("н.в. - н.в.:\nYandex", buildExperience())
    }
}
