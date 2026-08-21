from typing import Dict, Optional
from server.config import settings
import logging

logger = logging.getLogger(__name__)

class TokenManager:
    def __init__(self):
        # In-memory token storage: {domain: {token_name: token_value}}
        self.tokens: Dict[str, Dict[str, str]] = {}

    def add_token(self, domain: str, token_name: str, token_value: str) -> None:
        """Add a session token for a domain."""
        if domain not in self.tokens:
            self.tokens[domain] = {}
        self.tokens[domain][token_name] = token_value
        logger.info(f"Added token for {domain}: {token_name}")

    def get_token(self, domain: str, token_name: str) -> Optional[str]:
        """Get a session token for a domain."""
        return self.tokens.get(domain, {}).get(token_name)

    def get_all_tokens(self, domain: str) -> Dict[str, str]:
        """Get all tokens for a domain."""
        return self.tokens.get(domain, {})

    def validate_token_scope(self, token_domain: str, target_domain: str) -> bool:
        """Validate that a token's domain matches the target domain."""
        # Extract root domain (e.g., "sub.nasa.gov" -> "nasa.gov")
        token_root = self._extract_root_domain(token_domain)
        target_root = self._extract_root_domain(target_domain)
        return token_root == target_root

    @staticmethod
    def _extract_root_domain(domain: str) -> str:
        """Extract the root domain (e.g., 'www.nasa.gov' -> 'nasa.gov')."""
        parts = domain.split(".")
        if len(parts) > 2:
            return ".".join(parts[-2:])  # e.g., ['www', 'nasa', 'gov'] -> 'nasa.gov'
        return domain

    def clear_tokens(self) -> None:
        """Clear all tokens (in-memory only)."""
        self.tokens = {}
        logger.info("All tokens cleared.")
