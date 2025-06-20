# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
<!-- insertion marker -->
## [0.5.0](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.5.0) - 2025-06-20

<small>[Compare with 0.4.4](https://github.com/SeqOIA-IT/variantplaner/compare/0.4.4...0.5.0)</small>

### Features

- store info and format header associate to column in parquet metadata ([eca6812](https://github.com/SeqOIA-IT/variantplaner/commit/eca6812d44cb76e2b4e064882c70a47ccc11e482) by Pierre Marijon).
- rename option index in child and add documentation ([047506b](https://github.com/SeqOIA-IT/variantplaner/commit/047506b62a3a8909c62a949820d84fba38b7f188) by Pierre Marijon).
- transmission are run in any sample with a parent in ped file ([1032d3e](https://github.com/SeqOIA-IT/variantplaner/commit/1032d3ed608d677d5de1da3441ff76b69fcec2bf) by Pierre Marijon).
- add support of any format ([7070977](https://github.com/SeqOIA-IT/variantplaner/commit/7070977b26a73ff96f5855d6e03885ef0cb1a0a2) by Pierre Marijon).
- rename option index in child and add documentation ([4670526](https://github.com/SeqOIA-IT/variantplaner/commit/46705260c0ae22155c150707edcbabcfc6cbe7e4) by Pierre Marijon).

### Bug Fixes

- if column are missing in format return null ([762512a](https://github.com/SeqOIA-IT/variantplaner/commit/762512aeb22ccd4d4b902a5a939ff4a60b72f54c) by Pierre Marijon).
- improve documentation ([762512a](https://github.com/SeqOIA-IT/variantplaner/commit/7b761390e676cda5b7d7f07a6d41ab6185cf7c70) by Pierre Marijon).

## [0.4.4](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.4.4) - 2025-05-20

<small>[Compare with 0.4.3](https://github.com/SeqOIA-IT/variantplaner/compare/0.4.3...0.4.4)</small>

### Bug Fixes

- replace int2string by any2string and use uuid instead of python hash function ([a63aa8c](https://github.com/SeqOIA-IT/variantplaner/commit/a63aa8c6f6da6c40fd96b3a9f87e85a38d5c9783) by Pierre Marijon).
- temporary file name is now a hash of input file name ([2af10fc](https://github.com/SeqOIA-IT/variantplaner/commit/2af10fcc3bee4e696a0b8a3d76582b2920b46dce) by Pierre Marijon).
- support version 1.29 of polars ([810659a](https://github.com/SeqOIA-IT/variantplaner/commit/810659a63b3d793e546a9fd0e661912cee96e944) by Pierre Marijon).

## [0.4.3](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.4.3) - 2025-05-14

<small>[Compare with 0.4.2](https://github.com/SeqOIA-IT/variantplaner/compare/0.4.2...0.4.3)</small>

### Features

- set row group size parameter of sink_polars ([9f2285a](https://github.com/SeqOIA-IT/variantplaner/commit/9f2285a7237cc5f0875c9e17cb6ec8810f883fe4) by Pierre Marijon).

### Bug Fixes

- correct snpeff annotation script ([197297c](https://github.com/SeqOIA-IT/variantplaner/commit/197297c847e39ec44fa9c9763e4b3e0863c810af) by Pierre Marijon).
- apply click 8.2 change ([4524890](https://github.com/SeqOIA-IT/variantplaner/commit/45248907e4f5e97a2bf5cd5bff3127959f33935f) by Pierre Marijon).

## [0.4.2](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.4.2) - 2025-04-15

<small>[Compare with 0.4.1](https://github.com/SeqOIA-IT/variantplaner/compare/0.4.1...0.4.2)</small>

### Features

- support compressed vcf with xopen ([3310947](https://github.com/SeqOIA-IT/variantplaner/commit/3310947fd8013740739894a642f9c8517b434993))

### Bug Fixes

- remove debug instruction ([dd93d54](https://github.com/SeqOIA-IT/variantplaner/commit/dd93d5441f84c8051d25a35fb5443acca3426f5a) by Pierre Marijon).

## [0.4.1](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.4.1) - 2025-04-15

<small>[Compare with 0.4.0](https://github.com/SeqOIA-IT/variantplaner/compare/0.4.0...0.4.1)</small>

### Bug Fixes

- try to avoid possible random error in int2string ([5c7d40e](https://github.com/SeqOIA-IT/variantplaner/commit/5c7d40e1246397cb5dac601f0959c5552ffc3bcd) by Pierre Marijon).

## [0.4.0](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.4.0) - 2025-04-10

<small>[Compare with 0.3.1](https://github.com/SeqOIA-IT/variantplaner/compare/0.3.1...0.4.0)</small>

### Bug Fixes

- genotype samples_names perform unique sample ([64e7274](https://github.com/SeqOIA-IT/variantplaner/commit/64e7274f525eb9da0dd611566c3b3db5bd9d5f17) by Pierre Marijon).
- improve struct variant tmp file naming ([3119a40](https://github.com/SeqOIA-IT/variantplaner/commit/3119a407c76d4f3a7d71938126c6dc92fa8ee8ed) by Pierre Marijon).

### Code Refactoring

- rename variantplaner_rs in variantid and rewrite it ([3961428](https://github.com/SeqOIA-IT/variantplaner/commit/3961428f3163f35b79e21f2573b3007ac364af9e) by Pierre Marijon).

## [0.3.1](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.3.1) - 2024-12-16

<small>[Compare with 0.3.1](https://github.com/SeqOIA-IT/variantplaner/compare/0.3.0...0.3.1)</small>

### Features

- struct unique variant split variants by chromosome ([ae7eb65](https://github.com/SeqOIA-IT/variantlaner/commit/ae7eb6599927e022122c0464164657019784ff47) by Pierre Marijon).
- struct genotype polars threads parameter have an effect ([6419e02](https://github.com/SeqOIA-IT/variantlaner/commit/6419e02570fff59713623db0baf02ee7c27f4f46) by Pierre Marijon).
- use new functionality of variantplaner_rs in variantplaner cli ([f986213](https://github.com/SeqOIA-IT/variantlaner/commit/f9862139554027d8558562696b604628e2fdef30) by Pierre Marijon).
- variantplaner_rs partitions could be parameterize ([8b2066e](https://github.com/SeqOIA-IT/variantplaner/commit/8b2066ebf96e5ba7dc34181359a1d13121253048) by Pierre Marijon).

### Bug Fixes

- use number of bit ask by user in partitions ([4409d8c](https://github.com/SeqOIA-IT/variantplaner/commit/4409d8c6934fd6b5131376d41a515d5fa36ee9b2) by Pierre Marijon).
- readd documentation generation ([6467ee2](https://github.com/SeqOIA-IT/variantplaner/commit/6467ee2d38b0885676ba0d17ed299869252c57b3) by Pierre Marijon).
- transmission generation not failled if ped file contain only one line ([58ee926](https://github.com/SeqOIA-IT/variantplaner/commit/58ee926c11cf62a289645acd59b32e3281e5852b) by Pierre Marijon).

## [0.3.0](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.3.0) - 2024-09-30

<small>[Compare with 0.2.4](https://github.com/SeqOIA-IT/variantplaner/compare/0.2.4...0.3.0)</small>

### Features

- move ped code from io to object ([b6638ca](https://github.com/SeqOIA-IT/variantplaner/commit/b6638ca7a562316a25c18e54459a74926582357f) by Pierre Marijon).
- parquet2vcf can extract only variant of one chromosome ([f29c6ac](https://github.com/SeqOIA-IT/variantplaner/commit/f29c6ac2ea048714729515422858087195b31417) by Pierre Marijon).
- improve alt '*' management ([755a5fa](https://github.com/SeqOIA-IT/variantplaner/commit/755a5fad7b822463495c3bae391542872d0a0ac2) by Pierre Marijon).
- partition support append mode ([1b6603f](https://github.com/SeqOIA-IT/variantplaner/commit/1b6603ffd24b2f2d81bdf8198ae4378ef9e6a78e) by Pierre Marijon).
- variant merge support append ([d12d357](https://github.com/SeqOIA-IT/variantplaner/commit/d12d3574a91e0ff5dc33d7171097a9a5f4faf8cd) by Pierre Marijon).
- Add python 3.12 in ci test and support ([c51c932](https://github.com/SeqOIA-IT/variantplaner/commit/c51c932180b1d7bba2e00c5720cc7bd4bf987e33) by Pierre Marijon).
- Better variant hash we only need store ref length ([8a3db5e](https://github.com/SeqOIA-IT/variantplaner/commit/8a3db5eab8c91b727a1e91f82b15c52c963c1a8c) by Pierre Marijon).
- add documentation on how interogate genotype variants partitions ([b843bca](https://github.com/SeqOIA-IT/variantplaner/commit/b843bca05aa463703e2f708450b48656512dbcaa) by Pierre Marijon).
- New cli ([c2cb033](https://github.com/SeqOIA-IT/variantplaner/commit/c2cb033ce00f548f7d6f1041d5381adfc0debcf5) by Pierre Marijon).

### Bug Fixes

- add output file in struct operation only if it's exist ([9a868ad](https://github.com/SeqOIA-IT/variantplaner/commit/9a868ad58d12210fc46ccf35a0503e6bceae28ba) by Pierre Marijon).
- not failled if SVTYPE or SVLEN column isn't present ([32a8dad](https://github.com/SeqOIA-IT/variantplaner/commit/32a8dad0d5f5654d06d39e79cc03b53cb2c91e13) by Pierre Marijon).
- correct benchmark script run ([8ebdca0](https://github.com/SeqOIA-IT/variantplaner/commit/8ebdca08f1f7e7871771050f7df43aa96be825d6) by Pierre Marijon).

### Code Refactoring

- Move many variant operation in object. ([df36fa0](https://github.com/SeqOIA-IT/variantplaner/commit/df36fa0db9e933030b4b72f92645f5717b74597e) by Pierre Marijon).

## [0.2.4](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.2.4) - 2023-12-21

<small>[Compare with 0.2.4](https://github.com/SeqOIA-IT/variantplaner/compare/0.2.3...0.2.4)</small>

### Features

- add variantplaner logo.
- add method to compute partition value of id.

### Bug Fixes

- fix: #41 vcf spec indicate Integer must be store in 32bits.
- update to polars 0.20.

## [0.2.3](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.2.2) - 2023-11-21

<small>[Compare with 0.2.2](https://github.com/SeqOIA-IT/variantplaner/compare/0.2.2..0.2.3)</small>

### Features:

- Use ruff format in place of black
- Minimal polars version is 0.19.15
- SV cannot have small variant id
- Type of id is include in part of id (all long variant are store in same place)

### Fix:

- Usage intgerate chromosome2length option

## [0.2.2](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.2.2) - 2023-10-19

<small>[Compare with first 0.2.0](https://github.com/SeqOIA-IT/variantplaner/compare/0.2.1...0.2.2)</small>

### Fix:

- Correct typo in readme
- Correct change in variantplaner_rs/Cargo.lock

## [0.2.1](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.2.1) - 2023-10-09

<small>[Compare with first 0.2.0](https://github.com/SeqOIA-IT/variantplaner/compare/0.2.0...0.2.1)</small>

### Fix:

- Hot fix some lazy trouble

## [0.2.0](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.2.0) - 2023-10-02

<small>[Compare with first 0.1.0](https://github.com/SeqOIA-IT/variantplaner/compare/0.1.0...0.2.0)</small>

### Features:

- Replace hash variant id by a uniq variant id
- Improve variant transmission system to support genome with ploidie lower than 92
- Genotype partitioning now use position part of unique id to get more local request

### Fixes:

- Documentation fix
- Test coverage improvement

## [0.1.0](https://github.com/SeqOIA-IT/variantplaner/releases/tag/0.1.0) - 2023-07-25

<small>[Compare with first commit](https://github.com/SeqOIA-IT/variantplaner/compare/265a95ea26746b7aa796c3df6cee2451a608dd49...0.1.0)</small>
