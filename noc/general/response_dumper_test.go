package timemachine

import (
	"compress/gzip"
	"io/ioutil"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"testing"
	"time"

	"github.com/jonboulle/clockwork"
	"github.com/spf13/afero"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/puncher/lib/logging"
	"a.yandex-team.ru/noc/puncher/models"
)

var (
	testBase = "/var/spool/puncher/timemachine/1"
	logger   = logging.Must(log.WarnLevel)
	// Для тестов используется фейковое время
	startTime = time.Date(2020, 01, 02, 04, 05, 00, 00, time.UTC)
	// При изменении надо синхронно менять тест на запись архива
	cauthRules = []models.RawCAuthRule{
		{
			Destination: models.RawCAuthDestination{
				Name: "server1",
				Type: "server",
			},
			Source: models.RawCAuthSource{
				Name: "user1",
				Type: "user",
			},
		},
		{
			Destination: models.RawCAuthDestination{
				Name: "non-server1",
				Type: "otherDstType",
			},
			Source: models.RawCAuthSource{
				Name: "non-user1",
				Type: "otherSrcType",
			},
		},
	}
	staffUsers = []models.StaffUser{
		{
			UID:   "14323",
			Login: "user1",
			Official: models.StaffOfficial{
				Affiliation: "Y",
				IsDismissed: false,
				IsRobot:     false,
			},
			RobotOwners: nil,
			Name: models.StaffName{
				First: models.StaffDualLangName{
					Ru: "юзер1ф",
					En: "user1f",
				},
				Last: models.StaffDualLangName{
					Ru: "юзер1л",
					En: "user1l",
				},
			},
			Groups: nil,
		},
		{
			UID:   "12341234",
			Login: "user-robot-owner",
			Official: models.StaffOfficial{
				Affiliation: "Y",
				IsDismissed: false,
				IsRobot:     false,
			},
			RobotOwners: []models.StaffRobotOwner{
				{
					Person: models.StaffRobotPerson{
						Login: "robot1",
					},
				},
			},
			Name: models.StaffName{
				First: models.StaffDualLangName{
					Ru: "владелец",
					En: "user-robot-owner-first",
				},
				Last: models.StaffDualLangName{
					Ru: "робота",
					En: "user-robot-owner-last",
				},
			},
			Groups: nil,
		},
	}
	staffGroups = []models.StaffGroup{
		{
			ID:        89,
			IsDeleted: false,
			Name:      "g98",
			Type:      "gt1",
			URL:       "h://g98",
			Parent: models.StaffGroupParent{
				ID:  0,
				URL: "h://p98",
				Service: models.StaffGroupParentService{
					ID: 2,
				},
			},
			Department: models.StaffGroupDepartment{
				Name: models.StaffGroupDepartmentName{
					Full: models.StaffDualLangName{
						Ru: "Д1",
						En: "D1",
					},
				},
			},
			Service:   models.StaffGroupService{ID: 5},
			RoleScope: "a:n",
		},
		{
			ID:        76,
			IsDeleted: false,
			Name:      "g76",
			Type:      "gt1",
			URL:       "h://g76",
			Parent: models.StaffGroupParent{
				ID: 89,
				Service: models.StaffGroupParentService{
					ID: 2,
				},
			},
			Department: models.StaffGroupDepartment{
				Name: models.StaffGroupDepartmentName{
					Full: models.StaffDualLangName{
						Ru: "Д2",
						En: "D2",
					},
				},
			},
			Service:   models.StaffGroupService{ID: 5},
			RoleScope: "r:t",
		},
	}
	testSections = sortableSections{
		{
			Name:   "section1",
			Flags:  []string{"f1", "f2"},
			Scope:  []string{"s1", "s2"},
			Scope2: []string{"s21", "s22"},
			Owners: []models.Subject{{
				Type: "user",
				Name: "user1",
			}},
			Ports: []struct {
				Port  string `json:"port"`
				Proto string `json:"proto"`
			}{{
				Port:  "22",
				Proto: "tcp",
			}},
		},
	}
)

func TestHistFileList_Sort(t *testing.T) {
	dates := []string{"200911102300", "200912102300", "200911092300", "200911101400", "201911101400", "201911101300"}
	datesSorted := []string{"201911101400", "201911101300", "200912102300", "200911102300", "200911101400", "200911092300"}
	fl := make(HistFileList, 0)
	flSorted := make(HistFileList, 0)
	for _, d := range dates {
		da, _ := time.Parse("200601021504", d)
		fl = append(fl, HistFile{
			Date: da,
		})
	}
	for _, d := range datesSorted {
		da, _ := time.Parse("200601021504", d)
		flSorted = append(flSorted, HistFile{
			Date: da,
		})
	}
	sort.Sort(fl)
	assert.Equal(t, flSorted, fl)
}

