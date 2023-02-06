import { execView } from '@lib/views/execView';
import { HomeLink2 } from '@block/home-link2/home-link2.view';

export function simple() {
    return (
        <div class="root" style="display: inline-block">
            <div>
                {execView(HomeLink2, {
                    mods: {
                        color: 'inherit'
                    },
                    content: 'link'
                })}
            </div>
        </div>
    );
}
