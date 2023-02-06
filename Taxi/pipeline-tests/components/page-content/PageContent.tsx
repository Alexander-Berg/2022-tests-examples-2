import {Button} from 'amber-blocks';
import Plus from 'amber-blocks/icon/Plus';
import React, {FC, Fragment, memo, useCallback} from 'react';

import {Row} from '_blocks/row';
import useOperation from '_hooks/use-operation';
import {useQuery} from '_hooks/use-query-params';
import useSaga from '_hooks/use-saga';

import {CREATE_BUTTON_TITLES} from '../../consts';
import {FormMode, TabType} from '../../enums';
import {service as entityService} from '../../sagas/services/EntityService';
import PipelineTestsService, {service as pipelineTestsService} from '../../sagas/services/PipelineTestsService';
import {queryParsers} from '../../utils';
import EntityList from '../entity-list';
import {renderCheckItem, renderMockItem, renderTestItem} from '../entity-list/utils';
import {saga} from './saga';

import {b} from './PageContent.styl';

type Props = {
    service: string;
};

const REQUEST_MOCK_LIST_ID = PipelineTestsService.requestMockList.id!;
const REQUEST_CHECK_LIST_ID = PipelineTestsService.requestCheckList.id!;
const REQUEST_TEST_LIST_ID = PipelineTestsService.requestTestList.id!;

const PLUS_ICON = <Plus />;

const openCreateModal = () => {
    pipelineTestsService.actions.navigate({
        mode: FormMode.Create,
    });
};

const openViewModal = (id: string) => {
    pipelineTestsService.actions.navigate({
        mode: FormMode.View,
        id,
    });
};

const PageContent: FC<Props> = ({service}) => {
    const {tabType} = useQuery(queryParsers);

    useSaga(saga, [service, tabType]);

    const {result: mockList = []} = useOperation({operationId: REQUEST_MOCK_LIST_ID});
    const {result: checkList = []} = useOperation({operationId: REQUEST_CHECK_LIST_ID});
    const {result: testList = []} = useOperation({operationId: REQUEST_TEST_LIST_ID});

    const removeEntityItem = useCallback(
        (id: string) => {
            entityService.actions.removeEntity(tabType, id);
        },
        [tabType],
    );

    const buttonTitle = CREATE_BUTTON_TITLES[tabType] ?? tabType;

    return (
        <Fragment>
            <Row className={b('headRow')}>
                <Button className={b('plusButton')} iconStart={PLUS_ICON} onClick={openCreateModal}>
                    {buttonTitle}
                </Button>
            </Row>
            {tabType === TabType.Mock && (
                <EntityList
                    items={mockList}
                    renderItem={renderMockItem}
                    onRemove={removeEntityItem}
                    onRowClick={openViewModal}
                />
            )}
            {tabType === TabType.Check && (
                <EntityList
                    items={checkList}
                    renderItem={renderCheckItem}
                    onRemove={removeEntityItem}
                    onRowClick={openViewModal}
                />
            )}
            {tabType === TabType.Test && (
                <EntityList
                    items={testList}
                    renderItem={renderTestItem}
                    onRemove={removeEntityItem}
                    onRowClick={openViewModal}
                />
            )}
        </Fragment>
    );
};

export default memo(PageContent);
