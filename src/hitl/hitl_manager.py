"""
HITL Manager - Sistema Human-in-the-Loop
Detecta situações que requerem intervenção humana e envia notificações
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger


class HITLManager:
    """Gerenciador do sistema Human-in-the-Loop"""
    
    def __init__(self, settings):
        self.settings = settings
        self._ready = False
        
        # Estado das intervenções
        self.active_interventions: Dict[str, Dict] = {}
        self.intervention_history: List[Dict] = []
        
        # Configurações de notificação
        self.notification_enabled = True
        self.mock_mode = True  # Para o protótipo
        
        # Tipos de intervenção
        self.intervention_types = {
            "rule_conflict": {
                "priority": "high",
                "description": "Conflito de regras detectado"
            },
            "critical_decision": {
                "priority": "high",
                "description": "Decisão crítica necessária"
            },
            "complex_narrative": {
                "priority": "medium",
                "description": "Situação narrativa complexa"
            },
            "ai_request": {
                "priority": "medium",
                "description": "IA solicitou intervenção"
            },
            "player_complaint": {
                "priority": "high",
                "description": "Reclamação de jogador"
            },
            "technical_issue": {
                "priority": "low",
                "description": "Problema técnico detectado"
            }
        }
    
    async def initialize(self):
        """Inicializar HITL Manager"""
        try:
            logger.info("Inicializando HITL Manager...")
            
            if self.mock_mode:
                logger.info("📢 Modo mock ativado - notificações simuladas")
            else:
                # Em produção, configurar canais de notificação reais
                await self._setup_notification_channels()
            
            self._ready = True
            logger.info("✅ HITL Manager inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar HITL Manager: {e}")
            # Continuar em modo mock
            self.mock_mode = True
            self._ready = True
            logger.warning("Continuando em modo mock")
    
    def is_ready(self) -> bool:
        """Verifica se o HITL Manager está pronto"""
        return self._ready
    
    async def _setup_notification_channels(self):
        """Configurar canais de notificação reais"""
        # TODO: Implementar configuração real de Discord, Email, SMS
        pass
    
    async def trigger_intervention(self, reason: str, context: Dict, 
                                  priority: str = "medium", 
                                  intervention_type: str = "ai_request") -> Dict:
        """
        Aciona uma intervenção humana
        
        Args:
            reason: Motivo da intervenção
            context: Contexto da situação
            priority: Prioridade (low, medium, high)
            intervention_type: Tipo de intervenção
            
        Returns:
            Dict com ID da intervenção e status
        """
        try:
            # Gerar ID único
            intervention_id = f"intervention_{datetime.now().timestamp()}"
            
            # Criar registro da intervenção
            intervention = {
                "id": intervention_id,
                "type": intervention_type,
                "reason": reason,
                "context": context,
                "priority": priority,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "notified_channels": [],
                "resolution": None,
                "resolved_at": None,
                "resolved_by": None
            }
            
            # Adicionar à lista de intervenções ativas
            self.active_interventions[intervention_id] = intervention
            
            # Enviar notificações
            notification_result = await self._send_notifications(intervention)
            intervention["notified_channels"] = notification_result.get("channels", [])
            
            # Log da intervenção
            logger.warning(f"🚨 HITL Intervenção acionada: {reason} (ID: {intervention_id})")
            
            return {
                "intervention_id": intervention_id,
                "status": "triggered",
                "priority": priority,
                "notifications_sent": notification_result.get("success", False)
            }
            
        except Exception as e:
            logger.error(f"Erro ao acionar intervenção: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def _send_notifications(self, intervention: Dict) -> Dict:
        """
        Envia notificações para canais configurados
        
        Args:
            intervention: Dados da intervenção
            
        Returns:
            Resultado das notificações
        """
        if self.mock_mode:
            return await self._send_mock_notifications(intervention)
        else:
            return await self._send_real_notifications(intervention)
    
    async def _send_mock_notifications(self, intervention: Dict) -> Dict:
        """Simula envio de notificações para desenvolvimento"""
        
        channels_sent = []
        
        # Simular Discord
        if self.settings.discord_webhook_url:
            logger.info(f"📢 [MOCK] Discord notificado: {intervention['reason']}")
            channels_sent.append("discord")
        
        # Simular Email
        if self.settings.hitl_email_recipients:
            logger.info(f"📧 [MOCK] Email enviado para: {', '.join(self.settings.hitl_email_recipients)}")
            channels_sent.append("email")
        
        # Simular SMS
        if self.settings.twilio_phone_number:
            logger.info(f"📱 [MOCK] SMS enviado: {intervention['reason']}")
            channels_sent.append("sms")
        
        return {
            "success": True,
            "channels": channels_sent,
            "mode": "mock"
        }
    
    async def _send_real_notifications(self, intervention: Dict) -> Dict:
        """Envia notificações reais (para produção)"""
        
        channels_sent = []
        errors = []
        
        try:
            # Discord
            if self.settings.discord_webhook_url:
                discord_result = await self._send_discord_notification(intervention)
                if discord_result["success"]:
                    channels_sent.append("discord")
                else:
                    errors.append(f"Discord: {discord_result['error']}")
            
            # Email
            if self.settings.hitl_email_recipients:
                email_result = await self._send_email_notification(intervention)
                if email_result["success"]:
                    channels_sent.append("email")
                else:
                    errors.append(f"Email: {email_result['error']}")
            
            # SMS
            if self.settings.twilio_phone_number:
                sms_result = await self._send_sms_notification(intervention)
                if sms_result["success"]:
                    channels_sent.append("sms")
                else:
                    errors.append(f"SMS: {sms_result['error']}")
            
            return {
                "success": len(channels_sent) > 0,
                "channels": channels_sent,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificações: {e}")
            return {
                "success": False,
                "channels": [],
                "errors": [str(e)]
            }
    
    async def _send_discord_notification(self, intervention: Dict) -> Dict:
        """Envia notificação via Discord webhook"""
        # TODO: Implementar envio real via Discord
        return {"success": False, "error": "Not implemented"}
    
    async def _send_email_notification(self, intervention: Dict) -> Dict:
        """Envia notificação via email"""
        # TODO: Implementar envio real via SMTP
        return {"success": False, "error": "Not implemented"}
    
    async def _send_sms_notification(self, intervention: Dict) -> Dict:
        """Envia notificação via SMS (Twilio)"""
        # TODO: Implementar envio real via Twilio
        return {"success": False, "error": "Not implemented"}
    
    async def resolve_intervention(self, intervention_id: str, resolution: str, 
                                 resolved_by: str = "human") -> Dict:
        """
        Resolve uma intervenção
        
        Args:
            intervention_id: ID da intervenção
            resolution: Resolução aplicada
            resolved_by: Quem resolveu
            
        Returns:
            Status da resolução
        """
        try:
            if intervention_id not in self.active_interventions:
                raise ValueError(f"Intervenção não encontrada: {intervention_id}")
            
            intervention = self.active_interventions[intervention_id]
            
            # Atualizar intervenção
            intervention["status"] = "resolved"
            intervention["resolution"] = resolution
            intervention["resolved_at"] = datetime.now().isoformat()
            intervention["resolved_by"] = resolved_by
            
            # Mover para histórico
            self.intervention_history.append(intervention)
            del self.active_interventions[intervention_id]
            
            logger.info(f"✅ Intervenção resolvida: {intervention_id}")
            
            return {
                "status": "resolved",
                "intervention_id": intervention_id,
                "resolution": resolution
            }
            
        except Exception as e:
            logger.error(f"Erro ao resolver intervenção: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def get_active_interventions(self) -> List[Dict]:
        """Retorna lista de intervenções ativas"""
        return list(self.active_interventions.values())
    
    async def get_intervention_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de intervenções"""
        return self.intervention_history[-limit:]
    
    async def get_intervention_stats(self) -> Dict:
        """Retorna estatísticas das intervenções"""
        
        total_interventions = len(self.intervention_history) + len(self.active_interventions)
        active_count = len(self.active_interventions)
        resolved_count = len(self.intervention_history)
        
        # Contar por tipo
        type_counts = {}
        priority_counts = {}
        
        all_interventions = list(self.active_interventions.values()) + self.intervention_history
        
        for intervention in all_interventions:
            intervention_type = intervention.get("type", "unknown")
            priority = intervention.get("priority", "unknown")
            
            type_counts[intervention_type] = type_counts.get(intervention_type, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "total_interventions": total_interventions,
            "active_interventions": active_count,
            "resolved_interventions": resolved_count,
            "resolution_rate": (resolved_count / total_interventions * 100) if total_interventions > 0 else 0,
            "by_type": type_counts,
            "by_priority": priority_counts,
            "last_updated": datetime.now().isoformat()
        }
    
    def detect_intervention_needed(self, context: Dict) -> Optional[Dict]:
        """
        Detecta automaticamente se uma intervenção é necessária
        
        Args:
            context: Contexto da situação
            
        Returns:
            Dict com detalhes da intervenção necessária ou None
        """
        
        # Regras de detecção automática
        player_message = context.get("player_message", "").lower()
        
        # Palavras-chave que podem indicar problema
        problem_keywords = [
            "bug", "erro", "problema", "não funciona", "travou",
            "injusto", "trapaça", "hack", "roubo"
        ]
        
        # Palavras-chave sensíveis
        sensitive_keywords = [
            "suicídio", "morte", "matar", "violência",
            "discriminação", "preconceito", "assédio"
        ]
        
        # Detectar problemas técnicos
        if any(keyword in player_message for keyword in problem_keywords):
            return {
                "type": "technical_issue",
                "reason": "Possível problema técnico detectado",
                "priority": "medium",
                "auto_detected": True
            }
        
        # Detectar conteúdo sensível
        if any(keyword in player_message for keyword in sensitive_keywords):
            return {
                "type": "complex_narrative",
                "reason": "Conteúdo sensível detectado",
                "priority": "high",
                "auto_detected": True
            }
        
        # Detectar mensagens muito longas (possível confusão)
        if len(player_message) > 500:
            return {
                "type": "complex_narrative",
                "reason": "Mensagem muito longa, possível situação complexa",
                "priority": "low",
                "auto_detected": True
            }
        
        return None
    
    async def create_intervention_report(self) -> str:
        """Cria relatório das intervenções"""
        
        stats = await self.get_intervention_stats()
        active_interventions = await self.get_active_interventions()
        
        report = f"""
# Relatório de Intervenções HITL

## Estatísticas Gerais
- **Total de Intervenções**: {stats['total_interventions']}
- **Intervenções Ativas**: {stats['active_interventions']}
- **Intervenções Resolvidas**: {stats['resolved_interventions']}
- **Taxa de Resolução**: {stats['resolution_rate']:.1f}%

## Por Tipo
"""
        
        for intervention_type, count in stats['by_type'].items():
            report += f"- **{intervention_type}**: {count}\n"
        
        report += "\n## Por Prioridade\n"
        
        for priority, count in stats['by_priority'].items():
            report += f"- **{priority}**: {count}\n"
        
        if active_interventions:
            report += "\n## Intervenções Ativas\n"
            for intervention in active_interventions:
                report += f"- **{intervention['id']}**: {intervention['reason']} (Prioridade: {intervention['priority']})\n"
        
        report += f"\n*Relatório gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return report
    
    async def cleanup(self):
        """Limpeza na finalização"""
        logger.info("Finalizando HITL Manager...")
        self._ready = False