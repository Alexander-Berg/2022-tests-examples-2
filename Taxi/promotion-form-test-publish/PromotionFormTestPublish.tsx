import {Button} from 'amber-blocks';
import React, {useCallback, useEffect} from 'react';
import {useSelector} from 'react-redux';

import {AmberField, classNames} from '_blocks/form';
import {FormLayoutGroup, FormLayoutSimple} from '_blocks/form-layout';
import {Col, Row} from '_blocks/row';
import {useIsFormDisabled} from '_hooks/use-is-form-disabled';
import {binded as commonActions} from '_infrastructure/actions';
import i18n from '_utils/localization/i18n';

import {getPromotionType, getPublishPhones} from '../../selectors';
import {PromotionType} from '../../types';
import {promotionPath as path} from '../../utils';

interface Props {
    number: number;
    model: string;
    disabled: boolean;
}

const Phone: React.FC<Props> = ({model, disabled, number}) => {
    const phones = useSelector(getPublishPhones);
    const handleRemove = useCallback(() => {
        commonActions.form.change(
            path(m => m.$view.phones),
            [...phones.slice(0, number), ...phones.slice(number + 1)]
        );
    }, [phones, number]);

    return (
        <Row>
            <Col>
                <AmberField.text placeholder="+7xxxxxxxxxx" model={model} className={classNames.field250} />
            </Col>
            <Col>
                <Button disabled={disabled} onClick={handleRemove}>
                    {i18n.print('remove')}
                </Button>
            </Col>
        </Row>
    );
};

const PromotionFormTestPublish = () => {
    const phones = useSelector(getPublishPhones);
    const promotionType = useSelector(getPromotionType);
    const isDisabled = useIsFormDisabled();
    const isPromoOnMap = promotionType === PromotionType.PromoOnMap;
    const isShowcase = promotionType === PromotionType.Showcase;

    const hasPhones = !!phones?.length;

    useEffect(() => {
        if (!hasPhones) {
            commonActions.form.change(
                path(m => m.$view.phones),
                ['']
            );
        }
    }, [hasPhones]);

    const handleAddPhone = useCallback(() => {
        commonActions.form.change(
            path(m => m.$view.phones),
            [...phones, '']
        );
    }, [phones]);

    return (
        <FormLayoutGroup title={i18n.print('promotions_test_publish_phone_numbers')}>
            {hasPhones &&
                phones.map((phone, i) => (
                    <Phone disabled={isDisabled} key={i} number={i} model={path(m => m.$view.phones[i])} />
                ))}
            <Button disabled={isDisabled} onClick={handleAddPhone}>
                {i18n.print('promotions_add_a_phone_number')}
            </Button>
            {!isPromoOnMap && !isShowcase &&
                <FormLayoutSimple label={i18n.print('promotion_link_to_yql_task')}>
                    <AmberField.text className={classNames.field250} model={path(m => m.yql_data.link)}/>
                </FormLayoutSimple>
            }
        </FormLayoutGroup>
    );
};

export default React.memo(PromotionFormTestPublish);
