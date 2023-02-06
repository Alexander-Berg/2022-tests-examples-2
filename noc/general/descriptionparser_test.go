package descriptionparser

import (
	"reflect"
	"testing"
	"time"

	"github.com/gofrs/uuid"

	"a.yandex-team.ru/noc/nocrfcsd/internal/models"
)

const (
	description1 = `**Название изменения**
{{anchor name="rfc-name-start"}}Катим RT{{anchor name="rfc-name-stop"}}

**Тип изменения**
{{anchor name="rfc-type-start"}}Normal{{anchor name="rfc-type-stop"}}

**Связанный инцидент**
{{anchor name="rfc-linked-incident-start"}} {{anchor name="rfc-linked-incident-stop"}}

**Исполнитель**
{{anchor name="rfc-responsible-start"}}Курбанов Азат (azatkurbanov){{anchor name="rfc-responsible-stop"}}

**Добавить в календарь**
{{anchor name="rfc-addtocal-start"}}Да{{anchor name="rfc-addtocal-stop"}}

**Прямое согласование**
{{anchor name="rfc-add-approvers-start"}}Нет{{anchor name="rfc-add-approvers-stop"}}

**Согласовать (1)**
{{anchor name="rfc-add-approver1-start"}}{{anchor name="rfc-add-approver1-stop"}}

**Согласовать (2)**
{{anchor name="rfc-add-approver2-start"}}{{anchor name="rfc-add-approver2-stop"}}

**Согласовать (3)**
{{anchor name="rfc-add-approver3-start"}}{{anchor name="rfc-add-approver3-stop"}}

**Подсистема (как в Infra)**
{{anchor name="rfc-infra-start"}}NOC API - Racktables{{anchor name="rfc-infra-stop"}}

**Область применения изменения**
{{anchor name="rfc-dc-start"}}Другое{{anchor name="rfc-dc-stop"}}

**Устройства**
{{anchor name="rfc-devices-expression-start"}}noc-sas,   iva13-s666,iva13-s667, {Ивантеевка} and not {в оффлайне} and {лаборатория Владимир},,,sas-e2.yndx.net{{anchor name="rfc-devices-expression-stop"}}

**Предыдущий опыт/успех изменения**
{{anchor name="rfc-experience-start"}}Был опыт и он был успешным {{anchor name="rfc-experience-stop"}}

**Автоматизация изменения**
{{anchor name="rfc-chg-auto-start"}}Да {{anchor name="rfc-chg-auto-stop"}}

**Тестирование изменения (в случае отсутствия автоматизации)**
{{anchor name="rfc-chg-test-start"}} {{anchor name="rfc-chg-test-stop"}}

**Влияние на сервис**
{{anchor name="rfc-service-impact-start"}}Нет{{anchor name="rfc-service-impact-stop"}}

**Потенциальное влияние на сервис(ы)**
{{anchor name="rfc-services-start"}}{{anchor name="rfc-services-stop"}}

**Длительность влияния и откат**
{{anchor name="rfc-influence-rollback-start"}}{{anchor name="rfc-influence-rollback-stop"}}

**Дата проведения работ**
{{anchor name="rfc-date-start"}}2021-06-09{{anchor name="rfc-date-stop"}}

**Дата окончания работ**
{{anchor name="rfc-date-end-start"}}{{anchor name="rfc-date-end-stop"}}

**Время начала работ**
{{anchor name="rfc-time-begin-start"}}20:00{{anchor name="rfc-time-begin-stop"}}

**Время окончания работ**
{{anchor name="rfc-time-end-start"}}20:10{{anchor name="rfc-time-end-stop"}}

**Описание изменения**
{{anchor name="rfc-description-start"}}Выкатываю:

- https://noc-gitlab.yandex-team.ru/nocdev/racktables/-/merge_requests/1201 {{anchor name="rfc-description-stop"}}

**План подготовки к изменению**
{{anchor name="rfc-preparation-start"}} {{anchor name="rfc-preparation-stop"}}

**План выполнения изменения**
{{anchor name="rfc-execution-start"}}git pull {{anchor name="rfc-execution-stop"}}

**План отката изменения**
{{anchor name="rfc-rollback-start"}}git revert && git pull {{anchor name="rfc-rollback-stop"}}

**Установить мьют в хите**
{{anchor name="rfc-set-juggler-mute-start"}}Да{{anchor name="rfc-set-juggler-mute-stop"}}

**Mondata help keys для мьюта**
{{anchor name="rfc-juggler-mute-mondata-help-keys-start"}}mykey3,mykey2 , mykey1, mondata_help_mykey4{{anchor name="rfc-juggler-mute-mondata-help-keys-stop"}}
`
)

func timeMust(t *testing.T, rfc3339Time string) time.Time {
	t.Helper()
	ret, err := time.Parse(time.RFC3339, rfc3339Time)
	if err != nil {
		t.Fatalf("error parsing time test data: %v", err)
	}

	return ret
}

func Test_Parse(t *testing.T) {
	wantRFC1 := &models.RFC{
		ID:                        uuid.UUID{},
		Name:                      "Катим RT",
		ChangeType:                models.ChangeTypeNormal,
		LinkedIncident:            "",
		Responsible:               models.StaffUser{Login: "azatkurbanov"},
		AddToResponsiblesCalendar: true,
		AdditionalApprovers:       nil,
		ChangedService:            models.InfraEnvironment{ServiceName: "NOC API", EnvironmentName: "Racktables"},
		Datacenters:               []models.Datacenter{models.DatacenterOther},
		DevicesExpression:         "noc-sas,   iva13-s666,iva13-s667, {Ивантеевка} and not {в оффлайне} and {лаборатория Владимир},,,sas-e2.yndx.net",
		PreviousExperience:        models.PreviousExperienceSuccessful,
		ChangeAutomation:          models.ChangeAutomationAutomated,
		ChangeTesting:             models.ChangeTestingUnknown,
		ServiceImpact:             models.ServiceImpactAbsent,
		ImpactedABCServices:       nil,
		Interruption:              models.InterruptionTypeUnknown,
		Rollback:                  models.RollbackTypeUnknown,
		StartTime:                 timeMust(t, "2021-06-09T20:00:00+03:00"),
		EndTime:                   timeMust(t, "2021-06-09T20:10:00+03:00"),
		ChangeDescription: `Выкатываю:

- https://noc-gitlab.yandex-team.ru/nocdev/racktables/-/merge_requests/1201`,
		PreparationDescription: "",
		ExecutionDescription:   "git pull",
		RollbackDescription:    "git revert && git pull",
		JugglerMute: &models.JugglerMute{
			MondataHelpKeys: []string{"mykey1", "mykey2", "mykey3", "mykey4"},
		},
	}
	got, err := Parse(description1)
	if err != nil {
		t.Errorf("parseStartrekIssueDescription() error = %v, wantErr nil", err)
	}
	if !reflect.DeepEqual(got, wantRFC1) {
		t.Errorf("parseStartrekIssueDescription() = %+v, want %+v", got, wantRFC1)
	}
}
