import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:models/models.dart';

class TMXShopCategory extends StatelessWidget {
  final Category category;
  final VoidCallback? onTap;

  const TMXShopCategory({
    required this.category,
    required this.onTap,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = YXTheme.of<YXThemeData>(context);

    return AspectRatio(
      aspectRatio: 0.84,
      child: Material(
        type: MaterialType.transparency,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(
            theme.buttonTheme.muBorderRadius * theme.buttonTheme.muHeight,
          ),
          child: Ink(
            width: double.infinity,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(
                theme.buttonTheme.muBorderRadius * theme.buttonTheme.muHeight,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                YXListItem(
                  borderType: YXListBorderType.none,
                  title: category.title,
                ),
                Expanded(
                  child: CachedNetworkImage(
                    alignment: Alignment.bottomRight,
                    fit: BoxFit.fitHeight,
                    imageUrl: category.imageUrl,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
