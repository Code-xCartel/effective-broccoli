from effective_broccoli.domain.abstract import AbstractDomain
from effective_broccoli.domain.RPS.RPS import RPS

DOMAIN_REGISTRY = {"RPS": RPS}


def get_domain_from_registry(domain: str) -> type[AbstractDomain]:
    if domain not in DOMAIN_REGISTRY:
        raise Exception(f"Domain '{domain}' is not registered.")
    return DOMAIN_REGISTRY[domain]
