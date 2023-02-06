// import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../utils/navigation/navigation_manager.dart';

class UserAvatarButton extends ConsumerWidget {
  const UserAvatarButton({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = YXTheme.of<YXThemeData>(context);
    const imageUrl =
        'https://sun9-47.userapi.com/impg/mWmFrvQaa3UQ_DcrvBtiWkekx-d3kM0sP6_Elw/ENWamKih9z8.jpg?size=2560x1707&quality=95&sign=55ce032e31afec9f289908a3309d9789&type=album';
    final navigator = ref.watch(navigationManagerProvider);

    return GestureDetector(
      onTap: () {
        navigator.openProfilePage();
      },
      child: Center(
        child: Container(
          decoration: BoxDecoration(
            color: theme.colorScheme.minorBackground,
            border: Border.all(
              color: theme.colorScheme.mainBackground,
            ),
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                blurRadius: 20,
                color: YXColors.trueBlack.withOpacity(0.12),
                offset: theme.shadowBottom.offset,
              ),
            ],
          ),
          child: const FittedBox(
            child: TXMUserpic(
              imageUrl: imageUrl,
            ),
          ),
        ),
      ),
    );
  }
}
