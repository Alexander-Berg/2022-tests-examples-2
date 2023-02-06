package insights

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/gofrs/uuid"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	_insights "a.yandex-team.ru/security/impulse/api/internal/insights/mocks"
	"a.yandex-team.ru/security/impulse/api/internal/testutils"
	"a.yandex-team.ru/security/impulse/api/webhook/internal/config"
	"a.yandex-team.ru/security/impulse/api/webhook/internal/infra"
	"a.yandex-team.ru/security/impulse/models"
	"a.yandex-team.ru/security/libs/go/simplelog"
)

var cfg config.Config

func init() {
	simplelog.SetLevel(simplelog.DebugLevel)
	cfg = config.Config{
		DBConn:     os.Getenv("DB_DSN"),
		DBPassword: os.Getenv("DB_PASSWORD"),
		DBRetries:  1,
		UseAuth:    false,
		Debug:      true,
	}
}

func TestProjectInsightsController(t *testing.T) {
	testingCtx := testutils.NewTestingCtx()
	taskID := uuid.Must(uuid.NewV4()).String()
	orgID := 1
	projectID := 1
	scanID := 2
	commitHash := "aaaaa"

	testStartTime := time.Unix(1655491525, 0)
	testEndTime := time.Unix(1655491525, 0)
	testRepoPath := "/classifieds/verticals-backend"

	testingCtx.TaskRepoMock.On("GetByTaskID", context.TODO(), taskID).Return(&models.Task{
		TaskID:         taskID,
		OrganizationID: orgID,
		ProjectID:      projectID,
		Parameters: models.TaskParameters{
			"repositories": []interface{}{
				map[string]interface{}{
					"url": "https://a.yandex-team.ru/arc/trunk/arcadia" + testRepoPath,
				},
			},
		},
		StartTime:       testStartTime.Unix(),
		Status:          models.Created,
		CallbackURL:     "http://some-callback-url",
		Analysers:       models.TaskAnalysers{},
		NonTemplateScan: false,
	}, nil)

	blockerNotFalseVulnerabilitiesCount := 10
	criticalNotFalseVulnerabilitiesCount := 11
	mediumNotFalseVulnerabilitiesCount := 12
	lowNotFalseVulnerabilitiesCount := 13
	infoNotFalseVulnerabilitiesCount := 14

	testingCtx.ProjectRepoMock.On("GetStatisticsByID", context.TODO(), projectID).Return(&models.ProjectStatistics{
		BlockerNotFalseVulnerabilitiesCount:  blockerNotFalseVulnerabilitiesCount,
		CriticalNotFalseVulnerabilitiesCount: criticalNotFalseVulnerabilitiesCount,
		MediumNotFalseVulnerabilitiesCount:   mediumNotFalseVulnerabilitiesCount,
		LowNotFalseVulnerabilitiesCount:      lowNotFalseVulnerabilitiesCount,
		InfoNotFalseVulnerabilitiesCount:     infoNotFalseVulnerabilitiesCount,
	}, nil)
	currentScanInstance := &models.ScanInstance{
		ScanID:       scanID,
		TaskID:       taskID,
		RawReportURL: "",
		ReportURL:    "",
		CommitHash:   commitHash,
		StartTime:    testStartTime,
		EndTime:      testEndTime,
	}

	data, _ := json.Marshal(&models.WebhookReport{
		OrganizationID: orgID,
		ProjectID:      projectID,
		Instances:      []*models.ScanInstance{currentScanInstance},
	})

	expected := make([]models.MetricForInsights, 0)
	metricsData := map[string]int{
		"impulse_count_blocker_issues":  blockerNotFalseVulnerabilitiesCount,
		"impulse_count_critical_issues": criticalNotFalseVulnerabilitiesCount,
		"impulse_count_medium_issues":   mediumNotFalseVulnerabilitiesCount,
		"impulse_count_low_issues":      lowNotFalseVulnerabilitiesCount,
		"impulse_count_info_issues":     infoNotFalseVulnerabilitiesCount,
	}
	for name, value := range metricsData {
		expected = append(expected, models.MetricForInsights{
			Category: "security",
			Name:     name,
			Paths:    []string{testRepoPath},
			Data: []models.MetricData{{
				Timestamp:  "2022-06-17T15:45:25Z",
				CommitHash: commitHash,
				Value:      value,
			}},
		})
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/webhook/insights/export", bytes.NewReader(data))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	insightsClient := new(_insights.API)
	insightsClient.On("SendMetrics", context.TODO(), mock.MatchedBy(func(actual []models.MetricForInsights) bool {
		return assert.ElementsMatch(t, actual, expected)
	})).Return(nil)
	api := e.Group("/api/v1")
	insights := Controller{
		Infra: &infra.Infra{
			Insights: insightsClient,
			CFG:      cfg,
		},
	}
	assert.NoError(t, insights.BuildRoute(api.Group("/webhook")))
	insights.projectUsecase = testingCtx.ProjectUsecase
	insights.taskUsecase = testingCtx.TaskUsecase
	assert.NoError(t, insights.insightsExport(c))
	defer insightsClient.AssertExpectations(t)
}
