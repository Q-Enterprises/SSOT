"""
Qbert Query Parser - A playful query interface for the Qube system.

Inspired by arcade gaming culture, this parser handles natural language
queries to the Qube orchestrator and capsule system.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class QueryType(Enum):
    """Types of queries supported by the Qbert parser."""
    CAPSULE_LOOKUP = "capsule_lookup"
    SCRIPT_SEARCH = "script_search"
    ARTIFACT_FIND = "artifact_find"
    LINEAGE_TRACE = "lineage_trace"
    TELEMETRY_CHECK = "telemetry_check"
    RELAY_STATUS = "relay_status"
    UNKNOWN = "unknown"


@dataclass
class ParsedQuery:
    """Structured representation of a parsed query."""
    query_type: QueryType
    target: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_query: Optional[str] = None


class QbertQueryParser:
    """
    A query parser that understands gaming-themed and natural language
    queries for the Qube orchestrator system.
    """

    def __init__(self):
        """Initialize the parser with keyword mappings."""
        self.keywords = {
            "capsule": QueryType.CAPSULE_LOOKUP,
            "script": QueryType.SCRIPT_SEARCH,
            "artifact": QueryType.ARTIFACT_FIND,
            "lineage": QueryType.LINEAGE_TRACE,
            "fork": QueryType.LINEAGE_TRACE,
            "telemetry": QueryType.TELEMETRY_CHECK,
            "relay": QueryType.RELAY_STATUS,
            "status": QueryType.RELAY_STATUS,
        }

    def parse(self, query: str) -> ParsedQuery:
        """
        Parse a natural language query into structured format.

        Args:
            query: The raw query string

        Returns:
            ParsedQuery object with structured query information
        """
        query_lower = query.lower().strip()
        
        # Detect query type based on keywords
        query_type = QueryType.UNKNOWN
        target = None
        filters = {}
        
        for keyword, qtype in self.keywords.items():
            if keyword in query_lower:
                query_type = qtype
                # Extract potential target after the keyword
                if keyword in query_lower:
                    parts = query_lower.split(keyword)
                    if len(parts) > 1:
                        # Clean up target
                        target = parts[1].strip().split()[0] if parts[1].strip().split() else None
                break

        # Look for version indicators
        if "v1" in query_lower:
            filters["version"] = "v1"
        
        # Look for specific capsule patterns
        if "qube" in query_lower or "qbert" in query_lower:
            filters["namespace"] = "qube"
        
        if "cinematic" in query_lower:
            filters["category"] = "cinematic"
        
        if "lineage" in query_lower or "fork" in query_lower:
            query_type = QueryType.LINEAGE_TRACE

        return ParsedQuery(
            query_type=query_type,
            target=target,
            filters=filters if filters else None,
            metadata={"gaming_ref": self._detect_gaming_refs(query)},
            raw_query=query
        )

    def _detect_gaming_refs(self, query: str) -> List[str]:
        """Detect gaming culture references in the query."""
        gaming_refs = []
        refs = {
            "qbert": "Q*bert",
            "t-rex": "Chrome T-Rex Runner",
            "ralph": "Wreck-It Ralph",
            "sugar rush": "Sugar Rush Racing",
            "street fighter": "Street Fighter",
            "nos": "Nitrous Oxide System (Racing)",
            "mc": "Master of Ceremonies / Emcee",
        }
        
        query_lower = query.lower()
        for key, name in refs.items():
            if key in query_lower:
                gaming_refs.append(name)
        
        return gaming_refs

    def format_response(self, parsed: ParsedQuery) -> Dict[str, Any]:
        """
        Format a parsed query into a response payload.

        Args:
            parsed: ParsedQuery object

        Returns:
            Dictionary ready for JSON serialization
        """
        return {
            "query_type": parsed.query_type.value,
            "target": parsed.target,
            "filters": parsed.filters,
            "metadata": parsed.metadata,
            "raw_query": parsed.raw_query,
        }


def create_parser() -> QbertQueryParser:
    """Factory function to create a QbertQueryParser instance."""
    return QbertQueryParser()


# Example queries that the parser can handle:
EXAMPLES = [
    "capsule qube cinematic v1",
    "script lineage fork",
    "artifact relay status",
    "telemetry check qube",
    "find capsule script.qube.cinematic.v1",
]
