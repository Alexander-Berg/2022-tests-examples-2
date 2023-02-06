package storage

import (
	"context"
	"encoding/json"
	"path"
	"strconv"
	"testing"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/config"
	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/fraud"
	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/logs"
)

const (
	DefaultHostID = 0x7F
)

func getTestDBSchemaPath() string {
	return path.Join(
		yatest.SourcePath("passport/infra/daemons/yasmsd/internal/testdata"),
		"storage_test.sqlite")
}

// Создание тестовой базы с очередью из count sms-сообщений.
func createTestSmsQueue(count int) (*Storage, error) {
	storage, err := CreateTestDatabase(getTestDBSchemaPath())
	if err != nil {
		return nil, err
	}

	query := "INSERT INTO `smsqueue_anonym` (`phone`, `gateid`, `text`, `create_time`, `touch_time`, `sender`, `metadata`) VALUES (?, ?, ?, ?, ?, ?, ?)"
	for i := 0; i < count; i++ {
		created := time.Now()
		data, _ := json.Marshal(fraud.Metadata{
			UserPhone:   "+70000000000",
			Timestamp:   created,
			RequestPath: "/please/send/my/sms",
		})

		_, err = storage.DB.Exec(query,
			"+70000000000",
			32,
			"sms-"+strconv.Itoa(i+1),
			created.Format(time.RFC3339),
			created.Format(time.RFC3339),
			"passport",
			data,
		)
		if err != nil {
			storage.Close()
			return nil, err
		}
	}

	return storage, nil
}

func TestGlobalSmsId(t *testing.T) {
	expected := uint64(2255999999999999)
	actual := GlobalSmsID(0xFF, 999999999999)
	if expected != actual {
		t.Errorf(`expected: %d, actual: %d`, expected, actual)
	}

	expected = uint64(2001000000000001)
	actual = GlobalSmsID(0x01, 1)
	if expected != actual {
		t.Errorf(`expected: %d, actual: %d`, expected, actual)
	}
}

func TestMaskedPhone(t *testing.T) {
	check := func(phone, expected string) {
		actual := MaskedPhone(phone)
		if actual != expected {
			t.Errorf(`maskedPhone("%s"), expected: "%s", actual: "%s"`, phone, expected, actual)
		}
	}

	check("", "")
	check("+7000", "+7000")
	check("+70000", "+7****")
	check("+71234567890", "+7123456****")
}

func TestExecHeartbeat(t *testing.T) {
	storage, err := CreateTestDatabase(getTestDBSchemaPath())
	if err != nil {
		t.Fatal(err)
	}
	defer storage.Close()

	err = execHeartbeat(context.Background(), storage.DB, "yasms-test-v1.passport.yandex.net")
	if err != nil {
		t.Error(err)
	}

	// TODO: проверить, что именно записалось.
}

func TestSmsString(t *testing.T) {
	sms := &SmsRow{}
	str := sms.String()
	if len(str) == 0 {
		t.Error("expected > 0")
	}
}

func TestSmsStatboxRecord(t *testing.T) {
	sms := &SmsRow{}
	statbox := sms.StatboxSlice(PrivateSliceFormatter{}, "test-action", []string{logs.StatboxFieldPrice, "50"})
	if len(statbox) == 0 {
		t.Error("expected > 0")
	} else if len(statbox)%2 != 0 {
		t.Error("expected even length")
	}
}

func TestSmsStatboxFormatter(t *testing.T) {
	sms := &SmsRow{}
	sms.Phone = "+71234567890"
	statboxPublic := sms.StatboxPrivateSlice("test-action", []string{logs.StatboxFieldPrice, "50"})
	require.Equal(t, config.SenderStatboxType, statboxPublic[1])
	require.Equal(t, "number", statboxPublic[10])
	require.Equal(t, sms.Phone, statboxPublic[11])

	statboxPrivate := sms.StatboxPublicSlice("test-action", []string{logs.StatboxFieldPrice, "50"})
	require.Equal(t, config.SenderStatboxType, statboxPrivate[1])
	require.Equal(t, "masked_number", statboxPrivate[10])
	require.Equal(t, "+7123456****", statboxPrivate[11])
}

func TestQuerySmsList(t *testing.T) {
	count := 10

	storage, err := createTestSmsQueue(count)
	if err != nil {
		t.Fatal(err)
	}
	defer storage.Close()

	list, err := QuerySmsList(context.Background(), storage.DB, uint64(count+1), DefaultHostID)
	if err != nil {
		t.Error(err)
		return
	}

	if len(list) != count {
		t.Errorf("expected: %d, actual: %d", count, len(list))
		return
	}

	actual := list[5]

	if actual.ID == 0 {
		t.Error("expected > 0")
	}
	if len(actual.GUID) == 0 {
		t.Error("expected > 0")
	}
	if len(actual.Phone) == 0 {
		t.Error("expected > 0")
	}
	if len(actual.Text) == 0 {
		t.Error("expected > 0")
	}
	if actual.Gate == 0 {
		t.Error("expected > 0")
	}
	if len(actual.Sender) == 0 {
		t.Error("expected > 0")
	}
}

func TestUpdateSmsStatus(t *testing.T) {
	count := 10

	storage, err := createTestSmsQueue(count)
	if err != nil {
		t.Fatal(err)
	}
	defer storage.Close()

	err = UpdateSmsStatus(context.Background(), storage.DB, 5, SmsStatusLocked)
	if err != nil {
		t.Error(err)
		return
	}

	list, err := QuerySmsList(context.Background(), storage.DB, uint64(count+1), DefaultHostID)
	if err != nil {
		t.Error(err)
		return
	}

	if len(list) != count-1 {
		t.Errorf("expected: %d, actual: %d", count-1, len(list))
		return
	}
}

func TestSuspendSms(t *testing.T) {
	count := 10

	storage, err := createTestSmsQueue(count)
	if err != nil {
		t.Fatal(err)
	}
	defer storage.Close()

	//
	// попытка 1
	//

	err = SuspendSms(context.Background(), storage.DB, 5, 0, time.Second)
	if err != nil {
		t.Error(err)
		return
	}

	// sms должна появиться заново только через 1 секунду
	list, err := QuerySmsList(context.Background(), storage.DB, uint64(count+1), DefaultHostID)
	if err != nil {
		t.Error(err)
		return
	}

	if len(list) != count-1 {
		t.Errorf("expected: %d, actual: %d", count-1, len(list))
		return
	}

	time.Sleep(1 * time.Second)

	list, err = QuerySmsList(context.Background(), storage.DB, uint64(count+1), DefaultHostID)
	if err != nil {
		t.Error(err)
		return
	}

	if len(list) != count {
		t.Errorf("expected: %d, actual: %d", count, len(list))
		return
	}

	//
	// попытка 2
	//

	err = SuspendSms(context.Background(), storage.DB, 5, 1, 0)
	if err != nil {
		t.Error(err)
		return
	}

	time.Sleep(1 * time.Second)

	list, err = QuerySmsList(context.Background(), storage.DB, uint64(count+1), DefaultHostID)
	if err != nil {
		t.Error(err)
		return
	}

	if len(list) != count-1 {
		t.Errorf("expected: %d, actual: %d", count-1, len(list))
		return
	}
}
