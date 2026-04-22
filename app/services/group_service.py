from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from datetime import datetime

from app.models import MealiFastGroup, GroupMember, User
from app.core.constants import GroupStatus, MemberStatus, AuditAction
from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    InsufficientPermissionException,
)
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class GroupService(BaseService[MealiFastGroup]):
    """Service for group operations"""
    
    def __init__(self):
        super().__init__(MealiFastGroup)
    
    def create_group(
        self,
        db: Session,
        group_name: str,
        company_name: str,
        admin_id: str,
        subscription_plan_id: str,
    ) -> MealiFastGroup:
        """Create new group"""
        try:
            group = self.create(
                db,
                group_name=group_name,
                company_name=company_name,
                group_admin_id=admin_id,
                subscription_plan_id=subscription_plan_id,
                status=GroupStatus.PENDING,
            )
            logger.info(f"Group created: {group.id}")
            return group
        except Exception as e:
            logger.error(f"Failed to create group: {e}")
            raise
    
    def approve_group(self, db: Session, group_id: str) -> MealiFastGroup:
        """Approve pending group"""
        group = self.get_by_id(db, group_id)
        
        if not group:
            raise NotFoundException("Group", group_id)
        
        if group.status != GroupStatus.PENDING:
            raise ConflictException(f"Cannot approve group with status {group.status}")
        
        group = self.update(db, group_id, status=GroupStatus.ACTIVE)
        logger.info(f"Group approved: {group_id}")
        return group
    
    def suspend_group(self, db: Session, group_id: str) -> MealiFastGroup:
        """Suspend active group"""
        group = self.get_by_id(db, group_id)
        
        if not group:
            raise NotFoundException("Group", group_id)
        
        group = self.update(db, group_id, status=GroupStatus.SUSPENDED)
        logger.info(f"Group suspended: {group_id}")
        return group
    
    def reactivate_group(self, db: Session, group_id: str) -> MealiFastGroup:
        """Reactivate suspended group"""
        group = self.get_by_id(db, group_id)
        
        if not group:
            raise NotFoundException("Group", group_id)
        
        if group.status != GroupStatus.SUSPENDED:
            raise ConflictException(f"Cannot reactivate group with status {group.status}")
        
        group = self.update(db, group_id, status=GroupStatus.ACTIVE)
        logger.info(f"Group reactivated: {group_id}")
        return group
    
    def get_group_members_count(self, db: Session, group_id: str) -> int:
        """Get active members count for group"""
        try:
            return db.query(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.status == MemberStatus.ACTIVE,
            ).count()
        except Exception as e:
            logger.error(f"Failed to count group members: {e}")
            raise


class GroupMemberService(BaseService[GroupMember]):
    """Service for group member operations"""
    
    def __init__(self):
        super().__init__(GroupMember)
    
    def invite_member(
        self,
        db: Session,
        group_id: str,
        email: str,
        user_id: Optional[str] = None,
    ) -> GroupMember:
        """Invite member to group"""
        # Check if already a member
        existing_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        ).first() if user_id else None
        
        if existing_member:
            raise ConflictException(f"User is already a member of this group")
        
        try:
            member = self.create(
                db,
                user_id=user_id,
                group_id=group_id,
                status=MemberStatus.INVITED,
            )
            logger.info(f"Member invited: {member.id}")
            return member
        except Exception as e:
            logger.error(f"Failed to invite member: {e}")
            raise
    
    def activate_member(self, db: Session, member_id: str) -> GroupMember:
        """Activate invited member"""
        member = self.get_by_id(db, member_id)
        
        if not member:
            raise NotFoundException("Member", member_id)
        
        if member.status != MemberStatus.INVITED:
            raise ConflictException(f"Cannot activate member with status {member.status}")
        
        member = self.update(db, member_id, status=MemberStatus.ACTIVE)
        logger.info(f"Member activated: {member_id}")
        return member
    
    def suspend_member(self, db: Session, member_id: str) -> GroupMember:
        """Suspend active member"""
        member = self.get_by_id(db, member_id)
        
        if not member:
            raise NotFoundException("Member", member_id)
        
        member = self.update(db, member_id, status=MemberStatus.SUSPENDED)
        logger.info(f"Member suspended: {member_id}")
        return member
    
    def deactivate_member(self, db: Session, member_id: str) -> GroupMember:
        """Deactivate member"""
        member = self.get_by_id(db, member_id)
        
        if not member:
            raise NotFoundException("Member", member_id)
        
        member = self.update(db, member_id, status=MemberStatus.INACTIVE)
        logger.info(f"Member deactivated: {member_id}")
        return member
    
    def get_group_members(self, db: Session, group_id: str, skip: int = 0, limit: int = 20) -> tuple[List[GroupMember], int]:
        """Get members of a group"""
        try:
            total = db.query(GroupMember).filter(GroupMember.group_id == group_id).count()
            members = db.query(GroupMember).filter(
                GroupMember.group_id == group_id
            ).offset(skip).limit(limit).all()
            return members, total
        except Exception as e:
            logger.error(f"Failed to get group members: {e}")
            raise
    
    def get_active_members(self, db: Session, group_id: str) -> List[GroupMember]:
        """Get active members of a group"""
        try:
            return db.query(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.status == MemberStatus.ACTIVE,
            ).all()
        except Exception as e:
            logger.error(f"Failed to get active members: {e}")
            raise
    
    def update_dietary_preferences(
        self,
        db: Session,
        member_id: str,
        dietary_preferences: list,
    ) -> GroupMember:
        """Update member dietary preferences"""
        member = self.get_by_id(db, member_id)
        
        if not member:
            raise NotFoundException("Member", member_id)
        
        member = self.update(db, member_id, dietary_preferences=dietary_preferences)
        logger.info(f"Dietary preferences updated for member: {member_id}")
        return member
