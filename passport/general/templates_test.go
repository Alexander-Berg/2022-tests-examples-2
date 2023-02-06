package mysql

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

var templatesList = []*model.Template{
	{
		ID:                "4",
		Text:              "I see a {{name}} and code {{code}}",
		AbcService:        "passport_infra",
		SenderMeta:        "{\"whatsapp\": {\"id\": 1111}}",
		FieldsDescription: "{\"code\": {\"privacy\": \"secret\"}}",
	},
	{
		ID:         "8",
		Text:       "New {{service}} init",
		AbcService: "passport_infra",
		SenderMeta: "{\"whatsapp\": {\"id\": 2222}}",
	},
}

func TestMySQLProvider_GetTemplatesCount(t *testing.T) {
	provider, _ := initProvider()
	count, err := provider.GetTemplatesCount(context.Background(), nil)
	require.NoError(t, err)
	require.Equal(t, uint64(2), count)
}

func TestMySQLProvider_GetTemplates_All(t *testing.T) {
	provider, _ := initProvider()
	templates, err := provider.GetTemplates(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	require.Equal(t, templatesList, templates)
}

func TestMySQLProvider_GetTemplates_CheckPages(t *testing.T) {
	provider, _ := initProvider()

	templates, err := provider.GetTemplates(context.Background(), "0", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.Template{
		templatesList[0],
	}, templates)

	templates, err = provider.GetTemplates(context.Background(), "4", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.Template{
		templatesList[1],
	}, templates)

	templates, err = provider.GetTemplates(context.Background(), "8", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.Template{}, templates)
}

func TestMySQLProvider_CreateTemplates(t *testing.T) {
	provider, _ := initProvider()
	newTemplate := &model.Template{
		Text:              "New template {{phone}}",
		AbcService:        "12345",
		SenderMeta:        "{\"whatsapp\": {\"id\": 8888}}",
		FieldsDescription: "{\"phone\": {\"privacy\": \"secret\"}}",
	}
	err := provider.SetTemplates(context.Background(), []*model.Template{newTemplate}, nil, nil)
	require.NoError(t, err)

	templates, err := provider.GetTemplates(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	newTemplate.ID = "9"
	require.Equal(t, []*model.Template{
		templatesList[0],
		templatesList[1],
		newTemplate,
	}, templates)
}

func TestMySQLProvider_UpdateTemplates(t *testing.T) {
	provider, _ := initProvider()
	newTemplate := &model.Template{
		ID:                "1000",
		Text:              "New template {{phone}}",
		AbcService:        "12345",
		SenderMeta:        "{\"whatsapp\": {\"id\": 8888}}",
		FieldsDescription: "{\"phone\": {\"privacy\": \"secret\"}}",
	}
	err := provider.SetTemplates(context.Background(), nil, []*model.Template{newTemplate}, nil)
	require.Error(t, err)
	templates, err := provider.GetTemplates(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	require.Equal(t, templatesList, templates)

	newTemplate.ID = "4"
	err = provider.SetTemplates(context.Background(), nil, []*model.Template{newTemplate}, nil)
	require.NoError(t, err)
	templates, err = provider.GetTemplates(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	updated := newTemplate
	updated.Text = templatesList[0].Text
	require.Equal(t, []*model.Template{
		updated,
		templatesList[1],
	}, templates)
}
