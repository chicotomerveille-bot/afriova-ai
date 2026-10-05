"""
Base Agent Class for Afriova AI
Définit l'interface commune pour tous les agents IA
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AgentResponse(BaseModel):
    """Modèle de réponse standard pour un agent"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()
    agent_id: str
    agent_name: str

class BaseAgent(ABC):
    """
    Classe de base abstraite pour tous les agents IA d'Afriova
    Chaque agent doit hériter de cette classe et implémenter les méthodes requises
    """
    
    def __init__(self, agent_id: str, name: str, role: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.description = description
        self.is_active = True
        self.created_at = datetime.utcnow()
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Méthode principale de traitement de l'agent
        À implémenter par chaque agent spécifique
        
        Args:
            input_data: Données d'entrée spécifiques à l'agent
            
        Returns:
            AgentResponse: Résultat du traitement
        """
        pass
    
    @abstractmethod
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Valide les données d'entrée pour l'agent
        
        Args:
            input_data: Données à valider
            
        Returns:
            bool: True si valide, False sinon
        """
        pass
    
    async def get_capabilities(self) -> List[str]:
        """
        Retourne la liste des capacités de l'agent
        À surcharger si nécessaire
        """
        return [self.role]
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé de l'agent
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "status": "healthy" if self.is_active else "inactive",
            "last_check": datetime.utcnow().isoformat(),
            "capabilities": await self.get_capabilities()
        }
    
    def __str__(self):
        return f"{self.name} ({self.agent_id}): {self.role}"
    
    def __repr__(self):
        return self.__str__()