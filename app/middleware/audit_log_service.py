import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import AuditLog
from app.core.constants import AuditAction

logger = logging.getLogger(__name__)


class AuditLogService:
    """Service for recording audit logs"""

    @staticmethod
    def log_action(
        db: Session,
        user_id: str,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        old_value: dict = None,
        new_value: dict = None,
        description: str = None,
    ) -> AuditLog:
        """Log an audit action"""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_value=str(old_value) if old_value else None,
                new_value=str(new_value) if new_value else None,
                description=description,
                created_at=datetime.utcnow(),
            )
            
            db.add(audit_log)
            db.commit()
            
            logger.info(
                f"Audit: {action.value} {entity_type}#{entity_id} by user {user_id}"
            )
            return audit_log
        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")
            db.rollback()
            return None

    @staticmethod
    def log_login(db: Session, user_id: str, success: bool = True) -> AuditLog:
        """Log user login"""
        return AuditLogService.log_action(
            db,
            user_id=user_id,
            action=AuditAction.LOGIN,
            entity_type="User",
            entity_id=user_id,
            description=f"Login {'successful' if success else 'failed'}",
        )

    @staticmethod
    def log_logout(db: Session, user_id: str) -> AuditLog:
        """Log user logout"""
        return AuditLogService.log_action(
            db,
            user_id=user_id,
            action=AuditAction.LOGOUT,
            entity_type="User",
            entity_id=user_id,
            description="User logged out",
        )

    @staticmethod
    def log_create(
        db: Session,
        user_id: str,
        entity_type: str,
        entity_id: str,
        new_value: dict,
        description: str = None,
    ) -> AuditLog:
        """Log entity creation"""
        return AuditLogService.log_action(
            db,
            user_id=user_id,
            action=AuditAction.CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            new_value=new_value,
            description=description or f"{entity_type} created",
        )

    @staticmethod
    def log_update(
        db: Session,
        user_id: str,
        entity_type: str,
        entity_id: str,
        old_value: dict,
        new_value: dict,
        description: str = None,
    ) -> AuditLog:
        """Log entity update"""
        return AuditLogService.log_action(
            db,
            user_id=user_id,
            action=AuditAction.UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            description=description or f"{entity_type} updated",
        )

    @staticmethod
    def log_delete(
        db: Session,
        user_id: str,
        entity_type: str,
        entity_id: str,
        old_value: dict,
        description: str = None,
    ) -> AuditLog:
        """Log entity deletion"""
        return AuditLogService.log_action(
            db,
            user_id=user_id,
            action=AuditAction.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            description=description or f"{entity_type} deleted",
        )

    @staticmethod
    def get_user_audit_logs(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list, int]:
        """Get audit logs for a user"""
        query = db.query(AuditLog).filter(AuditLog.user_id == user_id)
        total = query.count()
        logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        return logs, total

    @staticmethod
    def get_entity_audit_logs(
        db: Session,
        entity_type: str,
        entity_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list, int]:
        """Get audit logs for a specific entity"""
        query = db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id,
        )
        total = query.count()
        logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        return logs, total

    @staticmethod
    def get_all_audit_logs(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        action_filter: str = None,
    ) -> tuple[list, int]:
        """Get all audit logs with optional filtering"""
        query = db.query(AuditLog)
        
        if action_filter:
            try:
                query = query.filter(AuditLog.action == AuditAction[action_filter.upper()])
            except KeyError:
                pass
        
        total = query.count()
        logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        return logs, total
