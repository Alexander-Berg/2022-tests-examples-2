import {Button} from 'amber-blocks';
import Trash from 'amber-blocks/icon/Trash';
import React, {memo, ReactNode, SyntheticEvent, useCallback, useMemo} from 'react';

import {Col, Row} from '_blocks/row';
import {useIsFormDisabled} from '_hooks/use-is-form-disabled';

import {EntityItemType} from './types';

import {b} from './EntityItem.styl';

type Props<T extends EntityItemType> = {
    item: T;
    isDarkRow?: boolean;
    renderItem: (item: T) => ReactNode;
    onRemove: (id: string) => void;
    onRowClick: (id: string) => void;
};

const TRASH_ICON = <Trash />;

const EntityItem = function<T extends EntityItemType>({item, renderItem, isDarkRow, onRemove, onRowClick}: Props<T>) {
    const disabled = useIsFormDisabled();

    const renderedItem = useMemo(() => renderItem(item), [renderItem, item]);

    const handleRemove = useCallback(
        (event: SyntheticEvent) => {
            event.stopPropagation();
            onRemove(item.id);
        },
        [onRemove, item.id],
    );

    const handleRowClick = useCallback(() => {
        onRowClick(item.id);
    }, [onRowClick, item.id]);

    return (
        <Row verticalAlign="center" gap="xs" key={item.id} onClick={handleRowClick} className={b('row', {isDarkRow})}>
            <Col stretch>{renderedItem}</Col>
            {!disabled && (
                <Col>
                    <Button icon={TRASH_ICON} onClick={handleRemove} />
                </Col>
            )}
        </Row>
    );
};

export default memo(EntityItem);
