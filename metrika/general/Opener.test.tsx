import * as React from 'react';
import { shallow } from 'enzyme';
import { Opener, OpenerInjectedProps } from './Opener';

describe('Opener', () => {
    class OpenerContent extends React.Component<OpenerInjectedProps> {
        render() {
            return <div>hello world</div>;
        }
    }

    describe('при первом рендере', () => {
        it('по умолчанию закрыт', () => {
            const wrapper = shallow(
                <Opener>{(props) => <OpenerContent {...props} />}</Opener>,
            );
            expect(wrapper).toMatchSnapshot();
        });

        it('закрыт через isOpened=false', () => {
            const wrapper = shallow(
                <Opener isOpened={false}>
                    {(props) => <OpenerContent {...props} />}
                </Opener>,
            );
            expect(wrapper).toMatchSnapshot();
        });

        it('открыт через isOpened', () => {
            const wrapper = shallow(
                <Opener isOpened>
                    {(props) => <OpenerContent {...props} />}
                </Opener>,
            );
            expect(wrapper).toMatchSnapshot();
        });
    });

    describe('меняет состояние через коллбеки - ', () => {
        it('открывается', () => {
            const wrapper = shallow(
                <Opener>{(props) => <OpenerContent {...props} />}</Opener>,
            );
            wrapper.find(OpenerContent).prop('open')();
            wrapper.update();
            expect(wrapper).toMatchSnapshot();
        });
        it('открывается и закрывается', () => {
            const wrapper = shallow(
                <Opener>{(props) => <OpenerContent {...props} />}</Opener>,
            );
            wrapper.find(OpenerContent).prop('open')();
            wrapper.update();
            wrapper.find(OpenerContent).prop('close')();
            wrapper.update();
            expect(wrapper).toMatchSnapshot();
        });
    });
});
