actions = \
	allrun \
	bench \
	changelog \
	check \
	check-api \
	check-docs \
	check-quality \
	check-types \
	clean \
	coverage \
	docs \
	docs-build \
	docs-deploy \
	format \
	help \
	multirun \
	release \
	run \
	setup \
	test

.PHONY: $(actions)
$(actions):
	@python scripts/make $(MAKECMDGOALS)
