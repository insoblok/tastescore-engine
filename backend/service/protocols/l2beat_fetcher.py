"""L2BEAT API integration for fetching Layer 2 risk data."""
import requests
from typing import Dict, Optional, Any
from service.utils import logger


class L2BEATFetcher:
    """Fetches Layer 2 risk data from L2BEAT API."""
    
    BASE_URL = "https://api.l2beat.com/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "TasteScore-Engine/1.0"
        })
    
    def get_all_projects(self) -> list:
        """Fetch all L2 projects from L2BEAT."""
        try:
            url = f"{self.BASE_URL}/projects"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Fetched {len(data)} projects from L2BEAT")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch projects from L2BEAT: {e}")
            return []
    
    def get_project_risk(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get risk assessment for a specific L2 project."""
        try:
            projects = self.get_all_projects()
            for project in projects:
                if project.get("name", "").lower() == project_name.lower():
                    return self._calculate_risk_score(project)
            return None
        except Exception as e:
            logger.warning(f"Failed to get risk for {project_name}: {e}")
            return None
    
    def _calculate_risk_score(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk score from L2BEAT project data."""
        try:
            # L2BEAT provides risk scores in various categories
            # We'll calculate an overall risk score (0-1, where 1 is highest risk)
            risk_score = 0.0
            
            # Check for incidents
            incidents = project.get("incidents", []) or []
            if incidents:
                risk_score += min(0.4, len(incidents) * 0.1)
            
            # Check technology risk
            technology = project.get("technology", {})
            if technology:
                # Check for various risk factors
                state_validation = technology.get("stateValidation", {})
                if state_validation.get("type") == "None":
                    risk_score += 0.2
                
                data_availability = technology.get("dataAvailability", {})
                if data_availability.get("type") == "DAC":
                    risk_score += 0.1
                
                exit_window = technology.get("exitWindow", {})
                if exit_window:
                    risk_score += 0.1
            
            # Check for warnings
            warnings = project.get("warnings", []) or []
            if warnings:
                risk_score += min(0.2, len(warnings) * 0.05)
            
            # Clamp between 0 and 1
            risk_score = min(1.0, max(0.0, risk_score))
            
            return {
                "risk_score": risk_score,
                "technology": project.get("technology", {}),
                "incidents": incidents,
                "warnings": warnings,
                "name": project.get("name", ""),
                "technology_type": project.get("technology", {}).get("category", "")
            }
        except Exception as e:
            logger.error(f"Failed to calculate risk score: {e}")
            return {"risk_score": 0.5, "technology": {}, "incidents": [], "warnings": []}
    
    def get_l2_risk_for_protocol(self, protocol_chain: str) -> Optional[float]:
        """Get L2 risk score for a protocol based on its chain."""
        try:
            # Map common chain names to L2BEAT project names
            chain_mapping = {
                "arbitrum": "Arbitrum One",
                "optimism": "Optimism",
                "polygon": "Polygon",
                "base": "Base",
                "zksync": "zkSync Era",
                "starknet": "Starknet",
                "scroll": "Scroll",
            }
            
            project_name = chain_mapping.get(protocol_chain.lower())
            if not project_name:
                # If not an L2, return low risk
                return 0.0
            
            risk_data = self.get_project_risk(project_name)
            if risk_data:
                return risk_data.get("risk_score", 0.0)
            
            return 0.0
        except Exception as e:
            logger.warning(f"Failed to get L2 risk for {protocol_chain}: {e}")
            return None
