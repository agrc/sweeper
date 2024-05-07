# Changelog

## [2.0.0](https://github.com/agrc/sweeper/compare/v1.4.3...v2.0.0) (2024-05-07)


### ⚠ BREAKING CHANGES

* credentials.py has become config.json in cwd

### 🚀 Features

* allow for invocation without a config file ([e3107af](https://github.com/agrc/sweeper/commit/e3107af8b76265c3bab2f0afedf9f2be8d17cc31))
* implement EXCLUSIONS config ([5280fd8](https://github.com/agrc/sweeper/commit/5280fd84ae670497d6f190ce5b7b094b0b6fba72)), closes [#114](https://github.com/agrc/sweeper/issues/114)
* throw error if workspace does not exist ([cf6fb43](https://github.com/agrc/sweeper/commit/cf6fb4376f1e291f9d069b84ee59835f9ba0f842))


### 🐛 Bug Fixes

* add config to CI runs ([539d16f](https://github.com/agrc/sweeper/commit/539d16ff66aac3ccc897a2e8d510b2b4a5c107f1))
* credentials.py -&gt; config.json and smtp -> SendGrid ([8888cb7](https://github.com/agrc/sweeper/commit/8888cb755a37d883680fd2d2054df5b2c7114f33)), closes [#85](https://github.com/agrc/sweeper/issues/85) [#86](https://github.com/agrc/sweeper/issues/86)
* disable coverage when running tests in vscode ([7d0827f](https://github.com/agrc/sweeper/commit/7d0827ff00d289573ee99e5bbe352ef034695104))
* fix type errors ([f8f8012](https://github.com/agrc/sweeper/commit/f8f80127ca72086d0b124128d1c6fb6e22aa6fd7))
* handle street names that begin with cardinals ([b4372e5](https://github.com/agrc/sweeper/commit/b4372e550c4b33ccc01067114583f5698b88138a)), closes [#121](https://github.com/agrc/sweeper/issues/121)
* handle two unit numbers ([79c6f0f](https://github.com/agrc/sweeper/commit/79c6f0fb542f25eb649b72d3221ec2035a248a6e)), closes [#63](https://github.com/agrc/sweeper/issues/63)
* make exclusion matching work in CI ([2394ba3](https://github.com/agrc/sweeper/commit/2394ba377af1bd0d34fae0dbc964708ac6896472))
* modernize and apply best practices ([15c7bd0](https://github.com/agrc/sweeper/commit/15c7bd024ee7bd5a0b9e9e269fd7d90a9c21dd7b))
* move tests to standard directory and add skipping logic ([de83e86](https://github.com/agrc/sweeper/commit/de83e86c6e0160e371e49cc7e888a09950da8fbc))
* normalize shortened numeric street names ([e687551](https://github.com/agrc/sweeper/commit/e6875517ad305275770ce2084c0e0eb87ad303a7)), closes [#57](https://github.com/agrc/sweeper/issues/57)
* run ruff separate from pytest ([302c583](https://github.com/agrc/sweeper/commit/302c5832cf21506e912f16a78d37067857d142b3)), closes [#98](https://github.com/agrc/sweeper/issues/98)


### 📖 Documentation Improvements

* add functions that require the config file ([ea943bd](https://github.com/agrc/sweeper/commit/ea943bd6ed40a41466a6bc2836b42a1d280a8839))
* simplify run command in dev ([937c9c8](https://github.com/agrc/sweeper/commit/937c9c8e38d6f3a80eb7a45620673e1166662c2d))

## [1.4.3](https://github.com/agrc/sweeper/compare/v1.4.2...v1.4.3) (2023-07-06)


### 🐛 Bug Fixes

* lowercase filename ([2ab666c](https://github.com/agrc/sweeper/commit/2ab666c03c72850dcea5ab1bc57e2a1287642dac))

## [1.4.2](https://github.com/agrc/sweeper/compare/v1.4.1...v1.4.2) (2023-07-06)


### 📖 Documentation Improvements

* remove old deployment docs ([415db45](https://github.com/agrc/sweeper/commit/415db457a5ab6bd19ff4b85cd4e61ed2a8f3dcdd))
* update long description and author ([5d5628a](https://github.com/agrc/sweeper/commit/5d5628a9fa1509477f43a56bcc6d03a30357c40a))

## [1.4.1](https://github.com/agrc/sweeper/compare/v1.4.0...v1.4.1) (2023-07-06)


### 🐛 Bug Fixes

* correct py pi action ([c71e9f4](https://github.com/agrc/sweeper/commit/c71e9f4f789b658d9d750cfcfc03d96a2dc20e36))


### 📖 Documentation Improvements

* fix badge ([eea97fb](https://github.com/agrc/sweeper/commit/eea97fb7de90c6040b33ec6b1dbee1b065e068ce))

## [1.4.0](https://github.com/agrc/sweeper/compare/v1.3.5...v1.4.0) (2023-07-06)


### 🌲 Dependencies

* Q3 package updates ([20a1b6e](https://github.com/agrc/sweeper/commit/20a1b6e84e0243c0003321de56dc1c928019c179))
* update action deps ([84a5092](https://github.com/agrc/sweeper/commit/84a509294c311109f07154fae9aa8c482ad9f11d))


### 🚀 Features

* use release please pipeline ([9fb8007](https://github.com/agrc/sweeper/commit/9fb8007fd275d8262849db6a4ad650ad20df7a09))


### 🐛 Bug Fixes

* add missing dependency ([c4519b4](https://github.com/agrc/sweeper/commit/c4519b49de94e6ffb5ffcc6ba5c9b7ed9b5cbbb8)), closes [#93](https://github.com/agrc/sweeper/issues/93)
* correct dependency syntax ([4ea4d05](https://github.com/agrc/sweeper/commit/4ea4d053423ced8e2a0d3bb72ea87d4df6e23ccd))
