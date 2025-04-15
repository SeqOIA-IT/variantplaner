# VariantPlaner

variantplaner is a set of tools that converts a large set of vcf's into an interoperable data structure efficiently.

To show the capabilities of the `variantplaner`, we will use a small example.

The purpose of this short tutorial is to present:

- how to convert vcf into a more suitable format
- how data can be restructured for querying
- how to integrate variant annotation databases
- how these different files can be used to obtain interesting biological information

This tutorial suggests an organization of files, but you're under no obligation to follow it `variantplaner` is quite flexible in its organization.

## Setup

This tutorial assume you are on unix like system, you have python setup and you [install variantplaner](https://github.com/SeqOIA-IT/variantplaner#installation)


Requirements list:

- curl
- gunzip
- [pqrs](https://github.com/manojkarthick/pqrs) (only for transmission computation, otherwise optional)

Optional:

- gnu-parallel

Quering dataset:

- [polars-cli](https://crates.io/crates/polars-cli)
- [duckdb](https://duckdb.org/)


## Download data

```bash
mkdir -p vp_tuto/vcf/
cd vp_tuto
URI_ROOT="https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release"
curl ${URI_ROOT}/NA12878_HG001/latest/GRCh38/HG001_GRCh38_1_22_v4.2.1_benchmark.vcf.gz | gunzip - > vcf/HG001.vcf
curl ${URI_ROOT}/AshkenazimTrio/HG002_NA24385_son/latest/GRCh38/HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz | gunzip - > vcf/HG002.vcf
curl ${URI_ROOT}/AshkenazimTrio/HG003_NA24149_father/latest/GRCh38/HG003_GRCh38_1_22_v4.2.1_benchmark.vcf.gz | gunzip - > vcf/HG003.vcf
curl ${URI_ROOT}/AshkenazimTrio/HG004_NA24143_mother/latest/GRCh38/HG004_GRCh38_1_22_v4.2.1_benchmark.vcf.gz | gunzip - > vcf/HG004.vcf
curl ${URI_ROOT}/ChineseTrio/HG006_NA24694_father/latest/GRCh38/HG006_GRCh38_1_22_v4.2.1_benchmark.vcf.gz | gunzip - > vcf/HG006.vcf
curl ${URI_ROOT}/ChineseTrio/HG007_NA24695_mother/latest/GRCh38/HG007_GRCh38_1_22_v4.2.1_benchmark.vcf.gz | gunzip - > vcf/HG007.vcf
```

## Variant planner presentation

variantplaner is a python module with command line tools, it is composed of several subcommands (they will be detailed later) but has two global options, one for parallelization and another for the level of verbosity you want.

```
Usage: variantplaner [OPTIONS] COMMAND [ARGS]...

  Run VariantPlanner.

Options:
  -t, --threads INTEGER RANGE  Number of threads usable  [default: 1; x>=0]
  -v, --verbose                Verbosity level  [0<=x<=4]
  --debug-info                 Get debug information
  -h, --help                   Show this message and exit.

Commands:
  metadata      Convert metadata file in parquet file.
  parquet2vcf   Convert variant parquet in vcf.
  struct        Subcommand to made struct operation on parquet file.
  transmission  Generate transmission of a genotype set.
  vcf2parquet   Convert a vcf in parquet.
```


## vcf2parquet

First step is to convert vcf data in [parquet](https://en.wikipedia.org/wiki/Apache_Parquet), it's a column oriented format with better performance than indexed vcf.

We split vcf in two part on for variant information and another for genotype information.

```bash
mkdir -p variants genotypes/samples/
```

```
for vcf_path in $(ls vcf/*.vcf)
do
    sample_name=$(basename ${vcf_path} .vcf)
    variantplaner -t 4 vcf2parquet -i ${vcf_path} \
    -c grch38.92.csv \
    variants -o variants/${sample_name}.parquet \
    genotypes -o genotypes/samples/${sample_name}.parquet \
    -f GT:PS:DP:ADALL:AD:GQ
done
```

We iterate over all vcf, variants are store in `variants/{sample_name}.parquet`, genotype information are store in `variants/{sample_name}.parquet`. Only genotypes with a format value equal to the `-f` parameter value are retained.

/// details | gnu-parallel method
```bash
find vcf -type f -name *.vcf -exec basename {} .vcf \; | \
parallel variantplaner -t 2 vcf2parquet -c grch38.92.csv -i vcf/{}.vcf \
variants -o variants/{}.parquet genotypes -o genotypes/samples/{}.parquet -f GT:PS:DP:ADALL:AD:GQ
```
///

Parquet variants file contains 5 column:

- pos: Position of variant
- ref: Reference sequence
- alt: Alternative sequence
- id: An hash of other value collision isn't check but highly improbable [check api documentation](reference/variantplaner/normalization.md#variantplaner.normalization.add_variant_i)


/// details | variants parquet file content
You can inspect content of parquet file generate with pqrs
```bash
pqrs head variants/HG001.parquet
{id: 17886044532216650390, chr: 1, pos: 783006, ref: "A", alt: "G"}
{id: 7513336577790240873, chr: 1, pos: 783175, ref: "T", alt: "C"}
{id: 17987040642944149052, chr: 1, pos: 784860, ref: "T", alt: "C"}
{id: 10342734968077036194, chr: 1, pos: 785417, ref: "G", alt: "A"}
{id: 890514037559296207, chr: 1, pos: 797392, ref: "G", alt: "A"}
```
///

Parquet genotypes file contains column:

- id: Same as variant id
- gt: vcf GT value 1 -> heterozygote 2 -> homozygote (phasing information is lost)
- ps: Phase set in which this variant falls
- dp: vcf DP coverage of the variant for this sample
- adall: Net allele depths across all datasets
- ad: vcf AD per allele reads depth
- gq: vcf GQ quality of variant for this sample

/// details | genotypes parquet file content
You can inspect content of parquet file generate with pqrs
```bash
pqrs head genotypes/samples/HG001.parquet
{id: 17886044532216650390, sample: "HG001", gt: 2, ps: null, dp: 652, adall: [16, 234], ad: [0, 82], gq: 312}
{id: 7513336577790240873, sample: "HG001", gt: 2, ps: null, dp: 639, adall: [0, 218], ad: [0, 84], gq: 194}
{id: 17987040642944149052, sample: "HG001", gt: 2, ps: null, dp: 901, adall: [105, 406], ad: [0, 74], gq: 301}
{id: 10342734968077036194, sample: "HG001", gt: 2, ps: null, dp: 820, adall: [125, 383], ad: [0, 70], gq: 339}
{id: 890514037559296207, sample: "HG001", gt: 1, ps: null, dp: 760, adall: [161, 142], ad: [25, 37], gq: 147}
```
///

## Structuration of data

### Merge all variant

We can now aggregate all variant present in our dataset to perform this operation we use divide to conquer merge method by generate temporary file. By default, file are written in `/tmp` but you can control where these files are written by set `TMPDIR`, `TEMP` or `TMP` directory.

```bash
variantplaner -t 8 struct -i variants/*.parquet -- variants -o variants.parquet
```

File `variants.parquet` contains all unique variants present in dataset, `--` after last input path are mandatory.

### Genotypes structuration

### By samples

This structurations data is already down in vcf2parquet step check content of `genotypes/samples`:
```bash
➜ ls genotypes/samples
HG001.parquet  HG002.parquet  HG003.parquet  HG004.parquet  HG006.parquet  HG007.parquet
```

### By variants

Here, we'll organize the genotypes information by variants to make it easier to find samples where a variant is present or not.

```bash
mkdir -p genotypes/variants/
variantplaner -t 8 struct -i genotypes/samples/*.parquet -- genotypes -p genotypes/variants
```

All genotypes information are split in [hive like structure](https://duckdb.org/docs/data/partitioning/hive_partitioning) to optimize request on data, `--` after last input path are mandatory.

### Compute transmission mode

If you are working with families, `variantplaner` can calculate the modes of transmission of the variants.

For these step, we need to concatenate all genotypes of a AshkenazimTrio in one parquet sample.

```bash
pqrs merge -i genotypes/samples/HG002.parquet genotypes/samples/HG003.parquet genotypes/samples/HG004.parquet -o genotypes/samples/AshkenazimTrio.parquet
mkdir -p genotypes/transmissions/
variantplaner transmission -g genotypes/samples/AshkenazimTrio.parquet -i HG002 -m HG003 -f HG004 -o genotypes/transmissions/AshkenazimTrio.parquet
```

`-I` parameter is use for index sample, `-m` parameter is use for mother sample, `-f` parameter is use for father sample only the index sample is mandatory if mother sample or father sample isn't present command work, you could also use a pedigree file with parameter `-p`.

/// details | transmission parquet file content
```
{id: 10201716324449815219, index_gt: 2, index_ps: null, index_dp: 1066, index_adall: [0, 284], index_ad: [118, 586], index_gq: 598, mother_gt: null, mother_ps: null, mother_dp: null, mother_adall: null, mother_ad: null, mother_gq: null, father_gt: null, father_ps: null, father_dp: null, father_adall: null, father_ad: null, father_gq: null, origin: "#~~"}
{id: 8292180701257594706, index_gt: 1, index_ps: null, index_dp: 1122, index_adall: [177, 165], index_ad: [310, 283], index_gq: 556, mother_gt: null, mother_ps: null, mother_dp: null, mother_adall: null, mother_ad: null, mother_gq: null, father_gt: null, father_ps: null, father_dp: null, father_adall: null, father_ad: null, father_gq: null, origin: ""~~"}
{id: 1728452411043401356, index_gt: 1, index_ps: null, index_dp: 1365, index_adall: [225, 222], index_ad: [348, 380], index_gq: 658, mother_gt: null, mother_ps: null, mother_dp: null, mother_adall: null, mother_ad: null, mother_gq: null, father_gt: null, father_ps: null, father_dp: null, father_adall: null, father_ad: null, father_gq: null, origin: ""~~"}
{id: 4237549706021671868, index_gt: 1, index_ps: null, index_dp: 1019, index_adall: [154, 153], index_ad: [277, 282], index_gq: 517, mother_gt: null, mother_ps: null, mother_dp: null, mother_adall: null, mother_ad: null, mother_gq: null, father_gt: null, father_ps: null, father_dp: null, father_adall: null, father_ad: null, father_gq: null, origin: ""~~"}
{id: 1361753917441299167, index_gt: 1, index_ps: null, index_dp: 1033, index_adall: [159, 170], index_ad: [265, 273], index_gq: 552, mother_gt: null, mother_ps: null, mother_dp: null, mother_adall: null, mother_ad: null, mother_gq: null, father_gt: null, father_ps: null, father_dp: null, father_adall: null, father_ad: null, father_gq: null, origin: ""~~"}
```
///

Parquet transmissions file contains column all genotypes information with suffix `_index`, `_mother` and `_father` plus a `origin` column

Origin column contains a string with 3 character:

```
#~"
││└ ASCII_value_of(father genotype + 33)
│└─ ASCII_value_of(mother genotype + 33)
└── ASCII_value_of(index genotype  + 33)
```

In this example case, variants is homozygotes in index, mother information is missing, variants is heterozygotes in father.

Maximal genotype value is 92, which corresponds to the character `}`, `~` match with value 93, this value also mean unknow genotype.


## Add annotations

To work on your variant, you probably need variants annotations.

### Snpeff annotations

First convert your unique variants in parquet format (`variants.parquet`) in vcf:
```bash
variantplaner -t 8 parquet2vcf -i variants.parquet -o variants.vcf
```

`parquet2vcf` subcommand have many more options but we didn't need it now.

Next annotate this `variants.vcf` [with snpeff](https://pcingola.github.io/SnpEff/), we assume you generate a file call `variants.snpeff.vcf`.

To convert annotated vcf in parquet, keep 'ANN' info column and rename vcf id column in snpeff\_id you can run:
```bash
mkdir -p annotations
variantplaner -t 8 vcf2parquet -c grch38.92.csv -i variants.snpeff.vcf annotations -o annotations/snpeff.parquet vcf -i ANN -r snpeff_id
```

If you didn't set any value of option `-i` in vcf subsubcommand all info column are keep.

### Clinvar annotations

Download last clinvar version:

```bash
mkdir -p annotations
curl https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz \
| gunzip - > annotations/clinvar.vcf
```

Because clinvar's vcf file header does not contain information on contigs, you should create file `grch38.92.csv` with this content:
```
contig,length
chr1,248956422
chr10,133797422
chr11,135086622
chr12,133275309
chr13,114364328
chr14,107043718
chr15,101991189
chr16,90338345
chr17,83257441
chr18,80373285
chr19,58617616
chr2,242193529
chr20,64444167
chr21,46709983
chr22,50818468
chr3,198295559
chr4,190214555
chr5,181538259
chr6,170805979
chr7,159345973
chr8,145138636
chr9,138394717
chrMT,16569
chrX,156040895
chrY,57227415
```

Convert clinvar vcf file in parquet file:

```bash
variantplaner vcf2parquet -c grch38.92.csv -i annotations/clinvar.vcf annotations -o annotations/clinvar.parquet -r clinvar_id
```

Parquet file produce contains many columns:

- clinvar_id: content of vcf id column if option `-r` is not set, column name is `vid`
- id: variantplaner id
- All INFO filed

Annotations subcommand try to make match between vcf info type and parquet type.

/// details | `annotations/clinvar.parquet` file content
```bash
pqrs head annotations/clinvar.parquet
{clinvar_id: 2205837, id: 11650605831284591550, AF_ESP: null, AF_EXAC: null, AF_TGP: null, ALLELEID: 2193183, CLNDN: ["Inborn_genetic_diseases"], CLNDNINCL: null, CLNDISDB: ["MeSH:D030342", "MedGen:C0950123"], CLNDISDBINCL: null, CLNHGVS: ["NC_000001.11:g.69134A>G"], CLNREVSTAT: ["criteria_provided", "_single_submitter"], CLNSIG: ["Likely_benign"], CLNSIGCONF: null, CLNSIGINCL: null, CLNVC: "single_nucleotide_variant", CLNVCSO: "SO:0001483", CLNVI: null, DBVARID: null, GENEINFO: "OR4F5:79501", MC: ["SO:0001583|missense_variant"], ORIGIN: ["1"], RS: null}
{clinvar_id: 2252161, id: 2295086632353399847, AF_ESP: null, AF_EXAC: null, AF_TGP: null, ALLELEID: 2238986, CLNDN: ["Inborn_genetic_diseases"], CLNDNINCL: null, CLNDISDB: ["MeSH:D030342", "MedGen:C0950123"], CLNDISDBINCL: null, CLNHGVS: ["NC_000001.11:g.69581C>G"], CLNREVSTAT: ["criteria_provided", "_single_submitter"], CLNSIG: ["Uncertain_significance"], CLNSIGCONF: null, CLNSIGINCL: null, CLNVC: "single_nucleotide_variant", CLNVCSO: "SO:0001483", CLNVI: null, DBVARID: null, GENEINFO: "OR4F5:79501", MC: ["SO:0001583|missense_variant"], ORIGIN: ["1"], RS: null}
{clinvar_id: 2396347, id: 11033100074712141168, AF_ESP: null, AF_EXAC: null, AF_TGP: null, ALLELEID: 2386655, CLNDN: ["Inborn_genetic_diseases"], CLNDNINCL: null, CLNDISDB: ["MeSH:D030342", "MedGen:C0950123"], CLNDISDBINCL: null, CLNHGVS: ["NC_000001.11:g.69682G>A"], CLNREVSTAT: ["criteria_provided", "_single_submitter"], CLNSIG: ["Uncertain_significance"], CLNSIGCONF: null, CLNSIGINCL: null, CLNVC: "single_nucleotide_variant", CLNVCSO: "SO:0001483", CLNVI: null, DBVARID: null, GENEINFO: "OR4F5:79501", MC: ["SO:0001583|missense_variant"], ORIGIN: ["1"], RS: null}
{clinvar_id: 2288999, id: 10487392163259126218, AF_ESP: null, AF_EXAC: null, AF_TGP: null, ALLELEID: 2278803, CLNDN: ["Inborn_genetic_diseases"], CLNDNINCL: null, CLNDISDB: ["MeSH:D030342", "MedGen:C0950123"], CLNDISDBINCL: null, CLNHGVS: ["NC_000001.11:g.69769T>C"], CLNREVSTAT: ["criteria_provided", "_single_submitter"], CLNSIG: ["Uncertain_significance"], CLNSIGCONF: null, CLNSIGINCL: null, CLNVC: "single_nucleotide_variant", CLNVCSO: "SO:0001483", CLNVI: null, DBVARID: null, GENEINFO: "OR4F5:79501", MC: ["SO:0001583|missense_variant"], ORIGIN: ["1"], RS: null}
{clinvar_id: 2351346, id: 5356120651941363990, AF_ESP: null, AF_EXAC: null, AF_TGP: null, ALLELEID: 2333177, CLNDN: ["Inborn_genetic_diseases"], CLNDNINCL: null, CLNDISDB: ["MeSH:D030342", "MedGen:C0950123"], CLNDISDBINCL: null, CLNHGVS: ["NC_000001.11:g.69995G>C"], CLNREVSTAT: ["criteria_provided", "_single_submitter"], CLNSIG: ["Uncertain_significance"], CLNSIGCONF: null, CLNSIGINCL: null, CLNVC: "single_nucleotide_variant", CLNVCSO: "SO:0001483", CLNVI: null, DBVARID: null, GENEINFO: "OR4F5:79501", MC: ["SO:0001583|missense_variant"], ORIGIN: ["1"], RS: null}
```
///

With option of subcommand vcf `-i` you can select which column are included in parquet file
For example command:
```bash
variantplaner vcf2parquet -c grch38.92.csv -i annotations/clinvar.vcf annotations -o annotations/clinvar.parquet -r clinvar_id -i ALLELEID -i CLNDN -i AF_ESP -i GENEINFO
```

Produce a `annotations/clinvar.parquet` with columns:

- clinvar_id
- id
- ALLELEID
- CLNDN


/// details | `annotations/clinvar.parquet` file content
```bash
➜ pqrs head annotations/clinvar.parquet
{clinvar_id: 2205837, id: 11650605831284591550, ALLELEID: 2193183, CLNDN: ["Inborn_genetic_diseases"]}
{clinvar_id: 2252161, id: 2295086632353399847, ALLELEID: 2238986, CLNDN: ["Inborn_genetic_diseases"]}
{clinvar_id: 2396347, id: 11033100074712141168, ALLELEID: 2386655, CLNDN: ["Inborn_genetic_diseases"]}
{clinvar_id: 2288999, id: 10487392163259126218, ALLELEID: 2278803, CLNDN: ["Inborn_genetic_diseases"]}
{clinvar_id: 2351346, id: 5356120651941363990, ALLELEID: 2333177, CLNDN: ["Inborn_genetic_diseases"]}
```
///

### Split snpeff annotations in parquet column

After annotate your vcf with snpeff in `ann` mode and write result in file `snpeff_annotations.vcf` you could run a script similar to this to generate `snpeff_annotations.parquet`:
```python
from variantplaner import Vcf

vcf = Vcf()
try:
    vcf.from_path("snpeff_annotations.vcf", "grch38.92.csv")
except variantplaner.exception.NotAVCFError:
    print("snpeff_annotations.vcf seems to have error")
    return 1
except variantplaner.exception.NoContigsLengthInformationError:
    print("snpeff_annotations.vcf header seems not contain contig information")
    return 2

lf = vcf.lf.with_columns(vcf.header.info_parser())
lf = lf.drop(["chr", "pos", "ref", "alt", "filter", "qual", "info"])
lf = lf.rename({"vid": "id"})
lf = lf.explode("ANN")
lf = lf.cast({"id": polars.UInt64})

lf = lf.with_columns(
    [
        polars.col("ANN")
        .list.get(0)
        .str.split("|")
        .cast(polars.List(polars.Utf8()))
        .alias("ann"),
    ]
).drop("ANN")

lf = lf.with_columns(
    [
        polars.col("ann").list.get(1).alias("effect"),
        polars.col("ann").list.get(2).alias("impact"),
        polars.col("ann").list.get(3).alias("gene"),
        polars.col("ann").list.get(4).alias("geneid"),
        polars.col("ann").list.get(5).alias("feature"),
        polars.col("ann").list.get(6).alias("feature_id"),
        polars.col("ann").list.get(7).alias("bio_type"),
        polars.col("ann").list.get(8).alias("rank"),
        polars.col("ann").list.get(9).alias("hgvs_c"),
        polars.col("ann").list.get(10).alias("hgvs_p"),
        polars.col("ann").list.get(11).alias("cdna_pos"),
        polars.col("ann").list.get(12).alias("cdna_len"),
        polars.col("ann").list.get(13).alias("cds_pos"),
        polars.col("ann").list.get(14).alias("cvs_len"),
        polars.col("ann").list.get(15).alias("aa_pos"),
    ]
).drop("ann")

lf.sink_parquet("snpeff_annotations.parquet")
```

## Querying

You can use any tool or software library supporting the parquet format to use the files generated by `variantplaner`.

We show you how to use files with [polars-cli](https://crates.io/crates/polars-cli) and [duckdb](https://duckdb.org/).

### polars-cli

#### Count variants

```sql
〉select count(*) from read_parquet('variants.parquet');
┌─────────┐
│ count   │
│ ---     │
│ u32     │
╞═════════╡
│ 7852699 │
└─────────┘
```


/// details | check result with `pqrs`
We can check we have same result with pqrs

```bash
➜ pqrs rowcount variants.parquet
File Name: variants.parquet: 7852699 rows
```
///

#### Filter variants from annotations:

Get all variant with a AF_ESP upper than 0.9999

```sql
〉select chr, pos, ref, alt, AF_ESP from read_parquet('variants.parquet') as v left join read_parquet('annotations/clinvar.parquet') as c on c.id=v.id where AF_ESP>0.9999;
┌─────┬──────────┬─────┬─────┬─────────┐
│ chr ┆ pos      ┆ ref ┆ alt ┆ AF_ESP  │
│ --- ┆ ---      ┆ --- ┆ --- ┆ ---     │
│ u8  ┆ u64      ┆ str ┆ str ┆ f64     │
╞═════╪══════════╪═════╪═════╪═════════╡
│ 10  ┆ 16901372 ┆ G   ┆ C   ┆ 0.99992 │
│ 11  ┆ 78121030 ┆ T   ┆ A   ┆ 0.99992 │
└─────┴──────────┴─────┴─────┴─────────┘
```

#### Get sample have variant

Get all variant and sample with GENEINFO equal to 'SAMD11:148398'

```sql
〉select distinct chr, pos, ref, alt, sample from read_parquet('variants.parquet') as v left join read_parquet('genotypes/samples/*') as g on v.id=g.id left join read_parquet('annotations/clinvar.parquet') as a on v.id=a.id WHERE GENEINFO='SAMD11:148398';
┌─────┬────────┬─────┬─────┬────────┐
│ chr ┆ pos    ┆ ref ┆ alt ┆ sample │
│ --- ┆ ---    ┆ --- ┆ --- ┆ ---    │
│ u8  ┆ u64    ┆ str ┆ str ┆ str    │
╞═════╪════════╪═════╪═════╪════════╡
│ 1   ┆ 942451 ┆ T   ┆ C   ┆ HG003  │
│ 1   ┆ 942451 ┆ T   ┆ C   ┆ HG001  │
│ 1   ┆ 942451 ┆ T   ┆ C   ┆ HG007  │
│ 1   ┆ 942451 ┆ T   ┆ C   ┆ HG004  │
│ …   ┆ …      ┆ …   ┆ …   ┆ …      │
│ 1   ┆ 942934 ┆ G   ┆ C   ┆ HG003  │
│ 1   ┆ 943937 ┆ C   ┆ T   ┆ HG004  │
│ 1   ┆ 942451 ┆ T   ┆ C   ┆ HG002  │
│ 1   ┆ 942451 ┆ T   ┆ C   ┆ HG006  │
└─────┴────────┴─────┴─────┴────────┘
```

### duckdb

#### Count variants

```sql
D select count(*) from read_parquet('variants.parquet');
┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│      7852699 │
└──────────────┘
```


/// details | check result with `pqrs`
We can check we have same result with pqrs

```bash
➜ pqrs rowcount variants.parquet
File Name: variants.parquet: 7852699 rows
```
///

#### Filter variants from annotations:

Get all variant with a AF_ESP upper than 0.9999

```sql
D select chr, pos, ref, alt, AF_ESP from read_parquet('variants.parquet') as v left join read_parquet('annotations/clinvar.parquet') as c on c.id=v.id where AF_ESP>0.9999;
┌───────┬──────────┬─────────┬─────────┬─────────┐
│  chr  │   pos    │   ref   │   alt   │ AF_ESP  │
│ uint8 │  uint64  │ varchar │ varchar │ double  │
├───────┼──────────┼─────────┼─────────┼─────────┤
│    10 │ 16901372 │ G       │ C       │ 0.99992 │
│    11 │ 78121030 │ T       │ A       │ 0.99992 │
└───────┴──────────┴─────────┴─────────┴─────────┘
```

#### Get sample have variant

Get all variant and sample with GENEINFO equal to 'SAMD11:148398'

```sql
D select distinct chr, pos, ref, alt, sample from read_parquet('variants.parquet') as v left join read_parquet('genotypes/samples/*') as g on v.id=g.id left join read_parquet('annotations/clinvar.parquet') as a on v.id=a.id WHERE GENEINFO='SAMD11:148398';
┌───────┬────────┬─────────┬─────────┬─────────┐
│  chr  │  pos   │   ref   │   alt   │ sample  │
│ uint8 │ uint64 │ varchar │ varchar │ varchar │
├───────┼────────┼─────────┼─────────┼─────────┤
│     1 │ 942451 │ T       │ C       │ HG002   │
│     1 │ 942934 │ G       │ C       │ HG002   │
│     1 │ 942451 │ T       │ C       │ HG003   │
│     1 │ 942934 │ G       │ C       │ HG003   │
│     1 │ 942451 │ T       │ C       │ HG007   │
│     1 │ 943937 │ C       │ T       │ HG007   │
│     1 │ 942451 │ T       │ C       │ HG001   │
│     1 │ 942451 │ T       │ C       │ HG004   │
│     1 │ 943937 │ C       │ T       │ HG004   │
│     1 │ 942451 │ T       │ C       │ HG006   │
├───────┴────────┴─────────┴─────────┴─────────┤
│ 10 rows                            5 columns │
└──────────────────────────────────────────────┘
```

### Use genotype partition

In this example, I'll show how I interact with the data structures created by variantplaner.

#### Import

```python
import duckdb
import polars
import variantplaner
```

#### Get variants

```python
query = f"""
SELECT
  *
FROM
  read_parquet('variants.parquet') as v
WHERE
  v.chr == '19'
"""

variants = duckdb.query(query).pl()
```


#### Add annotations

```python
query = f"""
SELECT
  v.*, c.CLNSIG
FROM
  variants as v
  JOIN
  read_parquet('annotations/clinvar.parquet') as c
  ON
  v.id == c.id
WHERE
  c.CLNSIG LIKE '%Patho%'
"""

annotations = duckdb.query(query).pl()
```

#### Add genotypes

```python
def worker(name_data: (str, polars.DataFrame)) -> polars.DataFrame:
    """Request genotype homozygote variant."""
    name, data = name_data
    query = f"""
SELECT
  data.*, g.*,
FROM
  data
  JOIN
  read_parquet('genotypes/variants/id_part={name}/0.parquet') as g ON data.id = g.id
WHERE
  g.gt == 2
"""
	df = duckdb.query(query).pl()
	return df


annotations = variantplaner.normalization.add_id_part(annotations)

all_genotypes = []

for data in map(worker, annotations.group_by(by="id_part")):
    if data is not None:
        all_genotypes.append(data)

genotypes = polars.concat(all_genotypes)
```

genotypes is polars.DataFrame with pathogene homozygote variants in chromosome 19.
