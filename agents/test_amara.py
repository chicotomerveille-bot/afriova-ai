"""
Tests simples pour l'agent Amara
À exécuter avec: python -m pytest agents/test_amara.py -v
"""

import asyncio
import pytest
from agents.amara import amara_agent

@pytest.mark.asyncio
async def test_amara_initialization():
    """Test que l'agent Amara s'initialise correctement"""
    assert amara_agent.agent_id == "amara"
    assert amara_agent.name == "Amara"
    assert amara_agent.role == "Agent Téléphonique & SAV 24/7"
    assert amara_agent.is_active == True

@pytest.mark.asyncio
async def test_amara_handle_call():
    """Test de la gestion d'appel"""
    input_data = {
        "type": "call_handling",
        "caller_number": "+2250700000000",
        "purpose": "support",
        "language": "fr"
    }
    
    response = await amara_agent.process(input_data)
    
    assert response.success == True
    assert "call_id" in response.data
    assert response.data["caller_number"] == "+2250700000000"
    assert response.data["purpose"] == "support"
    assert response.agent_id == "amara"
    assert response.agent_name == "Amara"

@pytest.mark.asyncio
async def test_amara_schedule_appointment():
    """Test de prise de rendez-vous"""
    input_data = {
        "type": "appointment_scheduling",
        "client_name": "Jean Kouassi",
        "contact": "+2250700000000",
        "preferred_date": "2026-10-15T14:30:00Z",
        "purpose": "consultation",
        "language": "fr"
    }
    
    response = await amara_agent.process(input_data)
    
    assert response.success == True
    assert "appointment_id" in response.data
    assert response.data["client_name"] == "Jean Kouassi"
    assert response.data["purpose"] == "consultation"

@pytest.mark.asyncio
async def test_amara_payment_reminder():
    """Test d'envoi de rappel de paiement Mobile Money"""
    input_data = {
        "type": "payment_reminder",
        "customer_phone": "+2250700000000",
        "amount": 15000,
        "currency": "XOF",
        "due_date": "2026-10-20",
        "invoice_id": "INV-2026-001",
        "language": "fr"
    }
    
    response = await amara_agent.process(input_data)
    
    assert response.success == True
    assert "reminder_id" in response.data
    assert response.data["amount"] == 15000
    assert response.data["currency"] == "XOF"
    assert response.data["customer_phone"] == "+2250700000000"

@pytest.mark.asyncio
async def test_amara_language_translation():
    """Test de traduction linguistique"""
    input_data = {
        "type": "language_translation",
        "text": "Bonjour, je souhaite prendre un rendez-vous pour demain",
        "source_language": "fr",
        "target_language": "en",
        "context": "business"
    }
    
    response = await amara_agent.process(input_data)
    
    assert response.success == True
    assert "translation_id" in response.data
    assert response.data["source_language"] == "fr"
    assert response.data["target_language"] == "en"
    assert "translated_text" in response.data

@pytest.mark.asyncio
async def test_amara_validate_input():
    """Test de validation des entrées"""
    # Données valides
    valid_data = {"type": "call_handling", "caller_number": "+2250700000000"}
    assert await amara_agent.validate_input(valid_data) == True
    
    # Données invalides (missing type)
    invalid_data = {"caller_number": "+2250700000000"}
    assert await amara_agent.validate_input(invalid_data) == False

@pytest.mark.asyncio
async def test_amara_health_check():
    """Test du health check de l'agent"""
    health = await amara_agent.health_check()
    
    assert health["agent_id"] == "amara"
    assert health["agent_name"] == "Amara"
    assert health["status"] == "healthy"
    assert isinstance(health["capabilities"], list)
    assert len(health["capabilities"]) > 0

if __name__ == "__main__":
    # Exécution simple des tests
    asyncio.run(test_amara_initialization())
    asyncio.run(test_amara_handle_call())
    asyncio.run(test_amara_schedule_appointment())
    asyncio.run(test_amara_payment_reminder())
    asyncio.run(test_amara_language_translation())
    asyncio.run(test_amara_validate_input())
    asyncio.run(test_amara_health_check())
    print("✅ Tous les tests de base d'Amara ont réussi!")