package marcus_test

import (
	"context"
	"regexp"
	"testing"

	"github.com/stretchr/testify/suite"
	"go.uber.org/zap/zaptest"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/alexandria/internal/entities"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies/mocks"
)

const (
	softid     = "Cisco_IOS_12.2/2960_lanbase/122-55.SE12.yaml"
	swtype     = "ios"
	deprecated = false
	modelre    = "C.*"
	rackcode   = "{Cisco}"
)

func makeMatcher(index int, modelRE string, rackCode string, softID string) *entities.MatcherArcadia {
	return &entities.MatcherArcadia{
		Index:    index,
		ModelRe:  regexp.MustCompile(modelRE),
		RackCode: PrepareString(rackCode),
		SoftID:   PrepareString(softID),
	}
}

func PrepareString(check string) *string {
	if check != "" {
		return &check
	}
	return nil
}

func makeMatchers() []*entities.MatcherArcadia {
	return []*entities.MatcherArcadia{
		makeMatcher(0, "^CE128[0-9]{2}", "{Huawei}", "Huawei_VRP_8.5/CE12800/V200R005C10SPC800.yaml"),
		makeMatcher(1, modelre, rackcode, softid),
	}
}

func makeSoft(softid string, swType string, deprecated bool) *entities.SoftArcadia {
	return &entities.SoftArcadia{
		ID:         softid,
		Type:       &swType,
		Deprecated: deprecated,
	}
}

func makeRtResult() entities.ObjectRTClassifiedMap {
	return entities.ObjectRTClassifiedMap{
		"12345": {
			ID:               ptr.String("12345"),
			Name:             ptr.String("vla-s098"),
			FQDN:             ptr.String("vla-s098.yndx.net"),
			HWmodel:          ptr.String("C2960"),
			Vendor:           ptr.String(""),
			SoftID:           ptr.String("Cisco_IOS_12.2/2960_lanbase/122-55.SE12.yaml"),
			SoftMainVersion:  ptr.String("12.2(55)SE12"),
			RackCodesMatched: []*string{ptr.String("1")},
		},
	}
}

func makeRtResultBreed(id string, breed string) entities.ObjectRTBreedMap {
	return entities.ObjectRTBreedMap{
		id: {
			ID:    ptr.String(id),
			Breed: ptr.String(breed),
		},
	}
}

func makeRtResultMany() entities.ObjectRTClassifiedMap {
	return entities.ObjectRTClassifiedMap{
		"12345": {
			ID:               ptr.String("12345"),
			Name:             ptr.String("vla-s098"),
			FQDN:             ptr.String("vla-s098.yndx.net"),
			HWmodel:          ptr.String("C2960"),
			Vendor:           ptr.String("Cisco"),
			SoftID:           ptr.String("Cisco_IOS_12.2/2960_lanbase/122-55.SE12.yaml"),
			SoftMainVersion:  ptr.String("12.2(55)SE12"),
			RackCodesMatched: []*string{ptr.String("1")},
		},
		"54321": {
			ID:               ptr.String("54321"),
			Name:             ptr.String("vla-s097"),
			FQDN:             ptr.String("vla-s097.yndx.net"),
			HWmodel:          ptr.String("CE12804"),
			Vendor:           ptr.String("Huawei"),
			SoftID:           ptr.String("Huawei_VRP_8.5/CE12800/V200R005C10SPC800_V200R005SPH020.yaml"),
			SoftMainVersion:  ptr.String("V200R005C10SPC800"),
			RackCodesMatched: []*string{ptr.String("0")},
		},
	}
}

func makeRequestBulk(needModel bool) entities.MatchBulkMarcusRequest {
	var model0 *string = nil
	var model1 *string = nil
	if needModel {
		model0 = ptr.String("C2960")
		model1 = ptr.String("CE12804")
	}

	return entities.MatchBulkMarcusRequest{
		entities.MarcusRequestTuple{
			ObjectID: ptr.String("12345"),
			Model:    model0,
		},
		entities.MarcusRequestTuple{
			ObjectID: ptr.String("54321"),
			Model:    model1,
		},
	}

}

func makeRecognizeRequest(cmds map[string]string) entities.RecognizeSoftRequest {
	request := entities.RecognizeSoftRequest{
		{
			ObjectID: ptr.String("12345"),
			Cmds:     cmds,
		},
	}
	return request
}

func makeLogger(t *testing.T) log.Logger {
	return &zap.Logger{L: zaptest.NewLogger(t)}
}

type baseStashTestSuite struct {
	suite.Suite
	stash  *mocks.Stash
	ctx    context.Context
	logger log.Logger
}

func (suite *baseStashTestSuite) SetupTest() {
	suite.stash = &mocks.Stash{}
	suite.ctx = context.Background()
	suite.logger = makeLogger(suite.T())
}

func (suite *baseStashTestSuite) TearDownTest() {
	suite.stash.AssertExpectations(suite.T())
}
