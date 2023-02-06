package jobsite.headhunter

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.Contact
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.DictionaryEntry
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.DriverLicense
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.Education
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.EducationEntry
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.Experience
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.ExperienceItem
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.HiddenField
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.PhoneValue
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.Photo
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.Resume
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.Salary
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.Specialization
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.convertEducationEntry
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.convertExperienceItem
import ru.yandex.taxi.crm.masshire.search.jobsite.headhunter.convertResume
import ru.yandex.taxi.proto.crm.masshire.JobSite

internal fun phone(formatted: String?, comment: String? = null) =
    Contact.Phone(value = PhoneValue(formatted), comment = comment)

internal fun entry(name: String?) = DictionaryEntry(id = "some-id", name = name)

internal class ConvertResumeKtTest {
    @Nested
    inner class ConvertExperienceItemTest {
        @Test
        fun `given no company won't set company`() {
            val result = convertExperienceItem(ExperienceItem(company = null))

            assertEquals("", result.company)
        }

        @Test
        fun `given company sets company`() {
            val result = convertExperienceItem(ExperienceItem(company = "Yandex"))

            assertEquals("Yandex", result.company)
        }

        @Test
        fun `given no position won't set position`() {
            val result = convertExperienceItem(ExperienceItem(position = null))

            assertEquals("", result.position)
        }

        @Test
        fun `given position sets position`() {
            val result = convertExperienceItem(ExperienceItem(position = "SRE"))

            assertEquals("SRE", result.position)
        }

        @Test
        fun `given no start won't set started`() {
            val result = convertExperienceItem(ExperienceItem(start = null))

            assertFalse(result.hasStarted())
        }

        @Test
        fun `given invalid start won't set started`() {
            val result = convertExperienceItem(ExperienceItem(start = "invalid"))

            assertFalse(result.hasStarted())
        }

        @Test
        fun `given start sets started`() {
            val result = convertExperienceItem(ExperienceItem(start = "2005-01-31"))

            assertEquals(2005, result.started.year)
            assertEquals(1, result.started.month)
            assertEquals(31, result.started.day)
        }

        @Test
        fun `given no end won't set finished`() {
            val result = convertExperienceItem(ExperienceItem(end = null))

            assertFalse(result.hasFinished())
        }

        @Test
        fun `given invalid end won't set finished`() {
            val result = convertExperienceItem(ExperienceItem(end = "invalid"))

            assertFalse(result.hasFinished())
        }

        @Test
        fun `given end sets finished`() {
            val result = convertExperienceItem(ExperienceItem(end = "2005-01-31"))

            assertEquals(2005, result.finished.year)
            assertEquals(1, result.finished.month)
            assertEquals(31, result.finished.day)
        }

        @Test
        fun `given no description won't set description`() {
            val result = convertExperienceItem(ExperienceItem(description = null))

            assertEquals("", result.description)
        }

        @Test
        fun `given description sets description`() {
            val result = convertExperienceItem(ExperienceItem(description = "Yandex"))

            assertEquals("Yandex", result.description)
        }
    }

    @Nested
    inner class ConvertEducationEntryTest {
        @Test
        fun `given education without name won't set name`() {
            val result = convertEducationEntry(EducationEntry(name = null))

            assertEquals("", result.name)
        }

        @Test
        fun `given education with name sets name`() {
            val result = convertEducationEntry(EducationEntry(name = "MSU"))

            assertEquals("MSU", result.name)
        }

        @Test
        fun `given education without year won't set finished`() {
            val result = convertEducationEntry(EducationEntry(year = null))

            assertFalse(result.hasFinished())
        }

        @Test
        fun `given education with year sets finished`() {
            val result = convertEducationEntry(EducationEntry(year = 2000))

            assertEquals(2000, result.finished.year)
        }
    }

