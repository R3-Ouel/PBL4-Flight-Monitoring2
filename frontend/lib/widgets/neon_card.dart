import 'package:flutter/material.dart';

class NeonCard extends StatelessWidget {
  final Widget child;
  const NeonCard({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF0D0D1A) : Colors.white;
    final borderColor = isDark ? Colors.white10 : Colors.grey.shade200;
    final boxShadow = isDark
        ? [
            BoxShadow(
              color: Theme.of(context).colorScheme.primary.withOpacity(0.12),
              blurRadius: 12,
              spreadRadius: 1,
            ),
          ]
        : [
            BoxShadow(
              color: Colors.black.withOpacity(0.06),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ];

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: borderColor),
        boxShadow: boxShadow,
      ),
      child: DefaultTextStyle.merge(
        style: TextStyle(color: isDark ? Colors.white : Colors.black87),
        child: child,
      ),
    );
  }
}
