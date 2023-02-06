package worker

import (
	"encoding/json"
	"fmt"
	"os"
	"sync"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go/service/sqs"
	"github.com/gofrs/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	_sandboxTypes "a.yandex-team.ru/security/impulse/api/internal/sandbox"
	_sandbox "a.yandex-team.ru/security/impulse/api/internal/sandbox/mocks"
	_secnotify "a.yandex-team.ru/security/impulse/api/internal/secnotify/mocks"
	"a.yandex-team.ru/security/impulse/api/internal/testutils"
	"a.yandex-team.ru/security/impulse/api/worker/internal/config"
	_infra "a.yandex-team.ru/security/impulse/api/worker/internal/infra"
	"a.yandex-team.ru/security/impulse/models"
	_queueTypes "a.yandex-team.ru/security/impulse/pkg/queue"
	_queue "a.yandex-team.ru/security/impulse/pkg/queue/mocks"
	"a.yandex-team.ru/security/libs/go/simplelog"
)

var cfg config.Config

func init() {
	simplelog.SetLevel(simplelog.DebugLevel)
	cfg = config.Config{
		DBConn:              os.Getenv("DB_DSN"),
		DBPassword:          os.Getenv("DB_PASSWORD"),
		DBRetries:           1,
		SqsEndpoint:         "https://test.yandex-team.ru",
		SqsAccount:          "sersec",
		SandboxRetryTimeout: 0,
		UseAuth:             false,
		Debug:               true,
	}
}

func TestTaskProcessorOk(t *testing.T) {
	testingCtx := testutils.NewTestingCtx()
	taskID := uuid.Must(uuid.NewV4()).String()
	orgID := 1
	projectID := 1
	sandboxTaskID := 100500

	testRepoPath := "/classifieds/verticals-backend"
	taskParams := models.TaskParameters{
		"repositories": []interface{}{
			map[string]interface{}{
				"url": "https://a.yandex-team.ru/arc/trunk/arcadia" + testRepoPath,
			},
		},
	}
	testingCtx.TaskRepoMock.On("Update", mock.AnythingOfType("*context.cancelCtx"), &models.Task{
		TaskID: taskID,
		Status: models.Pending,
	}).Return(int64(1), nil)
	testingCtx.TaskRepoMock.On("Update", mock.AnythingOfType("*context.cancelCtx"), &models.Task{
		TaskID:        taskID,
		SandboxTaskID: sandboxTaskID,
		Status:        models.Running,
	}).Return(int64(1), nil)

	queueAPI := new(_queue.Queue)
	secnotifyAPI := new(_secnotify.API)
	sandboxAPI := new(_sandbox.API)
	worker := New(_infra.Infra{
		CFG:       &cfg,
		Sandbox:   sandboxAPI,
		Secnotify: secnotifyAPI,
		Queue:     queueAPI,
	})
	assert.NoError(t, worker.onStart())
	worker.projectUsecase = testingCtx.ProjectUsecase
	worker.vulnerabilityUsecase = testingCtx.VulnerabilityUsecase
	worker.taskUsecase = testingCtx.TaskUsecase
	worker.cronUsecase = testingCtx.CronUsecase
	worker.codeQLUsecase = testingCtx.CodeQLUsecase
	taskMessage := models.TaskMessageDTO{
		OrganizationID: orgID,
		ProjectID:      projectID,
		TaskID:         taskID,
		Parameters:     taskParams,
		Analysers:      models.TaskAnalysers{},
		OnAllProjects:  false,
		Tags:           models.ProjectTags{},
	}

	handle := "testtesttesttest"
	bodyBytes, _ := json.Marshal(&taskMessage)
	body := string(bodyBytes)
	msg := sqs.Message{
		Body:          &body,
		ReceiptHandle: &handle,
	}
	queueAPI.On("DeleteMessage", &_queueTypes.DeleteOptions{
		QueueURL:      "https://test.yandex-team.ru/sersec/tasks",
		ReceiptHandle: msg.ReceiptHandle,
	}).Return(nil)
	defer queueAPI.AssertExpectations(t)
	defer sandboxAPI.AssertExpectations(t)
	defer testingCtx.TaskRepoMock.AssertExpectations(t)

	sandboxAPI.On("CreateTask", &taskMessage, true).Return(sandboxTaskID, nil)
	sandboxAPI.On("StartTask", sandboxTaskID).Return(nil)

	messages := make(chan *sqs.Message)
	wg := sync.WaitGroup{}
	go worker.taskProcessor(&wg, messages)
	messages <- &msg
	close(messages)
	wg.Wait()

}

