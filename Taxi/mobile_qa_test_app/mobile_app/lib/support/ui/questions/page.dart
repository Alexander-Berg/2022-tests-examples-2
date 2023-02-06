import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../utils/localization.dart';
import '../../../utils/navigation/navigation_manager.dart';

class QuestionsPage extends ConsumerWidget {
  QuestionsPage({Key? key}) : super(key: key);
  final questions = List.generate(
    6,
    (index) => 'У меня нет номера телефона',
  );

  @override
  Widget build(BuildContext context, WidgetRef ref) => TXMScaffold.slivers(
        appBar: const TXMScaffoldAppBar(
          leadingIcon: YXIconData.back,
        ),
        header: TXMScaffoldHeaderSliver(
          Strings.of(context).supportPageTitle,
        ),
        slivers: [
          SliverToBoxAdapter(
            child: YXListText(
              borderType: YXListBorderType.none,
              text: Strings.of(context).supportPageBody,
            ),
          ),
          SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, i) => YXListItem(
                title: questions[i],
                onTap: () =>
                    ref.read(navigationManagerProvider).openSupportAnswerPage(),
                trail: const YXIcon(
                  YXIconData.chevronsmall,
                ),
              ),
              childCount: questions.length,
            ),
          ),
        ],
      );
}