    @Nested
    inner class ConvertResumeTest {
        @Test
        fun `always converts id`() {
            val result = convertResume(Resume(id = "1"))

            assertEquals("urn:hh:1", result.origin.externalId)
        }

        @Test
        fun `always sets jobSite`() {
            val result = convertResume(Resume(id = "1"))

            assertEquals(JobSite.JOB_SITE_HEAD_HUNTER, result.origin.jobSite)
        }

        @Test
        fun `given no alternate_url won't set externalUrl`() {
            val result = convertResume(Resume(id = "1", alternate_url = null))

            assertEquals("", result.origin.externalUrl)
        }

        @Test
        fun `given alternate_url sets externalUrl`() {
            val url = "https://hh.ru/resume/1111"
            val result = convertResume(Resume(id = "1", alternate_url = url))

            assertEquals(url, result.origin.externalUrl)
        }

        @Test
        fun `given no first_name won't set firstName`() {
            val result = convertResume(Resume(id = "1", first_name = null))

            assertEquals("", result.firstName)
        }

        @Test
        fun `given first_name sets firstName`() {
            val result = convertResume(Resume(id = "1", first_name = "Arkadiy"))

            assertEquals("Arkadiy", result.firstName)
        }

        @Test
        fun `given no middle_name won't set middleName`() {
            val result = convertResume(Resume(id = "1", middle_name = null))

            assertEquals("", result.middleName)
        }

        @Test
        fun `given middle_name sets middleName`() {
            val result = convertResume(Resume(id = "1", middle_name = "Ivanovich"))

            assertEquals("Ivanovich", result.middleName)
        }

        @Test
        fun `given no last_name won't set lastName`() {
            val result = convertResume(Resume(id = "1", last_name = null))

            assertEquals("", result.lastName)
        }

        @Test
        fun `given last_name sets lastName`() {
            val result = convertResume(Resume(id = "1", last_name = "Ivanov"))

            assertEquals("Ivanov", result.lastName)
        }

        @Test
        fun `given no salary won't set expectedSalary`() {
            val result = convertResume(Resume(id = "1", salary = null))

            assertFalse(result.hasExpectedSalary())
        }

        @Test
        fun `given salary without amount won't set expectedSalary`() {
            val result = convertResume(Resume(id = "1", salary = Salary(amount = null)))

            assertFalse(result.hasExpectedSalary())
        }

        @Test
        fun `given salary with amount sets units`() {
            val result = convertResume(Resume(id = "1", salary = Salary(amount = 10000)))

            assertEquals(10000, result.expectedSalary.units)
        }

        @Test
        fun `given currency and no amount won't set expectedSalary`() {
            val salary = Salary(amount = null, currency = "RUB")
            val result = convertResume(Resume(id = "1", salary = salary))

            assertFalse(result.hasExpectedSalary())
        }

        @Test
        fun `given amount and no currency won't set currency`() {
            val salary = Salary(amount = 10000, currency = null)
            val result = convertResume(Resume(id = "1", salary = salary))

            assertEquals("", result.expectedSalary.currency)
        }

        @Test
        fun `given currency and amount sets currency`() {
            val salary = Salary(amount = 10000, currency = "RUB")
            val result = convertResume(Resume(id = "1", salary = salary))

            assertEquals("RUB", result.expectedSalary.currency)
        }

        @Test
        fun `given no hidden_fields sets contactsAreHidden to false`() {
            val result = convertResume(Resume(id = "1", hidden_fields = null))

            assertFalse(result.contactsAreHidden)
        }

        @Test
        fun `given empty hidden_fields sets contactsAreHidden to false`() {
            val result = convertResume(Resume(id = "1", hidden_fields = listOf()))

            assertFalse(result.contactsAreHidden)
        }

        @Test
        fun `given hidden_fields sets contactsAreHidden`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        hidden_fields = listOf(HiddenField(id = "phones")),
                    )
                )

            assertTrue(result.contactsAreHidden)
        }

        @Test
        fun `given no can_view_full_info won't set contacts`() {
            val result = convertResume(Resume(id = "1", can_view_full_info = null))

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given false can_view_full_info won't set contacts`() {
            val result = convertResume(Resume(id = "1", can_view_full_info = false))

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given can_view_full_info sets contacts`() {
            val result = convertResume(Resume(id = "1", can_view_full_info = true))

            assertTrue(result.hasContacts())
        }

        @Test
        fun `given no contacts won't set contacts`() {
            val result = convertResume(Resume(id = "1", contact = null))

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given empty contacts won't set contacts`() {
            val result = convertResume(Resume(id = "1", contact = listOf()))

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given email with null value won't set contacts`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        contact = listOf(Contact.Email(value = null)),
                    )
                )

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given email adds contacts`() {
            val email = "email@email.com"
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        contact = listOf(Contact.Email(value = email)),
                    )
                )

            assertEquals(1, result.contacts.emailsCount)
            assertEquals(email, result.contacts.emailsList[0])
        }

        @Test
        fun `given phone with null value won't set contacts`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        contact = listOf(Contact.Phone(value = null)),
                    )
                )

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given phone with null formatted won't set contacts`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        contact = listOf(phone(formatted = null)),
                    )
                )

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given phone adds contacts`() {
            val phone = "8(499)123-45-67"
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        contact = listOf(phone(formatted = phone)),
                    )
                )

            assertEquals(1, result.contacts.phonesCount)
            assertEquals(phone, result.contacts.phonesList[0].formatted)
            assertEquals("", result.contacts.phonesList[0].info)
        }

        @Test
        fun `given phone with comment sets contacts info`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        contact = listOf(phone(formatted = "", comment = "info")),
                    )
                )

            assertEquals(1, result.contacts.phonesCount)
            assertEquals("info", result.contacts.phonesList[0].info)
        }

        @Test
        fun `given unknown contact won't set contacts`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        contact = listOf(Contact.UnknownContact),
                    )
                )

            assertFalse(result.hasContacts())
        }

        @Test
        fun `given no experience won't set experience`() {
            val result = convertResume(Resume(id = "1", experience = null))

            assertFalse(result.hasExperience())
        }

        @Test
        fun `given empty experience won't set experience`() {
            val result = convertResume(Resume(id = "1", experience = listOf()))

            assertFalse(result.hasExperience())
        }

        @Test
        fun `given experience adds experience entry`() {
            val result =
                convertResume(
                    Resume(id = "1", experience = listOf(ExperienceItem(company = "Yandex")))
                )

            assertEquals(1, result.experience.entriesCount)
            assertEquals("Yandex", result.experience.entriesList[0].company)
        }

        @Test
        fun `given no total_experience won't set experience`() {
            val result = convertResume(Resume(id = "1", total_experience = null))

            assertFalse(result.hasExperience())
        }

        @Test
        fun `given total_experience without months won't set experience`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        total_experience = Experience(months = null),
                    )
                )

            assertFalse(result.hasExperience())
        }

        @Test
        fun `given total_experience sets totalMonths`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        total_experience = Experience(months = 36),
                    )
                )

            assertEquals(36, result.experience.totalMonths)
        }

        @Test
        fun `given no education won't set education`() {
            val result = convertResume(Resume(id = "1", education = null))

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given no primary education won't set education`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        education = Education(primary = null),
                    )
                )

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given empty primary education won't set education`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        education = Education(primary = listOf()),
                    )
                )

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given primary education adds education entry`() {
            val education = Education(primary = listOf(EducationEntry(name = "MSU")))
            val result = convertResume(Resume(id = "1", education = education))

            assertEquals(1, result.education.entriesCount)
            assertEquals("MSU", result.education.entriesList[0].name)
        }

        @Test
        fun `given no elementary education won't set education`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        education = Education(elementary = null),
                    )
                )

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given empty elementary education won't set education`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        education = Education(elementary = listOf()),
                    )
                )

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given elementary education adds education entry`() {
            val education = Education(elementary = listOf(EducationEntry(name = "MSU")))
            val result = convertResume(Resume(id = "1", education = education))

            assertEquals(1, result.education.entriesCount)
            assertEquals("MSU", result.education.entriesList[0].name)
        }

        @Test
        fun `given no additional education won't set education`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        education = Education(additional = null),
                    )
                )

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given empty additional education won't set education`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        education = Education(additional = listOf()),
                    )
                )

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given additional education adds education entry`() {
            val education = Education(additional = listOf(EducationEntry(name = "MSU")))
            val result = convertResume(Resume(id = "1", education = education))

            assertEquals(1, result.education.entriesCount)
            assertEquals("MSU", result.education.entriesList[0].name)
        }

        @Test
        fun `given no attestation education won't set education`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        education = Education(attestation = null),
                    )
                )

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given empty attestation education won't set education`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        education = Education(attestation = listOf()),
                    )
                )

            assertFalse(result.hasEducation())
        }

        @Test
        fun `given attestation education adds education entry`() {
            val education = Education(attestation = listOf(EducationEntry(name = "MSU")))
            val result = convertResume(Resume(id = "1", education = education))

            assertEquals(1, result.education.entriesCount)
            assertEquals("MSU", result.education.entriesList[0].name)
        }

        @Test
        fun `given no specialization won't add specializations`() {
            val result = convertResume(Resume(id = "1", specialization = null))

            assertEquals(0, result.specializationsCount)
        }

        @Test
        fun `given specialization without profarea_name won't add specializations`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        specialization = listOf(Specialization(profarea_name = null)),
                    )
                )

            assertEquals(0, result.specializationsCount)
        }

        @Test
        fun `given specialization adds specializations`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        specialization = listOf(Specialization(profarea_name = "Sales")),
                    )
                )

            assertEquals(1, result.specializationsCount)
            assertEquals("Sales", result.specializationsList[0])
        }

        @Test
        fun `given same specialization adds only one`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        specialization =
                            listOf(
                                Specialization(profarea_name = "Sales"),
                                Specialization(profarea_name = "Sales"),
                            )
                    )
                )

            assertEquals(1, result.specializationsCount)
            assertEquals("Sales", result.specializationsList[0])
        }

        @Test
        fun `given no title won't set position`() {
            val result = convertResume(Resume(id = "1", title = null))

            assertEquals("", result.position)
        }

        @Test
        fun `given title sets position`() {
            val result = convertResume(Resume(id = "1", title = "Manager"))

            assertEquals("Manager", result.position)
        }

        @Test
        fun `given no age won't set age`() {
            val result = convertResume(Resume(id = "1", age = null))

            assertEquals(0, result.age)
        }

        @Test
        fun `given age sets age`() {
            val result = convertResume(Resume(id = "1", age = 30))

            assertEquals(30, result.age)
        }

        @Test
        fun `given no gender won't set gender`() {
            val result = convertResume(Resume(id = "1", gender = null))

            assertEquals("", result.gender)
        }

        @Test
        fun `given gender without name won't set gender`() {
            val result = convertResume(Resume(id = "1", gender = entry(name = null)))

            assertEquals("", result.gender)
        }

        @Test
        fun `given gender sets gender`() {
            val result = convertResume(Resume(id = "1", gender = entry(name = "Мужской")))

            assertEquals("Мужской", result.gender)
        }

        @Test
        fun `given no area won't add locations`() {
            val result = convertResume(Resume(id = "1", area = null))

            assertEquals(0, result.locationsCount)
        }

        @Test
        fun `given area without name won't add locations`() {
            val result = convertResume(Resume(id = "1", area = entry(name = null)))

            assertEquals(0, result.locationsCount)
        }

        @Test
        fun `given area adds location`() {
            val result = convertResume(Resume(id = "1", area = entry(name = "Кудымкар")))

            assertEquals(1, result.locationsCount)
            assertEquals("Кудымкар", result.locationsList[0])
        }

        @Test
        fun `given no citizenship won't add citizenships`() {
            val result = convertResume(Resume(id = "1", citizenship = null))

            assertEquals(0, result.citizenshipsCount)
        }

        @Test
        fun `given citizenship without name won't add citizenships`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        citizenship = listOf(entry(name = null)),
                    )
                )

            assertEquals(0, result.citizenshipsCount)
        }

        @Test
        fun `given citizenship adds citizenships`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        citizenship = listOf(entry(name = "RU")),
                    )
                )

            assertEquals(1, result.citizenshipsCount)
            assertEquals("RU", result.citizenshipsList[0])
        }

        @Test
        fun `given no driver_license_types won't add driverLicenses`() {
            val result = convertResume(Resume(id = "1", driver_license_types = null))

            assertEquals(0, result.driverLicensesCount)
        }

        @Test
        fun `given driver_license_types without id won't add driverLicenses`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        driver_license_types = listOf(DriverLicense(id = null)),
                    )
                )

            assertEquals(0, result.driverLicensesCount)
        }

        @Test
        fun `given driver_license_types adds driverLicenses`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        driver_license_types = listOf(DriverLicense(id = "A")),
                    )
                )

            assertEquals(1, result.driverLicensesCount)
            assertEquals("A", result.driverLicensesList[0])
        }

        @Test
        fun `given no schedules won't add schedules`() {
            val result = convertResume(Resume(id = "1", schedules = null))

            assertEquals(0, result.schedulesCount)
        }

        @Test
        fun `given schedule without name won't add schedules`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        schedules = listOf(entry(name = null)),
                    )
                )

            assertEquals(0, result.schedulesCount)
        }

        @Test
        fun `given schedules adds schedules`() {
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        schedules = listOf(entry(name = "Сменный график")),
                    )
                )

            assertEquals(1, result.schedulesCount)
            assertEquals("Сменный график", result.schedulesList[0])
        }

        @Test
        fun `given no updated_at won't set updatedAt`() {
            val result = convertResume(Resume(id = "1", updated_at = null))

            assertFalse(result.hasUpdatedAt())
        }

        @Test
        fun `given invalid updated_at won't set updatedAt`() {
            val result = convertResume(Resume(id = "1", updated_at = "invalid"))

            assertFalse(result.hasUpdatedAt())
        }

        @Test
        fun `given updated_at sets updatedAt`() {
            val result =
                convertResume(
                    Resume(id = "1", updated_at = "2013-10-17T15:22:55+0400"),
                )

            assertEquals(1382008975, result.updatedAt.seconds)
        }

        @Test
        fun `given no photo won't set photo`() {
            val result = convertResume(Resume(id = "1", photo = null))

            assertEquals(0, result.photosCount)
        }

        @Test
        fun `given only small photo adds photo`() {
            val photo = "https://hh.ru/photo/111"
            val result = convertResume(Resume(id = "1", photo = Photo(small = photo)))

            assertEquals(1, result.photosCount)
            assertEquals(photo, result.photosList[0].url)
        }

        @Test
        fun `given small and medium photos adds medium photo`() {
            val medium = "https://hh.ru/photo/111"
            val small = "https://hh.ru/photo/111s"
            val result =
                convertResume(
                    Resume(
                        id = "1",
                        photo = Photo(small = small, medium = medium),
                    )
                )

            assertEquals(1, result.photosCount)
            assertEquals(medium, result.photosList[0].url)
        }
    }
}
