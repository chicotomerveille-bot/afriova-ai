"""
Amara - Agent Téléphonique & SAV 24/7
Gère les appels entrants/sortants, qualification, prise de RDV, SAV sur WhatsApp/SMS
Adapté au contexte africain (Mobile Money, opérateurs locaux, langues locales)
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
from .base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

class AmaraAgent(BaseAgent):
    """Agent Téléphonique & SAV"""
    
    def __init__(self):
        super().__init__(
            agent_id="amara",
            name="Amara",
            role="Agent Téléphonique & SAV 24/7",
            description="Gère les appels entrants/sortants, qualification, prise de RDV, SAV sur WhatsApp/SMS. Adapté aux réalités africaines (Mobile Money, langues locales, horaires flexibles)."
        )
        # Spécificités africaines
        self.supported_languages = ["fr", "en", "ar", "sw", "wo", "yo", "ha"]  # Français, Anglais, Arabe, Swahili, Wolof, Yoruba, Hausa
        self.supported_currencies = ["XOF", "XAF", "NGN", "KES", "GHS", "ZAR", "MAD", "USD", "EUR"]
        self.supported_payment_methods = [
            "orange_money", "mtn_momo", "wave", "airtel_money", 
            "flutterwave", "paystack", "bank_transfer", "cash"
        ]
        
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Traite une demande liée aux télécommunications/SAV
        
        Types de requêtes supportés:
        - call_handling: Gestion d'appel entrant/sortant
        - appointment_scheduling: Prise de rendez-vous
        - customer_support: Support client
        - payment_reminder: Rappel de paiement Mobile Money
        - language_translation: Traduction/interprétation
        """
        try:
            request_type = input_data.get("type", "general_inquiry")
            
            if request_type == "call_handling":
                return await self._handle_call(input_data)
            elif request_type == "appointment_scheduling":
                return await self._schedule_appointment(input_data)
            elif request_type == "customer_support":
                return await self._provide_support(input_data)
            elif request_type == "payment_reminder":
                return await self._send_payment_reminder(input_data)
            elif request_type == "language_translation":
                return await self._translate_language(input_data)
            else:
                return await self._general_inquiry(input_data)
                
        except Exception as e:
            logger.error(f"Erreur dans AmaraAgent.process: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                message=f"Erreur lors du traitement: {str(e)}",
                agent_id=self.agent_id,
                agent_name=self.name
            )
    
    async def _handle_call(self, data: Dict[str, Any]) -> AgentResponse:
        """Gestion d'appel téléphonique"""
        # Implémentation simplifiée - à connecter à Twilio/Africastalking/etc.
        caller_number = data.get("caller_number")
        call_purpose = data.get("purpose", "general")
        
        logger.info(f"Amara gère l'appel de {caller_number} pour: {call_purpose}")
        
        # Simulation de traitement
        response_data = {
            "call_id": f"call_{datetime.utcnow().timestamp()}",
            "caller_number": caller_number,
            "purpose": call_purpose,
            "action_taken": "call_logged_and_routed",
            "follow_up_required": call_purpose in ["support", "complaint", "sales_inquiry"],
            "estimated_duration": "2-5 minutes",
            "language_detected": data.get("language", "fr"),
            "next_steps": [
                "Call logged in CRM",
                "Agent assigned if needed",
                "SMS confirmation sent"
            ]
        }
        
        return AgentResponse(
            success=True,
            message=f"Appel de {caller_number} traité avec succès",
            data=response_data,
            agent_id=self.agent_id,
            agent_name=self.name
        )
    
    async def _schedule_appointment(self, data: Dict[str, Any]) -> AgentResponse:
        """Prise de rendez-vous synchronisée avec calendrier"""
        client_name = data.get("client_name")
        client_contact = data.get("contact")
        preferred_date = data.get("preferred_date")
        purpose = data.get("purpose", "consultation")
        
        logger.info(f"Amara prend RDV pour {client_name} le {preferred_date}")
        
        response_data = {
            "appointment_id": f"appt_{datetime.utcnow().timestamp()}",
            "client_name": client_name,
            "client_contact": client_contact,
            "scheduled_date": preferred_date,
            "purpose": purpose,
            "calendar_sync": "google_calendar",  # Ou Outlook, Apple Calendar
            "reminder_sent": True,
            "reminder_method": ["sms", "whatsapp"],
            "location": data.get("location", "virtual"),
            "notes": data.get("notes", "")
        }
        
        return AgentResponse(
            success=True,
            message=f"Rendez-vous pris pour {client_name} le {preferred_date}",
            data=response_data,
            agent_id=self.agent_id,
            agent_name=self.name
        )
    
    async def _provide_support(self, data: Dict[str, Any]) -> AgentResponse:
        """Support client SAV"""
        issue_type = data.get("issue_type", "general")
        priority = data.get("priority", "medium")
        customer_id = data.get("customer_id")
        
        logger.info(f"Amara fournit support SAV pour client {customer_id}: {issue_type}")
        
        response_data = {
            "ticket_id": f"ticket_{datetime.utcnow().timestamp()}",
            "customer_id": customer_id,
            "issue_type": issue_type,
            "priority": priority,
            "status": "open",
            "assigned_to": "amara_agent",
            "estimated_resolution": self._estimate_resolution_time(priority),
            "contact_channels": ["phone", "whatsapp", "email"],
            "language": data.get("language", "fr"),
            "resolution_steps": self._get_resolution_steps(issue_type)
        }
        
        return AgentResponse(
            success=True,
            message=f"Ticket SAV créé pour {issue_type} (priorité: {priority})",
            data=response_data,
            agent_id=self.agent_id,
            agent_name=self.name
        )
    
    async def _send_payment_reminder(self, data: Dict[str, Any]) -> AgentResponse:
        """Envoi de rappel de paiement Mobile Money"""
        customer_phone = data.get("customer_phone")
        amount = data.get("amount")
        currency = data.get("currency", "XOF")
        due_date = data.get("due_date")
        invoice_id = data.get("invoice_id")
        
        logger.info(f"Amara envoie rappel paiement de {amount} {currency} à {customer_phone}")
        
        # Détermine le meilleur canal selon la région/opérateur
        payment_channels = self._get_preferred_payment_channels(customer_phone)
        
        response_data = {
            "reminder_id": f"rem_{datetime.utcnow().timestamp()}",
            "customer_phone": customer_phone,
            "amount": amount,
            "currency": currency,
            "due_date": due_date,
            "invoice_id": invoice_id,
            "payment_channels_offered": payment_channels,
            "message_sent": True,
            "delivery_method": "whatsapp",  # ou sms, selon préférence
            "language": data.get("language", "fr"),
            "follow_up_scheduled": True,
            "follow_up_date": self._calculate_follow_up_date(due_date)
        }
        
        return AgentResponse(
            success=True,
            message=f"Rappel de paiement de {amount} {currency} envoyé à {customer_phone}",
            data=response_data,
            agent_id=self.agent_id,
            agent_name=self.name
        )
    
    async def _translate_language(self, data: Dict[str, Any]) -> AgentResponse:
        """Service de traduction/interprétation linguistique"""
        text = data.get("text")
        source_lang = data.get("source_language", "fr")
        target_lang = data.get("target_language", "en")
        context = data.get("context", "business")
        
        logger.info(f"Amara traduit de {source_lang} vers {target_lang}: {text[:50]}...")
        
        # Ici, on intégrerait un service de traduction (Google, DeepL, ou modèle local)
        # Pour la demo, on simule
        translated_text = f"[TRADUIT de {source_lang} vers {target_lang}] {text}"
        
        response_data = {
            "translation_id": f"trans_{datetime.utcnow().timestamp()}",
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang,
            "context": context,
            "confidence_score": 0.95,  # À remplacer par vraie évaluation
            "delivery_method": data.get("delivery_method", "text"),
            "alternative_phrasings": []  # Pour langues tonales
        }
        
        return AgentResponse(
            success=True,
            message=f"Traduction de {source_lang} vers {target_lang} effectuée",
            data=response_data,
            agent_id=self.agent_id,
            agent_name=self.name
        )
    
    async def _general_inquiry(self, data: Dict[str, Any]) -> AgentResponse:
        """Gestion générale des demandes"""
        inquiry = data.get("inquiry", "")
        
        logger.info(f"Amara traite demande générale: {inquiry[:100]}...")
        
        return AgentResponse(
            success=True,
            message="Demande reçue et enregistrée",
            data={
                "inquiry_id": f"inq_{datetime.utcnow().timestamp()}",
                "inquiry": inquiry,
                "received_at": datetime.utcnow().isoformat(),
                "estimated_response_time": "5-15 minutes",
                "suggested_actions": [
                    "Vérifier la FAQ",
                    "Contacter le support spécialisé si nécessaire",
                    "Planifier un rappel si pas de réponse"
                ]
            },
            agent_id=self.agent_id,
            agent_name=self.name
        )
    
    # Méthodes utilitaires
    def _estimate_resolution_time(self, priority: str) -> str:
        times = {
            "low": "24-48 heures",
            "medium": "4-12 heures", 
            "high": "1-4 heures",
            "urgent": "30-60 minutes"
        }
        return times.get(priority, "4-12 heures")
    
    def _get_resolution_steps(self, issue_type: str) -> List[str]:
        steps_map = {
            "billing": ["Vérifier facture", "Contrôler paiement", "Contacter comptabilité"],
            "technical": ["Diagnostiquer problème", "Proposer solution", "Planifier intervention"],
            "service": ["Évaluer satisfaction", "Proposer amélioration", "Suivi qualité"],
            "general": ["Écouter actif", "Identifier besoin", "Proposer solution", "Suivi"]
        }
        return steps_map.get(issue_type, steps_map["general"])
    
    def _get_preferred_payment_channels(self, phone_number: str) -> List[str]:
        """Détermine les canaux de paiement préférés selon le numéro"""
        # Logique simplifiée basée sur préfixe
        if phone_number.startswith("+225"):  # Côte d'Ivoire
            return ["orange_money", "mtn_momo", "wave"]
        elif phone_number.startswith("+226"):  # Burkina Faso
            return ["orange_money", "mtn_momo"]
        elif phone_number.startswith("+233"):  # Ghana
            return ["mtn_momo", "airtel_tigo_money", "vodafone_cash"]
        elif phone_number.startswith("+234"):  # Nigeria
            return ["opay", "palmpay", "flutterwave", "bank_transfer"]
        else:
            return ["orange_money", "mtn_momo", "wave", "flutterwave", "paystack"]
    
    def _calculate_follow_up_date(self, due_date: str) -> str:
        """Calcule la date de suivi après échéance"""
        # Simplifié - en prod utiliser datetime parsing
        return f"{due_date}_plus_2_days"
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valide les données d'entrée pour Amara"""
        required_fields = ["type"]  # Au minimum le type de demande
        return all(field in input_data for field in required_fields)
    
    async def get_capabilities(self) -> List[str]:
        return [
            "call_handling_24_7",
            "appointment_scheduling",
            "customer_support_sav",
            "mobile_money_payment_reminders",
            "multilingual_support",
            "whatsapp_business_integration",
            "sms_notifications",
            "local_language_interpretation"
        ]

# Instance singleton pour faciliter l'accès
amara_agent = AmaraAgent()