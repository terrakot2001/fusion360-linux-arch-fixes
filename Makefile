.PHONY: test check install diagnostics

test:
	bash scripts/selftest.sh

check:
	python3 fusion360_arch_fix.py check

install:
	bash install.sh

diagnostics:
	bash scripts/collect-diagnostics.sh
