package jobsite.superjob

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.BaseEducationEntry
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.DictionaryEntry
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.EducationEntry
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.Phone
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.REMOTE_WORK_ID
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.REMOTE_WORK_VALUE
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.Resume
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.WorkHistoryItem
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.convertBaseEducationEntry
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.convertEducationEntry
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.convertPhone
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.convertResume
import ru.yandex.taxi.crm.masshire.search.jobsite.superjob.convertWorkHistoryItem
import ru.yandex.taxi.proto.crm.masshire.JobSite

internal class ConvertResumeKtTest {
    @Nested
    inner class ConvertWorkHistoryItemTest {
        @Test
        fun `given no name won't set company`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(name = null))

            assertEquals("", result.company)
        }

        @Test
        fun `given name sets company to it`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(name = "Yandex"))

            assertEquals("Yandex", result.company)
        }

        @Test
        fun `given no profession won't set position`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(profession = null))

            assertEquals("", result.position)
        }

        @Test
        fun `given profession sets position to it`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(profession = "DevOps"))

            assertEquals("DevOps", result.position)
        }

        @Test
        fun `given no work won't set description`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(work = null))

            assertEquals("", result.description)
        }

        @Test
        fun `given work sets description to it`() {
            val description = "DevOps of yandex.ru SERP"
            val result = convertWorkHistoryItem(WorkHistoryItem(work = description))

            assertEquals(description, result.description)
        }

        @Test
        fun `given no yearbeg won't set started`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(yearbeg = null))

            assertFalse(result.hasStarted())
        }

        @Test
        fun `given yearbeg sets started year to it`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(yearbeg = 2004))

            assertEquals(2004, result.started.year)
        }

        @Test
        fun `given no monthbeg won't set started month`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(yearbeg = 2004, monthbeg = null))

            assertEquals(0, result.started.month)
        }

        @Test
        fun `given monthbeg sets started month to it`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(yearbeg = 2004, monthbeg = 11))

            assertEquals(11, result.started.month)
        }

        @Test
        fun `given monthbeg without yearbeg won't set started`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(yearbeg = null, monthbeg = 11))

            assertFalse(result.hasStarted())
        }

        @Test
        fun `given no yearend won't set finished`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(yearend = null))

            assertFalse(result.hasFinished())
        }

        @Test
        fun `given yearend sets finished year to it`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(yearend = 2004))

            assertEquals(2004, result.finished.year)
        }

        @Test
        fun `given no monthend won't set finished month`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(yearend = 2004, monthend = null))

            assertEquals(0, result.finished.month)
        }

        @Test
        fun `given monthend sets finished month to it`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(yearend = 2004, monthend = 11))

            assertEquals(11, result.finished.month)
        }

        @Test
        fun `given monthend without yearend won't set finished`() {
            val result = convertWorkHistoryItem(WorkHistoryItem(yearend = null, monthend = 11))

            assertFalse(result.hasFinished())
        }
    }

    @Nested
    inner class ConvertPhoneTest {
        @Test
        fun `given no phone returns null`() {
            val result = convertPhone(Phone(phone = null))

            assertNull(result)
        }

        @Test
        fun `given phone sets formatted to it`() {
            val phone = "+7 (123) 456-78-90"
            val result = convertPhone(Phone(phone = phone))

            assertEquals(phone, result?.formatted)
        }

        @Test
        fun `given no call_from and no call_to won't set info`() {
            val phone = "+7 (123) 456-78-90"
            val result = convertPhone(Phone(phone = phone, call_from = null, call_to = null))

            assertEquals("", result?.info)
        }

        @Test
        fun `given call_from but no call_to won't set info`() {
            val phone = "+7 (123) 456-78-90"
            val result = convertPhone(Phone(phone = phone, call_from = "08:00", call_to = null))

            assertEquals("", result?.info)
        }

        @Test
        fun `given call_to but no call_from won't set info`() {
            val phone = "+7 (123) 456-78-90"
            val result = convertPhone(Phone(phone = phone, call_from = null, call_to = "20:00"))

            assertEquals("", result?.info)
        }

        @Test
        fun `given both call_from and call_to fills info`() {
            val phone = "+7 (123) 456-78-90"
            val result = convertPhone(Phone(phone = phone, call_from = "08:00", call_to = "20:00"))

            assertEquals("08:00–20:00", result?.info)
        }
    }

    @Nested
    inner class ConvertBaseEducationEntryTest {
        @Test
        fun `given no institute won't set name`() {
            val result = convertBaseEducationEntry(BaseEducationEntry(institute = null))

            assertEquals("", result.name)
        }

        @Test
        fun `given institute without title won't set name`() {
            val institute = DictionaryEntry(title = null)
            val result = convertBaseEducationEntry(BaseEducationEntry(institute = institute))

            assertEquals("", result.name)
        }

        @Test
        fun `given institute with title sets name to it`() {
            val institute = DictionaryEntry(title = "MSU")
            val result = convertBaseEducationEntry(BaseEducationEntry(institute = institute))

            assertEquals("MSU", result.name)
        }

        @Test
        fun `given no yearend won't set finished`() {
            val result = convertBaseEducationEntry(BaseEducationEntry(yearend = null))

            assertFalse(result.hasFinished())
        }

        @Test
        fun `given yearend sets finished`() {
            val result = convertBaseEducationEntry(BaseEducationEntry(yearend = 2004))

            assertEquals(2004, result.finished.year)
        }
    }

    @Nested
    inner class ConvertEducationEntryTest {
        @Test
        fun `given no name won't set name`() {
            val result = convertEducationEntry(EducationEntry(name = null))

            assertEquals("", result.name)
        }

        @Test
        fun `given name sets name`() {
            val result = convertEducationEntry(EducationEntry(name = "MSU"))

            assertEquals("MSU", result.name)
        }

        @Test
        fun `given no yearend won't set finished`() {
            val result = convertEducationEntry(EducationEntry(yearend = null))

            assertFalse(result.hasFinished())
        }

        @Test
        fun `given yearend sets finished`() {
            val result = convertEducationEntry(EducationEntry(yearend = 2004))

            assertEquals(2004, result.finished.year)
        }
    }

    @Nested
    inner class ConvertResumeTest {
        @Test
        fun `given resume with id converts it`() {
            val result = convertResume(Resume(id = "42424242"))

            assertTrue(result.hasOrigin())
            assertEquals("urn:sj:42424242", result.origin.externalId)
        }

        @Test
        fun `always sets job site to SuperJob`() {
            val result = convertResume(Resume(id = "42424242"))

            assertTrue(result.hasOrigin())
            assertEquals(JobSite.JOB_SITE_SUPER_JOB, result.origin.jobSite)
        }

        @Test
        fun `given no link won't set externalUrl`() {
            val result = convertResume(Resume(id = "42424242", link = null))

            assertEquals("", result.origin?.externalUrl)
        }

        @Test
        fun `given link sets externalUrl to it`() {
            val link = "https://superjob.ru/resumes/42"
            val result = convertResume(Resume(id = "42", link = link))

            assertEquals(link, result.origin?.externalUrl)
        }

        @Test
        fun `given no firstname won't set firstName`() {
            val result = convertResume(Resume(id = "42", firstname = null))

            assertEquals("", result.firstName)
        }

        @Test
        fun `given firstname sets firstName to it`() {
            val result = convertResume(Resume(id = "42", firstname = "Ivan"))

            assertEquals("Ivan", result.firstName)
        }

        @Test
        fun `given no lastname won't set lastName`() {
            val result = convertResume(Resume(id = "42", lastname = null))

            assertEquals("", result.lastName)
        }

        @Test
        fun `given lastname sets lastName to it`() {
            val result = convertResume(Resume(id = "42", lastname = "Ivanov"))

            assertEquals("Ivanov", result.lastName)
        }

        @Test
        fun `given no middlename won't set middleName`() {
            val result = convertResume(Resume(id = "42", middlename = null))

            assertEquals("", result.middleName)
        }

        @Test
        fun `given middlename sets middleName to it`() {
            val result = convertResume(Resume(id = "42", middlename = "I."))

            assertEquals("I.", result.middleName)
        }

        @Test
        fun `given no bought contacts won't set contacts`() {
            val result = convertResume(Resume(id = "42", contacts_bought = null))

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given not bought contacts won't set contacts`() {
            val result = convertResume(Resume(id = "42", contacts_bought = false))

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given bought contacts adds contacts`() {
            val result = convertResume(Resume(id = "42", contacts_bought = true))

            assertTrue(result.hasContacts())
        }

        @Test
        fun `given no email won't add email to contacts`() {
            val result = convertResume(Resume(id = "42", email = null))

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given email adds email to contacts`() {
            val email = "user@example.com"
            val result = convertResume(Resume(id = "42", email = email))

            assertEquals(1, result.contacts.emailsList.size)
            assertEquals(email, result.contacts.emailsList[0])
        }

        @Test
        fun `given missing phones won't add phones to contacts`() {
            val result = convertResume(Resume(id = "42", phones = null))

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given no phones won't add phones to contacts`() {
            val result = convertResume(Resume(id = "42", phones = listOf()))

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given phones adds phones to contacts`() {
            val phones =
                listOf(
                    Phone(phone = "01"),
                    Phone(phone = "02"),
                )
            val result = convertResume(Resume(id = "42", phones = phones))

            assertEquals(2, result.contacts.phonesList.size)
            assertEquals("01", result.contacts.phonesList[0].formatted)
            assertEquals("02", result.contacts.phonesList[1].formatted)
        }

        @Test
        fun `given no experience_month_count won't set totalMonths`() {
            val result = convertResume(Resume(id = "42", experience_month_count = null))

            assertFalse(result.hasExperience())
        }

        @Test
        fun `given experience_month_count sets totalMonths to it`() {
            val result = convertResume(Resume(id = "42", experience_month_count = 15))

            assertEquals(15, result.experience.totalMonths)
        }

        @Test
        fun `given missing work history won't add experience entries`() {
            val result =
                convertResume(
                    Resume(
                        id = "42",
                        experience_month_count = 10,
                        work_history = null,
                    ),
                )

            assertTrue(result.experience.entriesList.isEmpty())
        }

        @Test
        fun `given work history adds experience entries`() {
            val history =
                listOf(
                    WorkHistoryItem(name = "Company 1"),
                    WorkHistoryItem(name = "Company 2"),
                )
            val result = convertResume(Resume(id = "42", work_history = history))

            assertEquals(2, result.experience.entriesList.size)
            assertEquals("Company 1", result.experience.entriesList[0].company)
            assertEquals("Company 2", result.experience.entriesList[1].company)
        }

        @Test
        fun `given no base education won't add education entries`() {
            val result = convertResume(Resume(id = "42", base_education_history = null))

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given empty base education history won't add education entries`() {
            val result = convertResume(Resume(id = "42", base_education_history = listOf()))

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given non-empty base education history adds education entries`() {
            val education = listOf(BaseEducationEntry(institute = DictionaryEntry(title = "MSU")))
            val result = convertResume(Resume(id = "42", base_education_history = education))

            assertEquals(1, result.education.entriesList.size)
            assertEquals("MSU", result.education.entriesList[0].name)
        }

        @Test
        fun `given no education history won't add education entries`() {
            val result = convertResume(Resume(id = "42", education_history = null))

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given empty education history won't add education entries`() {
            val result = convertResume(Resume(id = "42", education_history = listOf()))

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given non-empty education history adds education entries`() {
            val education = listOf(EducationEntry(name = "MSU"))
            val result = convertResume(Resume(id = "42", education_history = education))

            assertEquals(1, result.education.entriesList.size)
            assertEquals("MSU", result.education.entriesList[0].name)
        }

        @Test
        fun `given no payment won't set expectedSalary`() {
            val result = convertResume(Resume(id = "42", payment = null))

            assertFalse(result.hasExpectedSalary())
        }

        @Test
        fun `given payment sets expectedSalary units`() {
            val result = convertResume(Resume(id = "42", payment = 42))

            assertEquals(42, result.expectedSalary?.units)
        }

        @Test
        fun `given payment and currency sets expectedSalary`() {
            val result =
                convertResume(
                    Resume(
                        id = "42",
                        payment = 42,
                        currency = "USD",
                    ),
                )

            assertEquals(42, result.expectedSalary.units)
            assertEquals("USD", result.expectedSalary.currency)
        }

        @Test
        fun `given currency without payment won't set expectedSalary`() {
            val result = convertResume(Resume(id = "42", currency = "USD"))

            assertFalse(result.hasExpectedSalary())
        }

        @Test
        fun `given no type of work won't add schedule`() {
            val result = convertResume(Resume(id = "42", type_of_work = null))

            assertTrue(result.schedulesList.isEmpty())
        }

        @Test
        fun `given type of work without title won't add schedule`() {
            val typeOfWork = DictionaryEntry(title = null)
            val result = convertResume(Resume(id = "42", type_of_work = typeOfWork))

            assertTrue(result.schedulesList.isEmpty())
        }

        @Test
        fun `given type of work with title adds schedule`() {
            val typeOfWork = DictionaryEntry(title = "fullDay")
            val result = convertResume(Resume(id = "42", type_of_work = typeOfWork))

            assertEquals(listOf("fullDay"), result.schedulesList)
        }

        @Test
        fun `given no place of work won't add schedule`() {
            val result = convertResume(Resume(id = "42", place_of_work = null))

            assertTrue(result.schedulesList.isEmpty())
        }

        @Test
        fun `given place of work with wrong id won't add schedule`() {
            val placeOfWork = DictionaryEntry(id = "some not remote id")
            val result = convertResume(Resume(id = "42", place_of_work = placeOfWork))

            assertTrue(result.schedulesList.isEmpty())
        }

        @Test
        fun `given place of work with correct id adds remote work schedule`() {
            val placeOfWork = DictionaryEntry(id = REMOTE_WORK_ID)
            val result = convertResume(Resume(id = "42", place_of_work = placeOfWork))

            assertEquals(listOf(REMOTE_WORK_VALUE), result.schedulesList)
        }

        @Test
        fun `given no age won't set age`() {
            val result = convertResume(Resume(id = "42", age = null))

            assertEquals(0, result.age)
        }

        @Test
        fun `given age sets age to it`() {
            val result = convertResume(Resume(id = "42", age = 24))

            assertEquals(24, result.age)
        }

        @Test
        fun `given no photo won't add photo`() {
            val result = convertResume(Resume(id = "42", photo = null))

            assertTrue(result.photosList.isEmpty())
        }

        @Test
        fun `given photo returns it`() {
            val photo = "https://static.sj.ru/photos/42/1"
            val result = convertResume(Resume(id = "42", photo = photo))

            assertEquals(result.photosList.size, 1)
            assertEquals(photo, result.photosList.first().url)
        }

        @Test
        fun `given no gender won't set gender`() {
            val result = convertResume(Resume(id = "42", gender = null))

            assertEquals("", result.gender)
        }

        @Test
        fun `given gender with no title won't set gender`() {
            val result = convertResume(Resume(id = "42", gender = DictionaryEntry(title = null)))

            assertEquals("", result.gender)
        }

        @Test
        fun `given gender with title set gender to title`() {
            val result =
                convertResume(Resume(id = "42", gender = DictionaryEntry(title = "apache")))

            assertEquals("apache", result.gender)
        }

        @Test
        fun `given no profession won't set position`() {
            val result = convertResume(Resume(id = "42", profession = null))

            assertEquals("", result.position)
        }

        @Test
        fun `given profession sets position to it`() {
            val result = convertResume(Resume(id = "42", profession = "DevOps"))

            assertEquals("DevOps", result.position)
        }

        @Test
        fun `given no date published and no date modified won't set updatedAt`() {
            val result =
                convertResume(
                    Resume(
                        id = "42",
                        date_published = null,
                        date_last_modified = null,
                    )
                )

            assertFalse(result.hasUpdatedAt())
        }

        @Test
        fun `given date published sets updatedAt to it`() {
            val result =
                convertResume(
                    Resume(
                        id = "42",
                        date_published = 1585581308,
                        date_last_modified = 1605091564,
                    )
                )

            assertEquals(1585581308, result.updatedAt.seconds)
        }

        @Test
        fun `given date modified without date published sets updatedAt to date modified`() {
            val result =
                convertResume(
                    Resume(
                        id = "42",
                        date_published = null,
                        date_last_modified = 1605091564,
                    )
                )

            assertEquals(1605091564, result.updatedAt.seconds)
        }

        @Test
        fun `given no town and no region won't add location`() {
            val result = convertResume(Resume(id = "42", town = null, region = null))

            assertTrue(result.locationsList.isEmpty())
        }

        @Test
        fun `given town adds it as location`() {
            val town = DictionaryEntry(title = "Lobnya")
            val region = DictionaryEntry(title = "Moscow region")
            val result = convertResume(Resume(id = "42", town = town, region = region))

            assertEquals(1, result.locationsList.size)
            assertEquals("Lobnya", result.locationsList[0])
        }

        @Test
        fun `given region and no town adds region as location`() {
            val region = DictionaryEntry(title = "Moscow region")
            val result = convertResume(Resume(id = "42", town = null, region = region))

            assertEquals(1, result.locationsList.size)
            assertEquals("Moscow region", result.locationsList[0])
        }

        @Test
        fun `given no catalogues won't add specializations`() {
            val result = convertResume(Resume(id = "42", catalogues = null))

            assertTrue(result.specializationsList.isEmpty())
        }

        @Test
        fun `given catalogues without title won't add specializations`() {
            val result =
                convertResume(
                    Resume(
                        id = "42",
                        catalogues = listOf(DictionaryEntry(id = "id")),
                    )
                )

            assertTrue(result.specializationsList.isEmpty())
        }

        @Test
        fun `given catalogues with title adds title as specializations`() {
            val catalogues =
                listOf(
                    DictionaryEntry(title = "DevOps"),
                    DictionaryEntry(title = "Software development"),
                )
            val result = convertResume(Resume(id = "42", catalogues = catalogues))

            assertEquals(2, result.specializationsList.size)
            assertEquals("DevOps", result.specializationsList[0])
            assertEquals("Software development", result.specializationsList[1])
        }

        @Test
        fun `given no citizenship won't add citizenships`() {
            val result = convertResume(Resume(id = "42", citizenship = null))

            assertTrue(result.citizenshipsList.isEmpty())
        }

        @Test
        fun `given citizenship without title won't add citizenships`() {
            val citizenship = DictionaryEntry(title = null)
            val result = convertResume(Resume(id = "42", citizenship = citizenship))

            assertTrue(result.citizenshipsList.isEmpty())
        }

        @Test
        fun `given citizenship with title add title to citizenships`() {
            val citizenship = DictionaryEntry(title = "Russia")
            val result = convertResume(Resume(id = "42", citizenship = citizenship))

            assertEquals(1, result.citizenshipsList.size)
            assertEquals("Russia", result.citizenshipsList[0])
        }

        @Test
        fun `given no driver licence wont add driver licenses`() {
            val result = convertResume(Resume(id = "42", driving_licence = null))

            assertTrue(result.driverLicensesList.isEmpty())
        }

        @Test
        fun `given driver licences adds driver licenses`() {
            val licenses = listOf("A", "B")
            val result = convertResume(Resume(id = "42", driving_licence = licenses))

            assertEquals(licenses, result.driverLicensesList)
        }
    }
}
