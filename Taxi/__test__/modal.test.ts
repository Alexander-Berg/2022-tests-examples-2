import {compose} from 'redux';

import {exact} from '_types/__test__/asserts';

import modal, {ModalProps} from '..';

test('Props correctly inferred', () => {
    type RequiredProps = {x: 2};
    type ExpectedProps = RequiredProps;
    const TestComponent: React.FC<RequiredProps & ModalProps> = () => null;

    const Modal = modal('modalId')(TestComponent);
    const Modal2 = compose(
        modal('modalId')
    )(TestComponent);

    exact<GetProps<typeof Modal>, ExpectedProps>(true);
    exact<GetProps<typeof Modal2>, ExpectedProps>(true);
});

test('Props correctly excluded by generic', () => {
    type ModalProps = {y: 2};
    type RequiredProps = {x: 2} & ModalProps;
    type ExpectedProps = {x: 2};
    const TestComponent: React.FC<RequiredProps & ModalProps> = () => null;

    const Modal = modal<ModalProps>('modalId')(TestComponent);
    const Modal2 = compose(
        modal<ModalProps>('modalId')
    )(TestComponent);

    exact<GetProps<typeof Modal>, ExpectedProps>(true);
    exact<GetProps<typeof Modal2>, ExpectedProps>(true);
});
