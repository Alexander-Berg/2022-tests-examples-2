import React, {memo, ReactNode} from 'react';

import {Row} from '_blocks/row';

import EntityItem from './EntityItem';
import {EntityItemType} from './types';

type Props<T extends EntityItemType> = {
    items: T[];
    renderItem: (item: T) => ReactNode;
    isDarkRow?: boolean;
    onRemove: (id: string) => void;
    onRowClick: (id: string) => void;
};

const EntityList = function<T extends EntityItemType>({items, renderItem, isDarkRow, onRemove, onRowClick}: Props<T>) {
    return (
        <Row verticalAlign="center" gap="no" nocols>
            {items.map(item => (
                <EntityItem
                    key={item.id}
                    item={item}
                    renderItem={renderItem}
                    onRemove={onRemove}
                    onRowClick={onRowClick}
                    isDarkRow={isDarkRow}
                />
            ))}
        </Row>
    );
};

export default memo(EntityList);
