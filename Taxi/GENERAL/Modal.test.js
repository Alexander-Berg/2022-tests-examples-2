import React from 'react';
import { shallow } from 'enzyme';
import toJson from 'enzyme-to-json';

import Modal from './Modal';

test('Modal does not crash', () => {
  const mockFunction = jest.fn();

  const tree = shallow(
    <Modal closeModal={mockFunction}>
      content
    </Modal>
  );

  expect(toJson(tree)).toMatchSnapshot();
});
