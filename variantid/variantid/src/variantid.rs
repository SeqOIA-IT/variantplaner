//! Module implement variantid panic

/* std use */

/* 3rd party use */
use polars::prelude::*;

/* project use */

#[derive(serde::Deserialize)]
struct ComputeIdKwargs {
    max_pos: u64,
}

#[inline(always)]
fn nuc2bit(nuc: u8) -> u64 {
    (nuc as u64 >> 1) & 0b11
}

#[inline(always)]
fn seq2bit(seq: &[u8]) -> u64 {
    let mut two_bit = 0;

    for nuc in seq {
        two_bit <<= 2;
        two_bit |= nuc2bit(*nuc)
    }

    two_bit
}

#[inline(always)]
fn ref_alt_space_usage(ref_len: u64, alt_len: u64) -> u64 {
    (64 - ref_len.leading_zeros() as u64) + (alt_len * 2)
}

fn compute_id_worker(pos: u64, ref_seq: &str, alt_seq: &str, max_pos: u64) -> u64 {
    let mut hash = 0;
    let pos_mov = max_pos.leading_zeros() as u64 - 1;
    let hasher: ahash::RandomState = ahash::RandomState::with_seeds(42, 42, 42, 42);

    if ref_alt_space_usage(ref_seq.len() as u64, alt_seq.len() as u64) > pos_mov {
        let mut key = Vec::with_capacity(128);

        key.extend(pos.to_be_bytes());
        key.extend(ref_seq.as_bytes());
        key.extend(alt_seq.as_bytes());

        hash = (1 << 63) | (hasher.hash_one(&key) >> 1);
    } else {
        hash |= pos << pos_mov;
        hash |= (ref_seq.len() as u64) << (alt_seq.len() * 2);
        hash |= seq2bit(alt_seq.as_bytes());
    }

    hash
}

#[derive(serde::Deserialize)]
struct ComputePartKwargs {
    number_of_bits: u64,
}

fn compute_part_worker(id: u64, number_of_bits: u64) -> u64 {
    if id >> 63 == 0b1 {
        (1 << number_of_bits) - 1
    } else {
        (id << 1) >> (64 - number_of_bits)
    }
}

#[pyo3_polars::derive::polars_expr(output_type=UInt64)]
fn compute_id(inputs: &[Series], kwargs: ComputeIdKwargs) -> PolarsResult<Series> {
    let pos = inputs[0].u64()?;
    let ref_seq = inputs[1].str()?;
    let alt_seq = inputs[2].str()?;
    let max_pos = kwargs.max_pos;

    let output: UInt64Chunked = UInt64Chunked::from_vec(
        PlSmallStr::from_str("id"),
        pos.iter()
            .zip(ref_seq.iter())
            .zip(alt_seq.iter())
            .map(|((p, r), a)| match (p, r, a) {
                (Some(p), Some(r), Some(a)) => compute_id_worker(p, r, a, max_pos),
                _ => u64::MAX,
            })
            .collect(),
    );

    Ok(output.into_series())
}

#[pyo3_polars::derive::polars_expr(output_type=UInt64)]
fn compute_part(inputs: &[Series], kwargs: ComputePartKwargs) -> PolarsResult<Series> {
    let id = inputs[0].u64()?;
    let number_of_bits = kwargs.number_of_bits;

    let output: UInt64Chunked =
        (*id).apply_values(|value| compute_part_worker(value, number_of_bits));

    Ok(output.into_series())
}
