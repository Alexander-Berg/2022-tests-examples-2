import React, { useState } from 'react';
import { useStyles } from './styles';
import { Button, Input } from 'antd';
import { Col, Row } from 'antd';
import { push } from '../../utils/ev';
import useSubscribe from '../../utils/useSubscribe';
import { useTranslation } from 'react-i18next';

const TestEvent = () => {
	const [t] = useTranslation();
	const [data, setData] = useState('');
	const classes = useStyles({});

	const [eventData, setEventData] = useState('');
	const [eventText, setEventText] = useState('');
	const [isInit, setInit] = useState(false);

	const pushEvent = () => {
		push([
			{
				data: {
					testData: data,
				},
				key: ['test', 'event', '123'],
			},
		]);
	};

	const eventsHandler = (data, code) => {
		setEventData(JSON.stringify(data, null, ' '));
		if (code === 'INIT') {
			setInit(true);
		}
		data.data.forEach((data) => {
			setEventText(data.testData);
		});
	};

	useSubscribe({
		key: ['test', 'event', '123'],
		cb: eventsHandler,
	});

	return (
		<Row justify="center">
			<Col span={6} data-test="test event page">
				<div className={classes.paper}>
					<h4>Is init:</h4>
					<p data-test="test event init">{isInit ? 'INIT' : 'NOT INIT'}</p>
					<h4>Event text:</h4>
					<p data-test="test event data view">{eventText}</p>
					<h4>Event data:</h4>
					<p>{eventData}</p>
					<Input.TextArea
						id="outlined-multiline-static"
						value={data}
						data-test="test event data input"
						rows={6}
						onChange={(event) => setData(event.target.value)}
					/>
					<Button
						color="primary"
						onClick={pushEvent}
						data-test="test event push btn"
					>
						{t('Отправить событие')}
					</Button>
				</div>
			</Col>
		</Row>
	);
};

export default TestEvent;
