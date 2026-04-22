from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

from app.core.constants import GroupStatus, MemberStatus, MemberRole, DietaryTag


# Group Schemas
class GroupBaseSchema(BaseModel):
    """Base group schema"""
    
    group_name: str = Field(..., min_length=1, max_length=255)
    company_name: str = Field(..., min_length=1, max_length=255)


class GroupCreateSchema(GroupBaseSchema):
    """Group creation schema"""
    
    subscription_plan_id: str
    billing_email: Optional[EmailStr] = None


class GroupResponseSchema(GroupBaseSchema):
    """Group response schema"""
    
    id: str
    group_admin_id: str
    subscription_plan_id: Optional[str]
    status: GroupStatus
    plan_start_date: Optional[datetime]
    plan_end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GroupDetailSchema(GroupResponseSchema):
    """Group detail schema with relationships"""
    
    member_count: Optional[int] = 0


class GroupListSchema(BaseModel):
    """Group list item schema"""
    
    id: str
    group_name: str
    company_name: str
    status: GroupStatus
    member_count: int


# Member Schemas
class MemberBaseSchema(BaseModel):
    """Base member schema"""
    
    dietary_preferences: Optional[List[DietaryTag]] = Field(default=[], description="Dietary restrictions")
    notes: Optional[str] = None


class MemberCreateSchema(BaseModel):
    """Member invitation schema"""
    
    email: EmailStr


class MemberResponseSchema(MemberBaseSchema):
    """Member response schema"""
    
    id: str
    user_id: str
    group_id: str
    status: MemberStatus
    member_role: MemberRole
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MemberDetailSchema(BaseModel):
    """Member detail schema with user info"""
    
    id: str
    user_id: str
    user_email: str
    user_full_name: str
    group_id: str
    status: MemberStatus
    member_role: MemberRole
    dietary_preferences: List[DietaryTag]
    created_at: datetime


class MemberListSchema(BaseModel):
    """Member list item schema"""
    
    id: str
    user_email: str
    user_full_name: str
    status: MemberStatus
    member_role: MemberRole


class MemberUpdateRoleSchema(BaseModel):
    """Update member role schema"""
    
    member_role: MemberRole


class MemberUpdateDietarySchema(BaseModel):
    """Update dietary preferences schema"""
    
    dietary_preferences: List[DietaryTag]
