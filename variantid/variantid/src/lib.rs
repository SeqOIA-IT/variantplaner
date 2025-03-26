use pyo3_polars::PolarsAllocator;

mod variantid;

#[global_allocator]
static ALLOC: PolarsAllocator = PolarsAllocator::new();
