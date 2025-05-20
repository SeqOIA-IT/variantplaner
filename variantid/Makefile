
SHELL=/bin/bash

venv:  ## Set up virtual environment
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

install: venv
	unset CONDA_PREFIX && \
	source venv/bin/activate && maturin develop -m variantid/Cargo.toml

install-release: venv
	unset CONDA_PREFIX && \
	source venv/bin/activate && maturin develop --release -m variantid/Cargo.toml

clean:
	-@rm -r venv
	-@rm -rf bench_data
	-@cd variantid && cargo clean

run: install
	source venv/bin/activate && python run.py

run-release: install-release
	source venv/bin/activate && python run.py

bench_data/HG001.vcf.gz:
	mkdir -p bench_data
	sed '2,$s/^/chr/' ../tests/data/grch38.92.csv > bench_data/grch38.92.csv
	curl https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release//NA12878_HG001/latest/GRCh38/HG001_GRCh38_1_22_v4.2.1_benchmark.vcf.gz > bench_data/HG001.vcf.gz

bench_data/HG001.v.parquet: bench_data/HG001.vcf.gz
	variantplaner vcf2parquet -i bench_data/HG001.vcf.gz -c bench_data/grch38.92.csv variants -o bench_data/HG001.v.parquet

benchmark: bench_data/HG001.v.parquet install-release
	hyperfine -n 1 -n 2 -n 4 -n 8 -n 12 "source venv/bin/activate && python bench.py 1 1" "source venv/bin/activate && python bench.py 2 1" "source venv/bin/activate && python bench.py 4 1" "source venv/bin/activate && python bench.py 8 1" "source venv/bin/activate && python bench.py 12 1"
