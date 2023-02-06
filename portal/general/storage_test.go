package storage

import (
	"io/ioutil"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/libs/utils/madm/v2"
	"a.yandex-team.ru/portal/avocado/libs/utils/madm/v2/madmtypes"
	"a.yandex-team.ru/portal/avocado/libs/utils/madmcontent"
	"a.yandex-team.ru/portal/avocado/libs/utils/runtimeconfig/v2"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/contexts"
	"a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
)

type StubFileWatcher struct {
}

func (fw *StubFileWatcher) Serve()       {}
func (fw *StubFileWatcher) Close() error { return nil }

func (fw *StubFileWatcher) Add(config runtimeconfig.Config) error {
	for _, filename := range config.GetPossibleFiles().AsSlice() {
		if _, err := os.Stat(filename); os.IsNotExist(err) {
			continue
		} else if err != nil {
			return err
		}
		data, err := ioutil.ReadFile(filename)
		if err != nil {
			return err
		}
		if err := config.Update(data); err != nil {
			return err
		}
		break
	}
	return nil
}

type ABFlagsTestStruct struct {
	Name       string              `madm:"name"`
	Value      string              `madm:"value"`
	Domain     madmtypes.DomainSet `madm:"domain"`
	Content    string              `madm:"content"`
	Geos       madmtypes.Geos      `madm:"geos"`
	From       *time.Time          `madm:"from"`
	Till       *time.Time          `madm:"to,till"`
	Filter     string              `madm:"filter"`
	YandexOnly bool                `madm:"yandex_only"`
	Yandex100  bool                `madm:"yandex100"`
	Percent    int64               `madm:"percent"`
	Selector   string              `madm:"selector"`
	ExpSlot    int64               `madm:"exp_slot"`
	Disabled   bool                `madm:"disabled"`
}

func TestStorage(t *testing.T) {
	fw := &StubFileWatcher{}

	s, err := NewStorage(log3.NewLoggerStub(), common.Development, nil, "localhost", fw, "testdata")
	require.NoError(t, err)

	items, err := s.StaticData(madm.ABFlagsV2, NewBaseContext(), madm.Yandex(), madm.Enabled(), madm.Dated(madm.UserTime))
	require.NoError(t, err)
	require.Len(t, items, 1)

	var obj ABFlagsTestStruct
	first, err := items.First()
	require.NoError(t, err)
	err = first.Fill(&obj)
	require.NoError(t, err)
	require.Equal(t, "redirect_m2nowww", obj.Name)
}

func NewBaseContext() contexts.Base {
	m := &mocks.Base{}
	m.On("GetRequest").Return(models.Request{
		IsInternal:   false,
		IsStaffLogin: false,
		IsPumpkin:    false,
		URL:          "",
		IP:           "",
		CGI:          nil,
	})
	m.On("GetLocalTimeOffset").Return(3 * time.Hour)
	m.On("GetMordaZone").Return(models.MordaZone{
		Value: "ru",
	}, nil)
	m.On("GetGeo").Return(models.Geo{Parents: []uint32{213, 10000}})
	m.On("GetAppInfo").Return(models.AppInfo{})
	m.On("GetMadmContent").Return(models.MadmContent{
		Values: []string{madmcontent.All},
	})
	m.On("GetTime").Return(&models.TimeData{
		MoscowTime: time.Now(),
		UserTime:   time.Now(),
		UTCTime:    time.Now(),
	})

	return m
}
