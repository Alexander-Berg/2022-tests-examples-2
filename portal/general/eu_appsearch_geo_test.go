package madm

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/fs"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/libs/utils/madm/paths"
	"a.yandex-team.ru/portal/avocado/libs/utils/runtimeconfig/v2"
)

func Test_euAppSearchGeoReader_IsAppSearchShort(t *testing.T) {
	fileData := `
{
   "all" : [
      {
         "app_platform" : "android",
         "app_version_min" : "20080000",
         "blocks" : "search_api services_api_eu privacy_api_eu",
         "except_countries" : "ru ua by kz uz tr",
         "except_langs" : "ru uk be kk tt tr uz",
         "geos" : "117, 206, 123, 120, 179, 115, 246, 116, 10074, 20574, 10077"
      },
      {
         "app_platform" : "android",
         "app_version_min" : "20080000",
         "blocks" : "search_api privacy_api_eu",
         "except_countries" : "ru ua by kz uz tr",
         "except_langs" : "ru uk be kk tt tr uz",
         "geos" : "203, 10064, 10069"
      },
      {
         "app_platform" : "android",
         "app_version_min" : "21020200",
         "blocks" : "search_api services_api_eu privacy_api_eu",
         "except_countries" : "ru ua by kz uz tr",
         "except_langs" : "ru uk be kk tt tr uz",
         "geos" : "10083, 10067, 122, 84, 994"
      }
   ],
   "index" : {
      "geo" : "1",
      "geos" : "1"
   },
   "options" : {
      "app" : "1",
      "enabled" : "1",
      "index" : [
         "geos"
      ],
      "index_fields" : [
         "geos"
      ],
      "json_asis" : "1",
      "mix" : "0",
      "v" : "2"
   }
}`

	testCases := []struct {
		name    string
		appInfo models.AppInfo
		apiInfo models.APIInfo
		geos    []uint32
		want    bool
	}{
		{
			name: "not short for wrong apiInfo",
			appInfo: models.AppInfo{
				Platform: "android",
				Version:  "21020200",
			},
			apiInfo: models.APIInfo{},
			geos:    []uint32{1},
		},
		{
			name: "not short for no geos",
			appInfo: models.AppInfo{
				Platform: "android",
				Version:  "21020200",
			},
			apiInfo: models.APIInfo{
				RealName: "search",
			},
		},
		{
			name: "not short for no platform",
			appInfo: models.AppInfo{
				Version: "21020200",
			},
			apiInfo: models.APIInfo{
				RealName: "search",
			},
			geos: []uint32{1},
		},
		{
			name: "not short for wrong geo",
			appInfo: models.AppInfo{
				Platform: "android",
				Version:  "21020200",
			},
			apiInfo: models.APIInfo{
				RealName: "search",
			},
			geos: []uint32{0},
		},
		{
			name: "short",
			appInfo: models.AppInfo{
				Platform: "android",
				Version:  "21020200",
			},
			apiInfo: models.APIInfo{
				RealName: "search",
			},
			geos: []uint32{84},
			want: true,
		},
		{
			name: "short even if wrong geos are included",
			appInfo: models.AppInfo{
				Platform: "android",
				Version:  "21020200",
			},
			apiInfo: models.APIInfo{
				RealName: "search",
			},
			geos: []uint32{0, 0, 0, 84, 0},
			want: true,
		},
		{
			name: "not short because of version",
			appInfo: models.AppInfo{
				Platform: "android",
				Version:  "21020199",
			},
			apiInfo: models.APIInfo{
				RealName: "search",
			},
			geos: []uint32{84},
		},
		{
			name: "not short because of platform",
			appInfo: models.AppInfo{
				Platform: "vedroid",
				Version:  "21020200",
			},
			apiInfo: models.APIInfo{
				RealName: "search",
			},
			geos: []uint32{84},
		},
		{
			name: "not short because of lang",
			appInfo: models.AppInfo{
				Platform: "android",
				Version:  "21020200",
				Lang:     "ru",
			},
			apiInfo: models.APIInfo{
				RealName: "search",
			},
			geos: []uint32{84},
		},
		{
			name: "not short because of country",
			appInfo: models.AppInfo{
				Platform: "android",
				Version:  "21020200",
				Country:  "ru",
			},
			apiInfo: models.APIInfo{
				RealName: "search",
			},
			geos: []uint32{84},
		},
	}

	dir := ""
	fileName := "eu_appsearch_geo"
	env := common.Development

	path := paths.NewPathsProvider(env, common.GetHostname()).GetSettingsPaths(dir, fileName)

	fileInfo := fs.NewVirtualFileInfo(path[0], time.Now())
	fileContents := []byte(fileData)
	file := fs.NewVirtualFile(fileContents, fileInfo)
	vfs, err := fs.NewVirtualFileSystem(file)
	require.NoError(t, err)

	logger := log3.NewLoggerStub()
	fileWatcher, err := runtimeconfig.NewFileWatcher(vfs, logger, nil, nil)
	require.NoError(t, err)

	reader, err := NewEUAppSearchGeoReader(dir, env, logger, fileWatcher)
	require.NoError(t, err)
	reader.WaitForInit()

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			assert.Equal(t, testCase.want, reader.IsAppSearchShort(testCase.appInfo, testCase.apiInfo, testCase.geos))
		})
	}
}
