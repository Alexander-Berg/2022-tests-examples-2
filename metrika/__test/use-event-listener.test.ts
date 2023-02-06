import '@testing-library/jest-dom/extend-expect';
import { renderHook } from '@testing-library/react-hooks';
import { useEventListener } from '@client-libs/react-utils/use-event-listener/use-event-listener';
import userEvent from '@testing-library/user-event';

const onClick = jest.fn();

describe('useEventListener', () => {
    beforeEach(() => {
        renderHook(() => useEventListener({
            eventName: 'click',
            handler: onClick,
            elem: document
        }));
    });

    afterEach(() => {
        onClick.mockClear();
    });

    it('should call event handler', () => {
        userEvent.click(document.body);
        expect(onClick).toBeCalled();
    });

    it('shouldn`t call event handler', () => {
        expect(onClick).not.toBeCalled();
    });
});