func TestHistFileList_FullSize(t *testing.T) {
	sizes := []int64{20851, 1361342179, 1361379}
	fl := make(HistFileList, 0)
	for _, s := range sizes {
		fl = append(fl, HistFile{
			Size: s,
		})
	}
	assert.Equal(t, int64(1362724409), fl.FullSize())
}

func TestDumperOuota_IsValid(t *testing.T) {
	type fields struct {
		KeepLastN int
		KeepTime  time.Duration
		SizeQuota int64
		AffectN   int
	}
	tests := []struct {
		name    string
		fields  fields
		want    bool
		wantErr bool
	}{
		{
			"Valid",
			fields{
				KeepLastN: 10,
				KeepTime:  0,
				SizeQuota: 0,
				AffectN:   0,
			},
			true,
			false,
		},
		{
			"AllZero",
			fields{
				KeepLastN: 0,
				KeepTime:  0,
				SizeQuota: 0,
				AffectN:   0,
			},
			false,
			true,
		},
		{
			"KeepLastN < 0",
			fields{
				KeepLastN: -1,
				KeepTime:  time.Hour * 24 * 30,
				SizeQuota: 1024 * 1024 * 1024,
				AffectN:   0,
			},
			false,
			true,
		},
		{
			"KeepTime < 0",
			fields{
				KeepLastN: 10,
				KeepTime:  -1,
				SizeQuota: 1024 * 1024 * 1024,
				AffectN:   0,
			},
			false,
			true,
		},
		{
			"SizeQuota < 0",
			fields{
				KeepLastN: 10,
				KeepTime:  time.Hour * 24 * 30,
				SizeQuota: -1,
				AffectN:   0,
			},
			false,
			true,
		},
		{
			"SizeQuota < 0",
			fields{
				KeepLastN: 10,
				KeepTime:  time.Hour * 24 * 30,
				SizeQuota: 1024 * 1024 * 1024,
				AffectN:   -1,
			},
			false,
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			d := &DumperOuota{
				KeepLastN: tt.fields.KeepLastN,
				KeepTime:  tt.fields.KeepTime,
				SizeQuota: tt.fields.SizeQuota,
				AffectN:   tt.fields.AffectN,
			}
			got, err := d.IsValid()
			if (err != nil) != tt.wantErr {
				t.Errorf("IsValid() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("IsValid() got = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMain(m *testing.M) {
	tmFs = afero.Afero{Fs: afero.NewMemMapFs()}
	Clock = clockwork.NewFakeClockAt(startTime)
	os.Exit(m.Run())
}

func TestGzFile(t *testing.T) {
	fileprefix := "test1_file"
	err := tmFs.MkdirAll(testBase, 0755)
	assert.NoError(t, err)
	file, err := NewGzFile(testBase, fileprefix)
	assert.NoError(t, err)
	msg := "test string1x2"
	n, err := file.Write([]byte(msg))
	assert.NoError(t, err)
	assert.Equal(t, len(msg), n)
	n, err = file.WriteString("\n")
	assert.NoError(t, err)
	assert.Equal(t, 1, n)
	err = file.Close()
	assert.NoError(t, err)
	helperTestGzFile(t, testBase, fileprefix, msg+"\n")
}

func TestGzFileError(t *testing.T) {
	fileprefix := "test2_file"
	err := tmFs.MkdirAll(testBase, 0755)
	assert.NoError(t, err)
	tmFs = afero.Afero{Fs: afero.NewReadOnlyFs(afero.NewMemMapFs())}
	_, err = NewGzFile(testBase, fileprefix)
	assert.EqualError(t, err, "operation not permitted")
}

func TestNewDumperError(t *testing.T) {
	tmFs = afero.Afero{Fs: afero.NewMemMapFs()}

	d := NewDumper("test", logger, DumperOuota{
		KeepLastN: 0,
		KeepTime:  0,
		SizeQuota: 0,
		AffectN:   0,
	})
	assert.Equal(t, &Dumper{}, d)
}

func helperTestCountFiles(t *testing.T, d *Dumper, expected int) {
	hfl, err := d.ListFiles()
	assert.NoError(t, err)
	assert.Equal(t, expected, len(hfl))
}

func helperTestGzFile(t *testing.T, basePath string, name string, content string) {
	files, err := tmFs.ReadDir(basePath)
	assert.NoError(t, err)
	assert.Equal(t, 1, len(files))
	assert.True(t, strings.HasSuffix(files[0].Name(), ".gz"))
	assert.Greater(t, files[0].Size(), int64(0))
	f, err := tmFs.Open(filepath.Join(basePath, files[0].Name()))
	assert.NoError(t, err)
	zr, err := gzip.NewReader(f)
	assert.NoError(t, err)
	assert.Equal(t, name, zr.Name)
	msgR, err := ioutil.ReadAll(zr)
	assert.NoError(t, err)
	cnt := []byte(content)
	assert.Equal(t, cnt, msgR)
	hf, err := MakeHistFile(filepath.Join(basePath, files[0].Name()))
	assert.NoError(t, err)
	assert.Equal(t, startTime, hf.Date)
}

func TestDumper_DumpCauth(t *testing.T) {
	tmFs = afero.Afero{Fs: afero.NewMemMapFs()}

	d := NewDumper("test-cauth", logger, DumperOuota{
		KeepLastN: 10,
		KeepTime:  0,
		SizeQuota: 0,
		AffectN:   0,
	})
	assert.NotNil(t, d)
	d.DumpCauth(cauthRules)
	helperTestGzFile(t, d.basePath, "rules",
		"non-user1:otherSrcType:otherDstType:non-server1\nuser1:user:server:server1\n")
}

func TestDumper_DumpSections(t *testing.T) {
	tmFs = afero.Afero{Fs: afero.NewMemMapFs()}

	d := NewDumper("test-sections", logger, DumperOuota{
		KeepLastN: 10,
		KeepTime:  0,
		SizeQuota: 0,
		AffectN:   0,
	})
	assert.NotEqual(t, &Dumper{}, d)
	d.DumpSections(testSections)
	helperTestGzFile(t, d.basePath, "sections",
		`{"Name":"section1","Flags":["f1","f2"],"Scope":["s1","s2"],"scope2":["s21","s22"],`+
			`"Owners":[{"type":"user","name":"user1"}],"Ports":[{"port":"22","proto":"tcp"}]}`+"\n",
	)
}

func TestDumper_WriteCandidates(t *testing.T) {
	tmFs = afero.Afero{Fs: afero.NewMemMapFs()}

	d := NewDumper("test-canditate", logger, DumperOuota{
		KeepLastN: 10,
		KeepTime:  0,
		SizeQuota: 0,
		AffectN:   0,
	})
	assert.NotEqual(t, &Dumper{}, d)
	d.DumpCandidate(models.Candidate{
		Username:     "candidate1",
		ID:           17,
		OfferState:   2,
		StaffGroupID: 7812954,
	})
	d.DumpCandidate(models.Candidate{
		Username:     "candidate2",
		ID:           19,
		OfferState:   1,
		StaffGroupID: 73456378,
	})
	d.WriteCandidates()
	helperTestGzFile(t, d.basePath,
		"test-canditate_candidates",
		`{"username":"candidate1","id":17,"state":2,"group":7812954}`+"\n"+
			`{"username":"candidate2","id":19,"state":1,"group":73456378}`+"\n")
}

func TestDumper_WriteUsers(t *testing.T) {
	tmFs = afero.Afero{Fs: afero.NewMemMapFs()}

	d := NewDumper("test-staff", logger, DumperOuota{
		KeepLastN: 10,
		KeepTime:  0,
		SizeQuota: 0,
		AffectN:   0,
	})
	assert.NotEqual(t, &Dumper{}, d)
	for _, u := range staffUsers {
		d.DumpUser(u)
	}
	assert.Equal(t, 2, len(d.data.(sortableStaffUsers)))
	d.WriteUsers()
	helperTestGzFile(t, d.basePath,
		"test-staff_users",
		`{"uid":"12341234","login":"user-robot-owner","official":{"affiliation":"Y","is_dismissed":false,`+
			`"is_robot":false},"robot_owners":[{"person":{"login":"robot1"}}],"name":{"first":{"ru":"владелец",`+
			`"en":"user-robot-owner-first"},"last":{"ru":"робота","en":"user-robot-owner-last"}},"groups":null}`+"\n"+
			`{"uid":"14323","login":"user1","official":{"affiliation":"Y","is_dismissed":false,"is_robot":false},`+
			`"robot_owners":null,"name":{"first":{"ru":"юзер1ф","en":"user1f"},"last":`+
			`{"ru":"юзер1л","en":"user1l"}},"groups":null}`+"\n")
}

func TestDumper_WriteGroups(t *testing.T) {
	tmFs = afero.Afero{Fs: afero.NewMemMapFs()}

	d := NewDumper("test-staff", logger, DumperOuota{
		KeepLastN: 10,
		KeepTime:  0,
		SizeQuota: 0,
		AffectN:   0,
	})
	assert.NotEqual(t, &Dumper{}, d)
	for _, g := range staffGroups {
		d.DumpGroup(g)
	}
	assert.Equal(t, 2, len(d.data.(sortableStaffGroups)))
	d.WriteGroups()
	helperTestGzFile(t, d.basePath,
		"test-staff_groups",
		`{"id":76,"is_deleted":false,"name":"g76","type":"gt1","url":"h://g76","parent":`+
			`{"id":89,"url":"","service":{"id":2}},"department":{"name":{"full":{"ru":"Д2","en":"D2"}}},`+
			`"service":{"id":5},"role_scope":"r:t"}`+"\n"+
			`{"id":89,"is_deleted":false,"name":"g98","type":"gt1","url":"h://g98","parent":`+
			`{"id":0,"url":"h://p98","service":{"id":2}},"department":{"name":{"full":{"ru":"Д1","en":"D1"}}},`+
			`"service":{"id":5},"role_scope":"a:n"}`+"\n")
}

func TestDumper_Rotate(t *testing.T) {
	tmFs = afero.Afero{Fs: afero.NewMemMapFs()}

	d := NewDumper("test-sections", logger, DumperOuota{
		KeepLastN: 4,
		KeepTime:  0,
		SizeQuota: 0,
		AffectN:   1,
	})
	assert.NotEqual(t, &Dumper{}, d)

	// Тестируем не только удаление по количеству, но и ограничение на затроннутые архивы
	t.Run("KeepLastN", func(t *testing.T) {
		d.DumpCauth(cauthRules)
		for i := 0; i < 5; i++ {
			Clock.(clockwork.FakeClock).Advance(time.Hour)
			d.DumpCauth(cauthRules)
		}
		hfl, err := d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 6, len(hfl))
		d.rotate()
		hfl, err = d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 5, len(hfl))
		d.rotate()
		hfl, err = d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 4, len(hfl))
	})

	t.Run("KeepTime", func(t *testing.T) {
		d.quota = DumperOuota{
			KeepLastN: 0,
			KeepTime:  time.Hour * 2,
			SizeQuota: 0,
			AffectN:   0,
		}
		d.rotate()
		hfl, err := d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 3, len(hfl))
		assert.True(t, Clock.Now().Sub(hfl[2].Date) <= time.Hour*2)
	})

	t.Run("SizeQuota", func(t *testing.T) {
		d.quota = DumperOuota{
			KeepLastN: 0,
			KeepTime:  0,
			SizeQuota: 200,
			AffectN:   0,
		}
		for i := 0; i < 5; i++ {
			Clock.(clockwork.FakeClock).Advance(time.Hour)
			d.DumpCauth(cauthRules)
		}
		d.rotate()
		hfl, err := d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 2, len(hfl))
		assert.GreaterOrEqual(t, int64(200), hfl.FullSize())
	})

	t.Run("KeepLastN and KeepTime", func(t *testing.T) {
		d.quota = DumperOuota{
			KeepLastN: 4,
			KeepTime:  time.Hour * 2,
			SizeQuota: 0,
			AffectN:   0,
		}
		for i := 0; i < 5; i++ {
			Clock.(clockwork.FakeClock).Advance(time.Hour)
			d.DumpCauth(cauthRules)
		}
		d.rotate()
		hfl, err := d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 3, len(hfl))
	})

	t.Run("All quota", func(t *testing.T) {
		d.quota = DumperOuota{
			KeepLastN: 4,
			KeepTime:  time.Hour * 2,
			SizeQuota: 500,
			AffectN:   0,
		}
		d.rotate()
		hfl, err := d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 3, len(hfl))
		for i := 0; i < 5; i++ {
			Clock.(clockwork.FakeClock).Advance(time.Hour)
			d.DumpCauth(cauthRules)
		}
		hfl, err = d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 8, len(hfl))
		Clock.(clockwork.FakeClock).Advance(24 * time.Hour)
		d.rotate()
		hfl, err = d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 2, len(hfl))
	})

	t.Run("Many archives", func(t *testing.T) {
		for i := 0; i < 1000; i++ {
			Clock.(clockwork.FakeClock).Advance(time.Hour)
			d.DumpCauth(cauthRules)
		}
		hfl, err := d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 1002, len(hfl))
		d.rotate()
		hfl, err = d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 992, len(hfl))
		d.quota.AffectN = 100
		d.rotate()
		hfl, err = d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 892, len(hfl))
		d.quota.AffectN = 1000
		Clock.(clockwork.FakeClock).Advance(time.Hour)
		d.rotate()
		hfl, err = d.ListFiles()
		assert.NoError(t, err)
		assert.Equal(t, 2, len(hfl))
	})
}