func TestTaskProcessorStartSandboxTaskError(t *testing.T) {
	testingCtx := testutils.NewTestingCtx()
	taskID := uuid.Must(uuid.NewV4()).String()
	orgID := 1
	projectID := 1
	sandboxTaskID := 100500

	testRepoPath := "/classifieds/verticals-backend"
	taskParams := models.TaskParameters{
		"repositories": []interface{}{
			map[string]interface{}{
				"url": "https://a.yandex-team.ru/arc/trunk/arcadia" + testRepoPath,
			},
		},
	}
	testingCtx.TaskRepoMock.On("Update", mock.AnythingOfType("*context.cancelCtx"), &models.Task{
		TaskID: taskID,
		Status: models.Pending,
	}).Return(int64(1), nil)
	testingCtx.TaskRepoMock.On("Update", mock.AnythingOfType("*context.cancelCtx"), &models.Task{
		TaskID:        taskID,
		SandboxTaskID: sandboxTaskID,
		Status:        models.Failed,
	}).Return(int64(1), nil)

	queueAPI := new(_queue.Queue)
	secnotifyAPI := new(_secnotify.API)
	sandboxAPI := new(_sandbox.API)
	worker := New(_infra.Infra{
		CFG:       &cfg,
		Sandbox:   sandboxAPI,
		Secnotify: secnotifyAPI,
		Queue:     queueAPI,
	})
	assert.NoError(t, worker.onStart())
	worker.projectUsecase = testingCtx.ProjectUsecase
	worker.vulnerabilityUsecase = testingCtx.VulnerabilityUsecase
	worker.taskUsecase = testingCtx.TaskUsecase
	worker.cronUsecase = testingCtx.CronUsecase
	worker.codeQLUsecase = testingCtx.CodeQLUsecase
	taskMessage := models.TaskMessageDTO{
		OrganizationID: orgID,
		ProjectID:      projectID,
		TaskID:         taskID,
		Parameters:     taskParams,
		Analysers:      models.TaskAnalysers{},
		OnAllProjects:  false,
		Tags:           models.ProjectTags{},
	}

	handle := "testtesttesttest"
	bodyBytes, _ := json.Marshal(&taskMessage)
	body := string(bodyBytes)
	msg := sqs.Message{
		Body:          &body,
		ReceiptHandle: &handle,
	}
	queueAPI.On("DeleteMessage", &_queueTypes.DeleteOptions{
		QueueURL:      "https://test.yandex-team.ru/sersec/tasks",
		ReceiptHandle: msg.ReceiptHandle,
	}).Return(nil)
	defer queueAPI.AssertExpectations(t)
	defer sandboxAPI.AssertExpectations(t)
	defer testingCtx.TaskRepoMock.AssertExpectations(t)

	sandboxAPI.On("CreateTask", &taskMessage, true).Return(sandboxTaskID, nil)
	sandboxAPI.On("StartTask", sandboxTaskID).Return(fmt.Errorf("unknown error"))

	messages := make(chan *sqs.Message)
	wg := sync.WaitGroup{}
	go worker.taskProcessor(&wg, messages)
	messages <- &msg
	close(messages)
	wg.Wait()
}

