import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../utils/assets.dart';
import '../../utils/localization.dart';

import 'txm_counter_button.dart';
import 'txm_small_button.dart';

class TXMProductCard extends HookConsumerWidget {
  final int count;
  final VoidCallback? onIncrement;
  final VoidCallback? onDecrement;
  final VoidCallback? onTapCartButton;
  final bool inCart;
  final String imageUrl;
  final bool hasDiscount;
  final String price;
  final String name;
  final String? additionText;
  final VoidCallback? onTap;

  const TXMProductCard({
    required this.imageUrl,
    required this.price,
    required this.name,
    this.additionText,
    this.hasDiscount = false,
    this.inCart = false,
    this.onTapCartButton,
    this.onIncrement,
    this.onDecrement,
    Key? key,
    this.count = 0,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = YXTheme.of<YXThemeData>(context);

    const productCardWidth = 120.0;

    return GestureDetector(
      onTap: onTap,
      child: SizedBox(
        width: productCardWidth,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                CachedNetworkImage(
                  imageUrl: imageUrl,
                ),
                if (hasDiscount) SvgPicture.asset(Assets.svgBestPrice),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              price,
              style: theme.textTheme.captionBold.copyWith(
                color: hasDiscount
                    ? theme.colorScheme.mainRed
                    : theme.colorScheme.mainText,
              ),
            ),
            Text(
              name,
              style: theme.textTheme.caption2.copyWith(
                color: theme.colorScheme.mainText,
              ),
            ),
            if (additionText != null)
              Text(
                '$additionText',
                style: theme.textTheme.caption2.copyWith(
                  color: theme.colorScheme.mainText,
                ),
              ),
            SizedBox(height: theme.mu(additionText != null ? 4 : 2)),
            if (inCart)
              TXMCounterButton(
                count,
                onDecrement: onDecrement,
                onIncrement: onIncrement,
              )
            else
              TXMSmallButton(
                title: Strings.of(context).addToCard,
                onTap: onTapCartButton,
              ),
          ],
        ),
      ),
    );
  }
}
