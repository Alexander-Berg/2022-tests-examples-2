import 'package:freezed_annotation/freezed_annotation.dart';

import 'bug.dart';

part 'build.freezed.dart';
part 'build.g.dart';

@freezed
class Build with _$Build {
  @JsonSerializable(explicitToJson: true)
  const factory Build({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'bugs') required List<Bug> bugs,
  }) = _Build;

  static const noBugs = Build(id: '0', bugs: []);

  factory Build.fromJson(Map<String, dynamic> json) => _$BuildFromJson(json);
}
