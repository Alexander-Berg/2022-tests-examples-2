package requirements_test

import (
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/yadi/pkg/manager"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager/pip/requirements"
)

func TestReadRequirementsFile(t *testing.T) {
	cases := []struct {
		reqFile  string
		deps     []manager.Dependency
		withDev  bool
		mustFail bool
	}{
		{
			reqFile: "editable.txt",
			deps: []manager.Dependency{
				{
					Name:        "MyPackage",
					RawVersions: "=3.0",
					Language:    "python",
				},
			},
			withDev:  false,
			mustFail: false,
		},
		{
			reqFile: "hashes.txt",
			deps: []manager.Dependency{
				{
					Name:        "flask",
					RawVersions: "=0.12.2",
					Language:    "python",
				},
				{
					Name:        "flask-script",
					RawVersions: "=2.0.6",
					Language:    "python",
				},
			},
			withDev:  false,
			mustFail: false,
		},
		{
			reqFile: "reference.txt",
			deps: []manager.Dependency{
				{
					Name:        "ref_prod_pkg",
					RawVersions: ">0.0.0",
					Language:    "python",
				},
				{
					Name:        "MyPackage",
					RawVersions: ">=1.1 =1.*",
					Language:    "python",
				},
			},
			withDev:  false,
			mustFail: false,
		},
		{
			reqFile: "reference.txt",
			deps: []manager.Dependency{
				{
					Name:        "ref_prod_pkg",
					RawVersions: ">0.0.0",
					Language:    "python",
				},
				{
					Name:        "ref_dev_pkg",
					RawVersions: ">0.0.0",
					Language:    "python",
				},
				{
					Name:        "MyPackage",
					RawVersions: ">=1.1 =1.*",
					Language:    "python",
				},
			},
			withDev:  true,
			mustFail: false,
		},
		{
			reqFile: "simple.txt",
			deps: []manager.Dependency{
				{
					Name:        "lol",
					RawVersions: ">=3.0",
					Language:    "python",
				},
				{
					Name:        "kek",
					RawVersions: "<=3.0",
					Language:    "python",
				},
			},
			withDev:  false,
			mustFail: false,
		},
		{
			reqFile: "specifiers.txt",
			deps: []manager.Dependency{
				{
					Name:        "LolKek",
					RawVersions: "=5.4",
					Language:    "python",
				},
			},
			withDev:  false,
			mustFail: false,
		},
		{
			reqFile:  "not-existed.txt",
			mustFail: true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.reqFile, func(t *testing.T) {
			req, err := requirements.ReadRequirementsFile(filepath.Join("testdata", tc.reqFile), tc.withDev)
			if tc.mustFail {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.deps, req.AllDependencies())
		})
	}
}

//TODO(buglloc): test extras
