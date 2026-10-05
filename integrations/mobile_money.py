"""
Intégrations Mobile Money pour l'Afrique
Support pour Orange Money, MTN Mobile Money, Wave, Airtel Money, etc.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import hashlib
import hmac
import json
import aiohttp
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class PaymentRequest(BaseModel):
    """Demande de paiement Mobile Money"""
    amount: float
    currency: str
    phone_number: str
    customer_name: Optional[str] = None
    reference: str
    description: Optional[str] = None
    callback_url: Optional[str] = None

class PaymentResponse(BaseModel):
    """Réponse de paiement Mobile Money"""
    success: bool
    transaction_id: Optional[str] = None
    reference: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None  # pending, completed, failed, cancelled
    message: str
    fees: Optional[float] = None
    processed_at: Optional[datetime] = None
    raw_response: Optional[Dict[str, Any]] = None

class MobileMoneyProvider(ABC):
    """Interface abstraite pour les providers Mobile Money"""
    
    def __init__(self, api_key: str, api_secret: str, environment: str = "sandbox"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.environment = environment
        self.base_url = self._get_base_url()
        
    @abstractmethod
    def _get_base_url(self) -> str:
        """Retourne l'URL de base de l'API selon l'environnement"""
        pass
    
    @abstractmethod
    def _get_headers(self, payload: Optional[Dict] = None) -> Dict[str, str]:
        """Génère les headers d'authentification"""
        pass
    
    @abstractmethod
    async def send_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Envoie une demande de paiement"""
        pass
    
    @abstractmethod
    async def check_transaction_status(self, transaction_id: str) -> PaymentResponse:
        """Vérifie le statut d'une transaction"""
        pass
    
    @abstractmethod
    async def validate_phone_number(self, phone_number: str) -> bool:
        """Valide le format du numéro de téléphone pour ce provider"""
        pass
    
    async def _make_request(self, method: str, endpoint: str, 
                          data: Optional[Dict] = None, 
                          params: Optional[Dict] = None) -> Dict[str, Any]:
        """Effectue une requête HTTP avec gestion d'erreurs"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(data)
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method, url, 
                    json=data, 
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        logger.error(f"API Error {response.status}: {response_data}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "details": response_data
                        }
                    
                    return response_data
            except Exception as e:
                logger.error(f"Request failed: {str(e)}", exc_info=True)
                return {
                    "success": False,
                    "error": "Request failed",
                    "details": str(e)
                }

# ======================
# ORANGE MONEY IMPLEMENTATION
# ======================

class OrangeMoneyProvider(MobileMoneyProvider):
    """Provider Orange Money (Côte d'Ivoire, Sénégal, Burkina Faso, etc.)"""
    
    def _get_base_url(self) -> str:
        if self.environment == "sandbox":
            return "https://api.orange.com/orange-money-webpay/sandbox/v1"
        return "https://api.orange.com/orange-money-webpay/v1"
    
    def _get_headers(self, payload: Optional[Dict] = None) -> Dict[str, str]:
        # Orange Money utilise Basic Auth ou OAuth2 selon l'implémentation
        # Simplifié pour l'exemple
        credentials = f"{self.api_key}:{self.api_secret}"
        encoded_credentials = hashlib.sha256(credentials.encode()).hexdigest()
        
        return {
            "Authorization": f"Bearer {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def send_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Envoie un paiement via Orange Money API"""
        # Validation du numéro
        if not await self.validate_phone_number(request.phone_number):
            return PaymentResponse(
                success=False,
                message=f"Numéro de téléphone invalide pour Orange Money: {request.phone_number}"
            )
        
        payload = {
            "amount": str(request.amount),
            "currency": request.currency,
            "order": {
                "reference": request.reference,
                "description": request.description or "Paiement via Afriova AI",
                "customer": {
                    "phone_number": request.phone_number,
                    "name": request.customer_name
                }
            },
            "return_url": request.callback_url or "https://afriova.ai/payment/callback",
            "cancel_url": request.callback_url or "https://afriova.ai/payment/cancelled"
        }
        
        response_data = await self._make_request(
            "POST", 
            "/merchant/payin/webpay", 
            data=payload
        )
        
        if response_data.get("success"):
            return PaymentResponse(
                success=True,
                transaction_id=response_data.get("transaction_id"),
                reference=request.reference,
                amount=request.amount,
                currency=request.currency,
                status="pending",
                message="Paiement initié avec succès",
                processed_at=datetime.utcnow(),
                raw_response=response_data
            )
        else:
            return PaymentResponse(
                success=False,
                message=response_data.get("message", "Erreur inconnue"),
                raw_response=response_data
            )
    
    async def check_transaction_status(self, transaction_id: str) -> PaymentResponse:
        """Vérifie le statut d'une transaction Orange Money"""
        response_data = await self._make_request(
            "GET",
            f"/merchant/payin/webpay/{transaction_id}/status"
        )
        
        if response_data.get("success"):
            status_mapping = {
                "PENDING": "pending",
                "SUCCESSFUL": "completed",
                "FAILED": "failed",
                "CANCELLED": "cancelled",
                "EXPIRED": "expired"
            }
            
            return PaymentResponse(
                success=True,
                transaction_id=transaction_id,
                amount=float(response_data.get("amount", 0)),
                currency=response_data.get("currency", "XOF"),
                status=status_mapping.get(response_data.get("status"), "unknown"),
                message=response_data.get("message", "Statut récupéré"),
                processed_at=datetime.utcnow(),
                raw_response=response_data
            )
        else:
            return PaymentResponse(
                success=False,
                message=response_data.get("message", "Erreur lors de la vérification"),
                raw_response=response_data
            )
    
    async def validate_phone_number(self, phone_number: str) -> bool:
        """Valide un numéro de téléphone pour Orange Money selon le pays"""
        # Formats courants pour Orange Money Afrique
        patterns = [
            r'^\+225\d{8,9}$',   # Côte d'Ivoire
            r'^\+221\d{9}$',     # Sénégal
            r'^\+226\d{8}$',     # Burkina Faso
            r'^\+223\d{8}$',     # Mali
            r'^\+228\d{8}$',     # Togo
            r'^\+229\d{8}$',     # Bénin
            r'^\+237\d{9}$',     # Cameroun
            r'^\+242\d{9}$',     # Congo-Brazzaville
            r'^\+243\d{9}$',     # Congo-Kinshasa
        ]
        
        import re
        return any(re.match(pattern, phone_number) for pattern in patterns)

# ======================
# MTN MOBILE MONEY IMPLEMENTATION
# ======================

class MTNMobileMoneyProvider(MobileMoneyProvider):
    """Provider MTN Mobile Money (disponible dans 18+ pays africains)"""
    
    def _get_base_url(self) -> str:
        if self.environment == "sandbox":
            return "https://sandbox.momodeveloper.mtn.com"
        return "https://momodeveloper.mtn.com"
    
    def _get_headers(self, payload: Optional[Dict] = None) -> Dict[str, str]:
        # MTN utilise OAuth2 avec subscription key
        return {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Authorization": f"Bearer {self.api_secret}",  # En prod, obtenir token OAuth
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def send_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Envoie un paiement via MTN Mobile Money API"""
        if not await self.validate_phone_number(request.phone_number):
            return PaymentResponse(
                success=False,
                message=f"Numéro de téléphone invalide pour MTN MoMo: {request.phone_number}"
            )
        
        # MTN MoMo Collection API
        payload = {
            "amount": str(request.amount),
            "currency": request.currency,
            "externalId": request.reference,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": request.phone_number
            },
            "payerMessage": request.description or "Paiement via Afriova AI",
            "payeeNote": f"Transaction Afriova AI - {request.reference}"
        }
        
        response_data = await self._make_request(
            "POST",
            "/collection/v1_0/topup",
            data=payload
        )
        
        # MTN retourne 202 Accepted pour demandes réussies
        if response_data.get("success") is not False:  # MTN peut retourner 202 sans body
            return PaymentResponse(
                success=True,
                transaction_id=response_data.get("referenceId", request.reference),
                reference=request.reference,
                amount=request.amount,
                currency=request.currency,
                status="pending",
                message="Paiement initié avec succès (MTN MoMo)",
                processed_at=datetime.utcnow(),
                raw_response=response_data
            )
        else:
            return PaymentResponse(
                success=False,
                message=response_data.get("message", "Erreur inconnue"),
                raw_response=response_data
            )
    
    async def check_transaction_status(self, transaction_id: str) -> PaymentResponse:
        """Vérifie le statut d'une transaction MTN MoMo"""
        response_data = await self._make_request(
            "GET",
            f"/collection/v1_0/topup/{transaction_id}"
        )
        
        if response_data.get("success") is not False:
            status_mapping = {
                "SUCCESSFUL": "completed",
                "FAILED": "failed",
                "PENDING": "pending"
            }
            
            return PaymentResponse(
                success=True,
                transaction_id=transaction_id,
                amount=float(response_data.get("amount", 0)),
                currency=response_data.get("currency", "XOF"),
                status=status_mapping.get(response_data.get("status"), "unknown"),
                message=response_data.get("reason", "Statut récupéré"),
                processed_at=datetime.utcnow(),
                raw_response=response_data
            )
        else:
            return PaymentResponse(
                success=False,
                message=response_data.get("message", "Erreur lors de la vérification"),
                raw_response=response_data
            )
    
    async def validate_phone_number(self, phone_number: str) -> bool:
        """Valide un numéro pour MTN Mobile Money"""
        # MTN opère dans beaucoup de pays africains
        patterns = [
            r'^\+233\d{9}$',     # Ghana
            r'^\+234\d{10,11}$', # Nigeria
            r'^\+256\d{9}$',     # Uganda
            r'^\+250\d{9}$',     # Rwanda
            r'^\+257\d{8}$',     # Burundi
            r'^\+260\d{9}$',     # Zambia
            r'^\+263\d{9}$',     # Zimbabwe
            r'^\+265\d{8,9}$',   # Malawi
            r'^\+266\d{8}$',     # Lesotho
            r'^\+267\d{8}$',     # Botswana
            r'^\+268\d{8}$',     # Eswatini
            r'^\+269\d{7}$',     # Djibouti
            r'^\+290\d{4}$',     # Sainte-Hélène
        ]
        
        import re
        return any(re.match(pattern, phone_number) for pattern in patterns)

# ======================
# WAVE IMPLEMENTATION (Sénégal, Côte d'Ivoire, etc.)
# ======================

class WaveProvider(MobileMoneyProvider):
    """Provider Wave (Sénégal, Côte d'Ivoire, Burkina Faso, Mali)"""
    
    def _get_base_url(self) -> str:
        # Wave utilise une API REST différente
        if self.environment == "sandbox":
            return "https://api.wave.com/sandbox"
        return "https://api.wave.com"
    
    def _get_headers(self, payload: Optional[Dict] = None) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def send_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Envoie un paiement via Wave API"""
        if not await self.validate_phone_number(request.phone_number):
            return PaymentResponse(
                success=False,
                message=f"Numéro de téléphone invalide pour Wave: {request.phone_number}"
            )
        
        payload = {
            "amount": {
                "value": int(request.amount * 100),  # Wave utilise centimes
                "currency": request.currency
            },
            "destination": {
                "type": "mobile_money",
                "phone_number": request.phone_number
            },
            "reference": request.reference,
            "description": request.description or "Paiement via Afriova AI"
        }
        
        response_data = await self._make_request(
            "POST",
            "/transfers",
            data=payload
        )
        
        if response_data.get("success"):
            return PaymentResponse(
                success=True,
                transaction_id=response_data.get("id"),
                reference=request.reference,
                amount=request.amount,
                currency=request.currency,
                status="pending",
                message="Paiement initié avec succès (Wave)",
                processed_at=datetime.utcnow(),
                raw_response=response_data
            )
        else:
            return PaymentResponse(
                success=False,
                message=response_data.get("message", "Erreur inconnue"),
                raw_response=response_data
            )
    
    async def check_transaction_status(self, transaction_id: str) -> PaymentResponse:
        """Vérifie le statut d'une transaction Wave"""
        response_data = await self._make_request(
            "GET",
            f"/transfers/{transaction_id}"
        )
        
        if response_data.get("success"):
            status_mapping = {
                "PENDING": "pending",
                "SETTLED": "completed",
                "FAILED": "failed",
                "CANCELLED": "cancelled"
            }
            
            return PaymentResponse(
                success=True,
                transaction_id=transaction_id,
                amount=float(response_data.get("amount", {}).get("value", 0)) / 100,
                currency=response_data.get("amount", {}).get("currency", "XOF"),
                status=status_mapping.get(response_data.get("status"), "unknown"),
                message=response_data.get("status", "Statut récupéré"),
                processed_at=datetime.utcnow(),
                raw_response=response_data
            )
        else:
            return PaymentResponse(
                success=False,
                message=response_data.get("message", "Erreur lors de la vérification"),
                raw_response=response_data
            )
    
    async def validate_phone_number(self, phone_number: str) -> bool:
        """Valide un numéro pour Wave"""
        patterns = [
            r'^\+225\d{8,9}$',   # Côte d'Ivoire
            r'^\+221\d{9}$',     # Sénégal
            r'^\+226\d{8}$',     # Burkina Faso
            r'^\+223\d{8}$',     # Mali
        ]
        
        import re
        return any(re.match(pattern, phone_number) for pattern in patterns)

# Factory pour obtenir le bon provider
def get_mobile_money_provider(provider_name: str, api_key: str, api_secret: str, 
                            environment: str = "sandbox") -> MobileMoneyProvider:
    """Factory pour créer un provider Mobile Money selon son nom"""
    providers = {
        "orange_money": OrangeMoneyProvider,
        "mtn_momo": MTNMobileMoneyProvider,
        "wave": WaveProvider,
        # Ajouter d'autres providers ici
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Provider non supporté: {provider_name}. Disponibles: {list(providers.keys())}")
    
    return provider_class(api_key, api_secret, environment)

# Exemple d'utilisation
if __name__ == "__main__":
    # Ce code ne s'exécutera pas directement car nécessite asyncio
    # Mais montre comment utiliser les integrations
    pass