func TestTaskProcessorTooManyRequests(t *testing.T) {
	testingCtx := testutils.NewTestingCtx()
	taskID := uuid.Must(uuid.NewV4()).String()
	orgID := 1
	projectID := 1
	sandboxTaskID := 100500

	testRepoPath := "/classifieds/verticals-backend"
	taskParams := models.TaskParameters{
		"repositories": []interface{}{
			map[string]interface{}{
				"url": "https://a.yandex-team.ru/arc/trunk/arcadia" + testRepoPath,
			},
		},
	}
	testingCtx.TaskRepoMock.On("Update", mock.AnythingOfType("*context.cancelCtx"), &models.Task{
		TaskID: taskID,
		Status: models.Pending,
	}).Return(int64(1), nil)
	testingCtx.TaskRepoMock.On("Update", mock.AnythingOfType("*context.cancelCtx"), &models.Task{
		TaskID:        taskID,
		SandboxTaskID: sandboxTaskID,
		Status:        models.Failed,
	}).Return(int64(1), nil)
	testingCtx.TaskRepoMock.On("Update", mock.AnythingOfType("*context.cancelCtx"), &models.Task{
		TaskID:        taskID,
		SandboxTaskID: sandboxTaskID,
		Status:        models.Running,
	}).Return(int64(1), nil)

	queueAPI := new(_queue.Queue)
	secnotifyAPI := new(_secnotify.API)
	sandboxAPI := new(_sandbox.API)
	worker := New(_infra.Infra{
		CFG:       &cfg,
		Sandbox:   sandboxAPI,
		Secnotify: secnotifyAPI,
		Queue:     queueAPI,
	})
	assert.NoError(t, worker.onStart())
	worker.projectUsecase = testingCtx.ProjectUsecase
	worker.vulnerabilityUsecase = testingCtx.VulnerabilityUsecase
	worker.taskUsecase = testingCtx.TaskUsecase
	worker.cronUsecase = testingCtx.CronUsecase
	worker.codeQLUsecase = testingCtx.CodeQLUsecase
	taskMessage := models.TaskMessageDTO{
		OrganizationID: orgID,
		ProjectID:      projectID,
		TaskID:         taskID,
		Parameters:     taskParams,
		Analysers:      models.TaskAnalysers{},
		OnAllProjects:  false,
		Tags:           models.ProjectTags{},
	}

	handle := "testtesttesttest"
	bodyBytes, _ := json.Marshal(&taskMessage)
	body := string(bodyBytes)
	msg := sqs.Message{
		Body:          &body,
		ReceiptHandle: &handle,
	}
	queueAPI.On("DeleteMessage", &_queueTypes.DeleteOptions{
		QueueURL:      "https://test.yandex-team.ru/sersec/tasks",
		ReceiptHandle: msg.ReceiptHandle,
	}).Return(nil)
	defer queueAPI.AssertExpectations(t)
	defer sandboxAPI.AssertExpectations(t)
	defer testingCtx.TaskRepoMock.AssertExpectations(t)

	sandboxAPI.On("CreateTask", &taskMessage, true).Return(sandboxTaskID, nil)
	sandboxAPI.On("StartTask", sandboxTaskID).Return(_sandboxTypes.TooManyRequests{}).Once()
	sandboxAPI.On("StartTask", sandboxTaskID).Return(nil)

	messages := make(chan *sqs.Message)
	wg := sync.WaitGroup{}
	go worker.taskProcessor(&wg, messages)
	messages <- &msg
	messages <- &msg
	close(messages)
	wg.Wait()
}

