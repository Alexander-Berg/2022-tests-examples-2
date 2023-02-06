import {Form, notification, Typography} from 'antd';
import React, {useCallback, useMemo} from 'react';
import {useSelector} from 'react-redux';

import {CampaignItem} from 'bundles/campaigns/api/campaign/types';
import useAudienceConfig from 'bundles/campaigns/hooks/useAudienceConfig';
import useCampaignAbilities from 'bundles/campaigns/hooks/useCampaignAbilities';
import useTestUsers from 'bundles/campaigns/hooks/useTestUsers';
import {useCampaign, useUpdateTestUsers} from 'bundles/campaigns/queries/campaigns';
import CutLink from 'common/components/cut-link';
import {Select} from 'common/components/dir-auto';
import {routerParamsSelector} from 'common/selectors/routerParams';
import {CampaignEntity} from 'common/types/Campaign';
import {defaultErrorHandler} from 'common/utils/errors/errorHandlers';
import config from 'config';

const {Link} = Typography;

const TEST_USERS_LIMIT = 5;
const TEST_USERS_LIMIT_DESCRIPTION = `Максимальное количество тестовых пользователей – ${TEST_USERS_LIMIT}`;

const TestUsers: React.FC = () => {
    const [form] = Form.useForm();
    const {campaignId} = useSelector(routerParamsSelector);
    const {campaign} = useCampaign(Number(campaignId));
    const abilities = useCampaignAbilities(Number(campaignId));
    const updateTestUsersMutation = useUpdateTestUsers(Number(campaignId));
    const {testUsers: {usePhoneValidation}} = useAudienceConfig(campaign?.entity);
    const {
        filterOptionsFunc,
        normalizeTestUsers,
        testUsers
    } = useTestUsers(campaign?.entity);

    const extra = useMemo(() => {
        let extraInfo;

        switch (campaign?.entity) {
            case CampaignEntity.Driver:
                extraInfo = (
                    <>
                        Помимо значений в списке можно ввести значение db_id_driver_uuid своей учётки.<br/>
                        Пример: 4e0b70d03b4548ee94885e1c6d4877e8_768a0ce0597f4acf8e79e3c43c481367<br/>
                        <CutLink title="Есть учётка, не знаю свой идентификатор">
                            Уточните
                            в <Link href={config.serverConfig.support_chat_url} target="_blank">чате поддержки</Link> по
                            номеру телефона
                        </CutLink>
                        <CutLink title="Нет учётки">
                            Скачайте Яндекс.Про и зарегистрируйтесь в качестве курьера или водителя
                            (тип учётки не принципиален для тестирования), регистрация занимает меньше 2 минут.
                        </CutLink>
                    </>
                );
                break;
            case CampaignEntity.Geo:
                extraInfo = (
                    <>
                        Укажите device_id.&nbsp;
                        <Link href="https://wiki.yandex-team.ru/mlu/crm/platform/campaign-management/user-guide/questions/#10" target="_blank">Подробнее</Link>
                    </>
                );
                break;
            default:
                extraInfo = 'Укажите номера телефонов в формате +79991234567';
                break;
        }

        return (
            <>
                {TEST_USERS_LIMIT_DESCRIPTION}<br/>
                {extraInfo}
            </>
        );
    }, [campaign?.entity]);

    const handleSave = useCallback((values: Pick<CampaignItem, 'test_users'>) => {
        if (values.test_users.length > TEST_USERS_LIMIT) {
            notification.error({message: TEST_USERS_LIMIT_DESCRIPTION});
            return;
        }

        form.validateFields(['test_users'])
            .then(() => updateTestUsersMutation.mutateAsync(values.test_users))
            .then(() => notification.success({message: 'Тестовые пользователи успешно обновлены'}))
            .catch(defaultErrorHandler('Не удалось обновить тестовых пользователей'));
    }, [form, updateTestUsersMutation]);

    const disabled = !abilities.EditTestUsers;

    const rules = useMemo(() => {
        if (!campaign?.entity || !usePhoneValidation) {
            return undefined;
        }

        return [{
            validator: (rule: unknown, value: string | string[]) => {
                if (([] as string[]).concat(value).every(item => /^(\+?[1-9]\d{1,14})?$/.test(item))) {
                    return Promise.resolve();
                } else {
                    return Promise.reject(Error('Неверный формат номера телефона'));
                }
            }
        }];
    }, [campaign?.entity, usePhoneValidation]);

    const handleChange = useCallback((values: string[]) => {
        if (values.length > TEST_USERS_LIMIT) {
            form.setFieldsValue({test_users: values.slice(0, TEST_USERS_LIMIT)});
        }
    }, [form]);

    if (!campaign) {
        return null;
    }

    return (
        <Form form={form} initialValues={campaign} onValuesChange={handleSave}>
            <Form.Item
                name="test_users"
                extra={extra}
                style={{margin: 0}}
                rules={rules}
                normalize={normalizeTestUsers}
                validateTrigger={false}
            >
                <Select
                    disabled={disabled}
                    mode="tags"
                    options={testUsers}
                    loading={updateTestUsersMutation.isLoading}
                    filterOption={filterOptionsFunc}
                    tokenSeparators={[',']}
                    onChange={handleChange}
                />
            </Form.Item>
        </Form>
    );
};

export default TestUsers;