func TestDumper_Rotate_Mixing(t *testing.T) {
	tmFs = afero.Afero{Fs: afero.NewMemMapFs()}

	du := NewDumper("test-staff", logger, DumperOuota{
		KeepLastN: 6,
		KeepTime:  0,
		SizeQuota: 0,
		AffectN:   0,
	})
	assert.NotEqual(t, &Dumper{}, du)
	dg := NewDumper("test-staff", logger, DumperOuota{
		KeepLastN: 4,
		KeepTime:  0,
		SizeQuota: 0,
		AffectN:   0,
	})
	assert.NotEqual(t, &Dumper{}, dg)
	for _, u := range staffUsers {
		du.DumpUser(u)
	}
	for _, g := range staffGroups {
		dg.DumpGroup(g)
	}
	dg.WriteGroups()
	helperTestCountFiles(t, dg, 1)
	for i := 0; i < 10; i++ {
		Clock.(clockwork.FakeClock).Advance(time.Hour)
		du.WriteUsers()
		dg.WriteGroups()
	}
	helperTestCountFiles(t, du, 10)
	helperTestCountFiles(t, dg, 11)
	du.rotate()
	helperTestCountFiles(t, du, 6)
	helperTestCountFiles(t, dg, 11)
	dg.rotate()
	helperTestCountFiles(t, du, 6)
	helperTestCountFiles(t, dg, 4)
}

