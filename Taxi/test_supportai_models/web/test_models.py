import pytest


# pylint: disable=C0103
pytestmark = [pytest.mark.pgsql('supportai_models', files=['models.sql'])]


@pytest.mark.set_worker(worker_id=1)
@pytest.mark.download_ml_resource(attrs={'type': 'detmir_dialog'})
async def test_one_message_model_v2(web_app_client):

    response_v2 = await web_app_client.post(
        f'/internal/supportai-models/v2/apply/text_classify'
        '?model_id=detmir_dialog&model_version=5',
        json={
            'chat_id': '12334567890',
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Какой статус у моего заказа?'},
                ],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )
    assert response_v2.status == 200

    content_v2 = await response_v2.json()

    assert ('most_probable_topic' in content_v2) and (
        content_v2['most_probable_topic'] is not None
    )


@pytest.mark.set_worker(worker_id=2)
@pytest.mark.download_ml_resource(attrs={'type': 'taxi_client_dialog'})
async def test_united_message_model(web_app_client):
    response = await web_app_client.post(
        f'/internal/supportai-models/v2/apply/text_classify'
        '?model_id=taxi_client_dialog&model_version=1',
        json={
            'chat_id': '12334567890',
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Какой статус у моего заказа?'},
                ],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )

    assert response.status == 200

    content = await response.json()
    assert ('most_probable_topic' in content) and (
        content['most_probable_topic'] is not None
    )


@pytest.mark.set_worker(worker_id=5)
@pytest.mark.download_ml_resource(attrs={'type': 'ya_drive_dialog'})
async def test_dialog_model(web_app_client):

    response = await web_app_client.post(
        f'/internal/supportai-models/v2/apply/text_classify'
        '?model_id=ya_drive_dialog&model_version=1',
        json={
            'chat_id': '12334567890',
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Машина попала в аварию'},
                ],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )
    assert response.status == 200
    content = await response.json()

    assert ('most_probable_topic' in content) and (
        content['most_probable_topic'] is not None
    )


@pytest.mark.set_worker(worker_id=4)
@pytest.mark.download_ml_resource(attrs={'type': 'justschool_dialog'})
async def test_knn_model(web_app_client):
    response = await web_app_client.post(
        f'/internal/supportai-models/v2/apply/text_classify'
        '?model_id=justschool_dialog&model_version=1',
        json={
            'chat_id': '12334567890',
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Отмените занятие на завтра'},
                ],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert ('most_probable_topic' in content) and (
        content['most_probable_topic'] is not None
    )


@pytest.mark.set_worker(worker_id=3)
@pytest.mark.download_ml_resource(
    attrs={'type': 'russian_post_b2b_orders_dialog'},
)
async def test_label_based_on_one_message_model(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models/v2/apply/text_classify?model_id='
        'russian_post_b2b_orders_dialog&model_version=1',
        json={
            'chat_id': '12334567890',
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Что с моей посылкой?'},
                ],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert ('most_probable_topic' in content) and (
        content['most_probable_topic'] is not None
    )


@pytest.mark.set_worker(worker_id=6)
@pytest.mark.download_ml_resource(attrs={'type': 'genotek_dialog'})
async def test_sentence_bert_one_message(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models/v2/apply/text_classify?model_id='
        'genotek_dialog&model_version=1',
        json={
            'chat_id': '12332112345312',
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'Сколько стоит генетический паспорт?',
                    },
                ],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert ('most_probable_topic' in content) and (
        content['most_probable_topic'] is not None
    )


@pytest.mark.set_worker(worker_id=7)
@pytest.mark.download_ml_resource(attrs={'type': 'dialog_act_hello'})
async def test_bert_binary_clf_v2(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models/v2/apply/multihead_text_classify?model_id='
        'dialog_act_hello&model_version=1',
        json={
            'chat_id': '12332112345312',
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Привет! У меня есть вопрос'},
                ],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )
    assert response.status == 200
    content = await response.json()
    outputs = content['result']
    assert len(outputs) == 1
    assert outputs[0]['slug'] == 'greeting'
    assert set(item['slug'] for item in outputs[0]['probabilities']) == {
        'yes',
        'no',
    }


@pytest.mark.set_worker(worker_id=10)
@pytest.mark.download_ml_resource(attrs={'type': 'sentiment'})
async def test_sentiment_clf_model(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models/v2/apply/multihead_text_classify?model_id='
        'sentiment&model_version=1',
        json={
            'chat_id': '12332112345312',
            'dialog': {
                'messages': [{'author': 'user', 'text': 'огогошеньки'}],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert 'result' in content
    print(content['result'])
    assert len(content['result']) == 1
    assert len(content['result'][0]['probabilities']) == 5


@pytest.mark.set_worker(worker_id=9)
@pytest.mark.download_ml_resource(attrs={'type': 'useresponse_search'})
async def test_qa_model(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models/v2/apply/text_classify?model_id='
        'useresponse_search&model_version=1',
        json={
            'chat_id': '12332112345312',
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Привет! У меня есть вопрос'},
                ],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert ('most_probable_topic' in content) and (
        content['most_probable_topic'] is not None
    )


@pytest.mark.set_worker(worker_id=8)
@pytest.mark.download_ml_resource(attrs={'type': 'genotek_dialog'})
async def test_s3_model(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models/v2/apply/text_classify?model_id='
        'genotek_dialog&model_version=2',
        json={
            'chat_id': '12332112345312',
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'Сколько стоит генетический паспорт?',
                    },
                ],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert ('most_probable_topic' in content) and (
        content['most_probable_topic'] is not None
    )


@pytest.mark.set_worker(worker_id=11)
@pytest.mark.download_ml_resource(attrs={'type': 'sbert_embedder'})
async def test_sbert_embedder_v2(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models/v2/apply/text_embed?model_id='
        'sbert_embedder&model_version=1',
        json={
            'chat_id': '12332112345312',
            'dialog': {
                'messages': [
                    {
                        'author': 'user',
                        'text': 'Сколько стоит генетический паспорт?',
                    },
                ],
            },
            'features': [],
        },
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/internal/supportai-models/v1/text_embed/bulk?model_id='
        'sbert_embedder&model_version=1',
        json={'texts': ['Текст 1', 'Текст 2', 'Текст 3', 'Текст 4']},
    )
    assert response.status == 200
    content = await response.json()

    assert len(content['embeddings']) == 4


@pytest.mark.set_worker(worker_id=1)
@pytest.mark.download_ml_resource(attrs={'type': 'detmir_dialog'})
async def test_united_handle(web_app_client):
    response = await web_app_client.post(
        f'/internal/supportai-models/v2/apply/text_classify'
        '?model_id=detmir_dialog&model_version=5',
        json={
            'chat_id': '12334567890',
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'Какой статус у моего заказа?'},
                ],
            },
            'features': [{'key': 'param', 'value': 1}],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert ('most_probable_topic' in content) and (
        content['most_probable_topic'] is not None
    )
