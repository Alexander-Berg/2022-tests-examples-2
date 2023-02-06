import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../common/broken/broken_widget.dart';
import '../../providers.dart';

class AnswerPage extends HookConsumerWidget {
  const AnswerPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) => BrokenWidget(
        brokenType: ref.watch(answerPageBrokenStateHolderProvider),
        child: TXMScaffold(
          appBar: const TXMScaffoldAppBar(
            leadingIcon: YXIconData.back,
          ),
          header: const TXMScaffoldHeaderSliver('У меня нету номера телефона'),
          body: const YXListText(
            borderType: YXListBorderType.none,
            text: 'Какой-нибудь ответ',
          ),
        ),
      );
}