func TestDumper_Commit(t *testing.T) {
	tmFs = afero.Afero{Fs: afero.NewMemMapFs()}

	t.Run("Uninited dumper", func(t *testing.T) {
		d := NewDumper("test-commit-err", logger, DumperOuota{
			KeepLastN: 0,
			KeepTime:  0,
			SizeQuota: 0,
			AffectN:   0,
		})
		assert.Equal(t, &Dumper{}, d)
		assert.NotPanics(t, func() { d.Commit("test") })
	})

	t.Run("Double commit", func(t *testing.T) {
		d := NewDumper("test-commit-double", logger, DumperOuota{
			KeepLastN: 7,
			KeepTime:  0,
			SizeQuota: 0,
			AffectN:   1000,
		})
		assert.NotEqual(t, &Dumper{}, d)
		for i := 0; i < 1000; i++ {
			Clock.(clockwork.FakeClock).Advance(time.Hour)
			d.DumpCauth(cauthRules)
		}
		assert.NotPanics(t, func() {
			d.Commit("test")
			d.Commit("test")
		})
		time.Sleep(time.Second)
		helperTestCountFiles(t, d, 7)
		for i := 0; i < 1000; i++ {
			Clock.(clockwork.FakeClock).Advance(time.Hour)
			d.DumpCauth(cauthRules)
		}
		d.rotate()
		helperTestCountFiles(t, d, 7)

	})

	t.Run("Rotate", func(t *testing.T) {
		d := NewDumper("test-commit", logger, DumperOuota{
			KeepLastN: 7,
			KeepTime:  0,
			SizeQuota: 0,
			AffectN:   100,
		})
		assert.NotEqual(t, &Dumper{}, d)
		for i := 0; i < 55; i++ {
			Clock.(clockwork.FakeClock).Advance(time.Hour)
			d.DumpCauth(cauthRules)
		}
		helperTestCountFiles(t, d, 55)
		d.Commit("test")
		time.Sleep(500 * time.Millisecond)
		helperTestCountFiles(t, d, 7)
	})

	t.Run("Commit clears data", func(t *testing.T) {
		d := NewDumper("test-commit-clear", logger, DefaultQuota)
		assert.Nil(t, d.data)

		for _, g := range staffGroups {
			d.DumpGroup(g)
		}
		assert.NotNil(t, d.data)

		d.Commit("test")
		assert.Nil(t, d.data)
	})

}