func TestTaskProcessorOrganizationScan(t *testing.T) {
	testingCtx := testutils.NewTestingCtx()
	taskID := uuid.Must(uuid.NewV4()).String()
	orgID := 1
	projectID1 := 1
	projectID2 := 2
	projectID3 := 3
	testRepoPath := "/classifieds/verticals-backend"
	taskParams := models.TaskParameters{
		"repositories": []interface{}{
			map[string]interface{}{
				"url": "https://a.yandex-team.ru/arc/trunk/arcadia" + testRepoPath,
			},
		},
	}

	loc, _ := time.LoadLocation("Europe/Moscow")
	testStartTime := time.Unix(1654511288, 0).In(loc)
	task := models.Task{
		TaskID:          taskID,
		OrganizationID:  orgID,
		ProjectID:       projectID1,
		Parameters:      taskParams,
		StartTime:       testStartTime.Unix(),
		Status:          models.Created,
		CallbackURL:     "http://some-callback-url",
		Analysers:       models.TaskAnalysers{},
		NonTemplateScan: false,
	}
	testingCtx.ProjectRepoMock.On("ListByOrganizationID", mock.AnythingOfType("*context.cancelCtx"), orgID).Return([]*models.ProjectInfo{
		{
			Project: models.Project{
				ID:             projectID1,
				Name:           "Test Project 1",
				Slug:           "test_proj_1",
				OrganizationID: task.OrganizationID,
				Tags:           models.ProjectTags{"Java"},
			},
		},
		{
			Project: models.Project{
				ID:             projectID2,
				Name:           "Test Project 2",
				Slug:           "test_proj_2",
				OrganizationID: task.OrganizationID,
				Tags:           models.ProjectTags{"Scala"},
			},
		},
		{
			Project: models.Project{
				ID:             projectID3,
				Name:           "Test Project 3",
				Slug:           "test_proj_3",
				OrganizationID: task.OrganizationID,
				Tags:           models.ProjectTags{"Scala", "Go"},
			},
		},
	}, nil)
	taskMessage := models.TaskMessageDTO{
		OrganizationID: orgID,
		Parameters:     taskParams,
		Analysers:      models.TaskAnalysers{"yadi_scan", "semgrep_scan"},
		OnAllProjects:  true,
		Tags:           models.ProjectTags{"Scala", "Go"},
	}
	for _, pID := range []int{projectID2, projectID3} {
		testingCtx.TaskRepoMock.On("GetLastTemplate", mock.AnythingOfType("*context.cancelCtx"), pID).Return(&models.TaskResponseDTO{
			Task: models.Task{
				OrganizationID:  orgID,
				ProjectID:       pID,
				Parameters:      taskParams,
				NonTemplateScan: false,
			},
		}, nil)
		testingCtx.TaskRepoMock.On("Create", mock.AnythingOfType("*context.cancelCtx"), mock.MatchedBy(func(actual *models.Task) bool {
			return assert.Equal(t, orgID, actual.OrganizationID) &&
				assert.Contains(t, []int{projectID2, projectID3}, actual.ProjectID) &&
				assert.Equal(t, taskParams, actual.Parameters) &&
				assert.Equal(t, taskMessage.Analysers, actual.Analysers)
		})).Return(nil).Once()
	}

	queueAPI := new(_queue.Queue)
	secnotifyAPI := new(_secnotify.API)
	sandboxAPI := new(_sandbox.API)
	worker := New(_infra.Infra{
		CFG:       &cfg,
		Sandbox:   sandboxAPI,
		Secnotify: secnotifyAPI,
		Queue:     queueAPI,
	})
	assert.NoError(t, worker.onStart())
	worker.projectUsecase = testingCtx.ProjectUsecase
	worker.vulnerabilityUsecase = testingCtx.VulnerabilityUsecase
	worker.taskUsecase = testingCtx.TaskUsecase
	worker.cronUsecase = testingCtx.CronUsecase
	worker.codeQLUsecase = testingCtx.CodeQLUsecase

	handle := "testtesttesttest"
	bodyBytes, _ := json.Marshal(&taskMessage)
	body := string(bodyBytes)
	msg := sqs.Message{
		Body:          &body,
		ReceiptHandle: &handle,
	}
	queueAPI.On("DeleteMessage", &_queueTypes.DeleteOptions{
		QueueURL:      "https://test.yandex-team.ru/sersec/tasks",
		ReceiptHandle: msg.ReceiptHandle,
	}).Return(nil)
	defer queueAPI.AssertExpectations(t)
	defer sandboxAPI.AssertExpectations(t)
	defer testingCtx.TaskRepoMock.AssertExpectations(t)
	defer testingCtx.ProjectRepoMock.AssertExpectations(t)

	queueAPI.On("DeleteMessage", &_queueTypes.DeleteOptions{
		QueueURL:      "https://test.yandex-team.ru/sersec/tasks",
		ReceiptHandle: msg.ReceiptHandle,
	}).Return(nil)
	expectedParams := models.TaskParameters{
		"repositories": []interface{}{
			map[string]interface{}{
				"branch": "", "path": "",
				"revision": "",
				"url":      "svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/classifieds/verticals-backend",
			},
		},
	}
	queueAPI.On("SendMessage", mock.MatchedBy(func(actual *_queueTypes.SendOptions) bool {
		payload := models.TaskMessageDTO{}
		return assert.NoError(t, json.Unmarshal([]byte(actual.Msg), &payload)) &&
			assert.Equal(t, payload.OrganizationID, task.OrganizationID) &&
			assert.Contains(t, []int{projectID1, projectID2, projectID3}, payload.ProjectID) &&
			assert.Equal(t, payload.Parameters, expectedParams)
	})).Return("", nil)

	messages := make(chan *sqs.Message)
	wg := sync.WaitGroup{}
	go worker.taskProcessor(&wg, messages)
	messages <- &msg
	close(messages)
	wg.Wait()
}
