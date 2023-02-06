import 'package:flutter_txm_ui_components/components.dart';

enum ShopSectionBorderRadiusType { all, top, bottom, none }
enum ShopSectionShadowType { all, top, bottom, none }

class ShopSection extends StatelessWidget {
  final Widget child;
  final String? title;
  final ShopSectionBorderRadiusType borderRadiusType;
  final ShopSectionShadowType? shadowType;

  const ShopSection({
    required this.child,
    this.shadowType = ShopSectionShadowType.none,
    this.title,
    this.borderRadiusType = ShopSectionBorderRadiusType.all,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = YXTheme.of<YXThemeData>(context);
    final isBorderRadiusTop = [
      ShopSectionBorderRadiusType.all,
      ShopSectionBorderRadiusType.top,
    ].contains(borderRadiusType);
    final isBorderRadiusBottom = [
      ShopSectionBorderRadiusType.bottom,
      ShopSectionBorderRadiusType.all,
    ].contains(borderRadiusType);
    final borderRadius = Radius.circular(
      theme.buttonTheme.muBorderRadius * theme.buttonTheme.muHeight,
    );

    return Container(
      margin: EdgeInsets.only(
        bottom: isBorderRadiusBottom ? theme.module / 1.3 : 0,
      ),
      padding: EdgeInsets.only(
        bottom: theme.listItemTheme.detailPadding.horizontal,
      ),
      decoration: BoxDecoration(
        color: theme.colorScheme.mainBackground,
        borderRadius: BorderRadius.vertical(
          top: isBorderRadiusTop ? borderRadius : Radius.zero,
          bottom: isBorderRadiusBottom ? borderRadius : Radius.zero,
        ),
        boxShadow: [
          if ([
            ShopSectionShadowType.all,
            ShopSectionShadowType.top,
          ].contains(shadowType))
            theme.shadowTop,
          if ([
            ShopSectionShadowType.all,
            ShopSectionShadowType.bottom,
          ].contains(shadowType))
            theme.shadowBottom,
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (title != null)
            YXListItem(
              title: title,
              detailPadding: const EdgeInsets.all(0),
              borderType: YXListBorderType.none,
            ),
          Padding(
            padding: theme.listItemTheme.rootContainerPadding,
            child: child,
          ),
        ],
      ),
    );
  }
}
