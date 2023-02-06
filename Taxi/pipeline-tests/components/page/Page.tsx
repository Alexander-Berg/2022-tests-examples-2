import Button from 'amber-blocks/button';
import {Tab, Tabs} from 'amber-blocks/stateless-tabs';
import React, {FC, memo, useCallback} from 'react';

import AsyncContent from '_blocks/async-content';
import PageTitle from '_blocks/page-title';
import {Col, Row} from '_blocks/row';
import pageContainer from '_hocs/page-container';
import {useParams, useQuery} from '_hooks/use-query-params';
import useSaga from '_hooks/use-saga';
import {binded as commonActions} from '_infrastructure/actions';
import {Layout, LayoutContent, PageLayoutBody, PageLayoutHeader} from '_pkg/blocks/layout';
import {buildPath} from '_utils/buildPath';

import ServiceDropdown from '../../../common/components/service-dropdown';
import {LABELS, ROUTE, TABS} from '../../consts';
import {TabType} from '../../enums';
import {service as pipelineTestsService} from '../../sagas/services/PipelineTestsService';
import {queryParsers, routeParamsParsers} from '../../utils';
import EntitySidebar from '../entity-sidebar';
import PageContent from '../page-content';
import {saga} from './saga';

const handleTabChange = (tabType: TabType) => {
    pipelineTestsService.actions.navigate({tabType});
};

const Page: FC = () => {
    const {service} = useParams(routeParamsParsers);
    const {operationId} = useSaga(saga, [service]);
    const {tabType, mode} = useQuery(queryParsers);

    const handleNavigateToAlgoritmhs = useCallback(() => {
        commonActions.router.push(buildPath(ROUTE, service));
    }, [service]);

    return (
        <AsyncContent id={operationId}>
            <Layout>
                <LayoutContent>
                    <PageLayoutHeader>
                        <Row gutter="l">
                            <Col>
                                <PageTitle text={LABELS.ALGORITHM_TESTS} />
                            </Col>
                            <Col>
                                <ServiceDropdown />
                            </Col>
                            <Col>
                                <Button onClick={handleNavigateToAlgoritmhs}>{LABELS.ALGORITHMS}</Button>
                            </Col>
                        </Row>
                    </PageLayoutHeader>
                    <PageLayoutBody>
                        <Row nocols>
                            <Tabs value={tabType} onChange={handleTabChange}>
                                {TABS.map(({id, title}) => (
                                    <Tab key={id} value={id}>
                                        {title}
                                    </Tab>
                                ))}
                            </Tabs>
                        </Row>
                        {service ? <PageContent service={service} /> : LABELS.SELECT_SERVICE}
                    </PageLayoutBody>
                </LayoutContent>
            </Layout>
            {service && mode && tabType && <EntitySidebar mode={mode} tabType={tabType} />}
        </AsyncContent>
    );
};

export default pageContainer(memo(Page));
