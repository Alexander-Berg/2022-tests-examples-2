import React from 'react';
import {configureI18n} from '_common/static/utils/i18n';
import tjson from '../.storybook/addon-config/tjson.json';
import moment from 'moment';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

Enzyme.configure({adapter: new Adapter()});

global.React = React;
global.i18n = configureI18n('ru', tjson, 'taxi-frontend');

moment.locale('ru');
