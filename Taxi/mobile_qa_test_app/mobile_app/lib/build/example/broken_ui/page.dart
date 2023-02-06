import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../common/broken/broken_widget.dart';
import 'manager.dart';
import 'state_holder.dart';

class UserPage extends HookConsumerWidget {
  const UserPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    useEffect(
      () {
        ref.read(userPageManagerProvider).onInit();
      },
      [],
    );

    return BrokenWidget(
      brokenType: ref
          .watch(userPageBrokenStateHolderProvider.select((s) => s.brokenType)),
      child: Scaffold(
        backgroundColor: Colors.pink,
        body: Center(
          child: TextButton(
            onPressed: ref.watch(userPageManagerProvider).onAddTap,
            child: Text("Text"),
          ),
        ),
      ),
    );
  }
}
