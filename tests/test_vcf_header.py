"""Test for the `objects.vcf_header` module."""

# std import
from __future__ import annotations

import pathlib

# 3rd party import
# project import
from variantplaner.objects import Vcf

DATA_DIR = pathlib.Path(__file__).parent / "data"


def test_vcf_metadata_no_genotypes() -> None:
    """Convert header in metadata."""
    vcf_path = DATA_DIR / "no_genotypes.vcf"

    obj = Vcf()
    obj.from_path(vcf_path, DATA_DIR / "grch38.92.csv")

    assert obj.header.build_metadata() == {
        "af_esp": 'INFO=<ID=AF_ESP,Number=1,Type=Float,Description="allele frequencies from GO-ESP">',
        "af_exac": 'INFO=<ID=AF_EXAC,Number=1,Type=Float,Description="allele frequencies from ExAC">',
        "af_tgp": 'INFO=<ID=AF_TGP,Number=1,Type=Float,Description="allele frequencies from TGP">',
        "alleleid": 'INFO=<ID=ALLELEID,Number=1,Type=Integer,Description="the ClinVar Allele ID">',
        "clndisdb": 'INFO=<ID=CLNDISDB,Number=.,Type=String,Description="Tag-value pairs of disease database name and identifier, e.g. OMIM:NNNNNN">',
        "clndisdbincl": 'INFO=<ID=CLNDISDBINCL,Number=.,Type=String,Description="For included Variant: Tag-value pairs of disease database name and identifier, e.g. OMIM:NNNNNN">',
        "clndn": 'INFO=<ID=CLNDN,Number=.,Type=String,Description="ClinVar\'s preferred disease name for the concept specified by disease identifiers in CLNDISDB">',
        "clndnincl": 'INFO=<ID=CLNDNINCL,Number=.,Type=String,Description="For included Variant : ClinVar\'s preferred disease name for the concept specified by disease identifiers in CLNDISDB">',
        "clnhgvs": 'INFO=<ID=CLNHGVS,Number=.,Type=String,Description="Top-level (primary assembly, alt, or patch) HGVS expression.">',
        "clnrevstat": 'INFO=<ID=CLNREVSTAT,Number=.,Type=String,Description="ClinVar review status for the Variation ID">',
        "clnsig": 'INFO=<ID=CLNSIG,Number=.,Type=String,Description="Clinical significance for this single variant; multiple values are separated by a vertical bar">',
        "clnsigconf": 'INFO=<ID=CLNSIGCONF,Number=.,Type=String,Description="Conflicting clinical significance for this single variant; multiple values are separated by a vertical bar">',
        "clnsigincl": 'INFO=<ID=CLNSIGINCL,Number=.,Type=String,Description="Clinical significance for a haplotype or genotype that includes this variant. Reported as pairs of VariationID:clinical significance; multiple values are separated by a vertical bar">',
        "clnvc": 'INFO=<ID=CLNVC,Number=1,Type=String,Description="Variant type">',
        "clnvcso": 'INFO=<ID=CLNVCSO,Number=1,Type=String,Description="Sequence Ontology id for variant type">',
        "clnvi": 'INFO=<ID=CLNVI,Number=.,Type=String,Description="the variant\'s clinical sources reported as tag-value pairs of database and variant identifier">',
        "dbvarid": 'INFO=<ID=DBVARID,Number=.,Type=String,Description="nsv accessions from dbVar for the variant">',
        "geneinfo": 'INFO=<ID=GENEINFO,Number=1,Type=String,Description="Gene(s) for the variant reported as gene symbol:gene id. The gene symbol and id are delimited by a colon (:) and each pair is delimited by a vertical bar (|)">',
        "mc": 'INFO=<ID=MC,Number=.,Type=String,Description="comma separated list of molecular consequence in the form of Sequence Ontology ID|molecular_consequence">',
        "origin": 'INFO=<ID=ORIGIN,Number=.,Type=String,Description="Allele origin. One or more of the following values may be added: 0 - unknown; 1 - germline; 2 - somatic; 4 - inherited; 8 - paternal; 16 - maternal; 32 - de-novo; 64 - biparental; 128 - uniparental; 256 - not-tested; 512 - tested-inconclusive; 1073741824 - other">',
        "rs": 'INFO=<ID=RS,Number=.,Type=String,Description="dbSNP ID (i.e. rs number)">',
    }


def test_vcf_metadata_no_info() -> None:
    """Convert header in metadata."""
    vcf_path = DATA_DIR / "no_info.vcf"

    obj = Vcf()
    obj.from_path(vcf_path, DATA_DIR / "grch38.92.csv")

    assert obj.header.build_metadata() == {
        "ad": 'FORMAT=<ID=AD,Number=R,Type=Integer,Description="Allelic depths for the ref and alt alleles in the order listed">',
        "dp": 'FORMAT=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth (reads with MQ=255 or with bad mates are filtered)">',
        "gq": 'FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">',
        "gt": 'FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
    }


def test_vcf_metadata_sv() -> None:
    """Convert header in metadata."""
    vcf_path = DATA_DIR / "sv.vcf"

    obj = Vcf()
    obj.from_path(vcf_path, DATA_DIR / "grch38.92.csv")

    assert obj.header.build_metadata() == {
        "bkptid": 'INFO=<ID=BKPTID,Number=.,Type=String,Description="ID of the assembled alternate allele in the assembly file">',
        "ciend": 'INFO=<ID=CIEND,Number=2,Type=Integer,Description="Confidence interval around END for imprecise variants">',
        "cipos": 'INFO=<ID=CIPOS,Number=2,Type=Integer,Description="Confidence interval around POS for imprecise variants">',
        "end": 'INFO=<ID=END,Number=1,Type=Integer,Description="End position of the variant described in this record">',
        "homlen": 'INFO=<ID=HOMLEN,Number=.,Type=Integer,Description="Length of base pair identical micro-homology at event breakpoints">',
        "homseq": 'INFO=<ID=HOMSEQ,Number=.,Type=String,Description="Sequence of base pair identical micro-homology at event breakpoints">',
        "svlen": 'INFO=<ID=SVLEN,Number=.,Type=Integer,Description="Difference in length between REF and ALT alleles">',
        "svtype": 'INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant">',
        "gt": 'FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
        "gq": 'FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype quality">',
        "cn": 'FORMAT=<ID=CN,Number=1,Type=Integer,Description="Copy number genotype for imprecise events">',
        "cnq": 'FORMAT=<ID=CNQ,Number=1,Type=Float,Description="Copy number genotype quality for imprecise events">',
    }


def test_vcf_metadata_sv_filter() -> None:
    """Convert header in metadata."""
    vcf_path = DATA_DIR / "sv.vcf"

    obj = Vcf()
    obj.from_path(vcf_path, DATA_DIR / "grch38.92.csv")

    assert obj.header.build_metadata(select_columns=["bkptid", "gt"]) == {
        "bkptid": 'INFO=<ID=BKPTID,Number=.,Type=String,Description="ID of the assembled alternate allele in the assembly file">',
        "gt": 'FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
    }
