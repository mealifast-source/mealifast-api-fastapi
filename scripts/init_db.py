#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and seeds initial data
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, SessionLocal
from app.models import (
    User,
    SubscriptionPlan,
    Meal,
)
from app.core.constants import UserRole, MealCategory, BillingCycle, MealsIncluded
from app.core.security import PasswordManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    init_db()
    logger.info("✓ Database tables created")


def seed_admin_user():
    """Create default admin user"""
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@mealifast.com").first()
        
        if admin:
            logger.info("✓ Admin user already exists")
            return
        
        password_manager = PasswordManager()
        admin = User(
            email="admin@mealifast.com",
            password_hash=password_manager.hash_password("AdminPassword123!"),
            full_name="Platform Administrator",
            phone_number="+1234567890",
            role=UserRole.PLATFORM_ADMIN,
            email_verified=True,
            active=True,
        )
        
        db.add(admin)
        db.commit()
        
        logger.info("✓ Admin user created (email: admin@mealifast.com, password: AdminPassword123!)")
    except Exception as e:
        logger.error(f"✗ Failed to create admin user: {e}")
        db.rollback()
    finally:
        db.close()


def seed_subscription_plans():
    """Create default subscription plans"""
    db = SessionLocal()
    try:
        # Check if plans exist
        existing_count = db.query(SubscriptionPlan).count()
        
        if existing_count > 0:
            logger.info(f"✓ Subscription plans already exist ({existing_count} found)")
            return
        
        plans = [
            SubscriptionPlan(
                plan_name="Starter",
                description="5 meals per week",
                price_per_meal=2.50,
                meals_included=MealsIncluded.FIVE,
                billing_cycle=BillingCycle.WEEKLY,
                min_members=5,
                active=True,
            ),
            SubscriptionPlan(
                plan_name="Professional",
                description="10 meals per week",
                price_per_meal=2.25,
                meals_included=MealsIncluded.TEN,
                billing_cycle=BillingCycle.WEEKLY,
                min_members=10,
                active=True,
            ),
            SubscriptionPlan(
                plan_name="Enterprise",
                description="20+ meals per week",
                price_per_meal=2.00,
                meals_included=MealsIncluded.TWENTY,
                billing_cycle=BillingCycle.BIWEEKLY,
                min_members=20,
                active=True,
            ),
        ]
        
        db.add_all(plans)
        db.commit()
        
        logger.info(f"✓ Created {len(plans)} subscription plans")
    except Exception as e:
        logger.error(f"✗ Failed to create subscription plans: {e}")
        db.rollback()
    finally:
        db.close()


def seed_meals():
    """Create sample meals"""
    db = SessionLocal()
    try:
        # Check if meals exist
        existing_count = db.query(Meal).count()
        
        if existing_count > 0:
            logger.info(f"✓ Meals already exist ({existing_count} found)")
            return
        
        meals = [
            # Breakfast
            Meal(
                name="Scrambled Eggs & Toast",
                description="Fresh eggs with whole wheat toast and butter",
                photo_url="https://via.placeholder.com/300x200?text=Eggs",
                category=MealCategory.BREAKFAST,
                cost_price=3.50,
                dietary_tags=["VEGETARIAN"],
                active=True,
            ),
            Meal(
                name="Oatmeal with Berries",
                description="Creamy oatmeal topped with fresh berries",
                photo_url="https://via.placeholder.com/300x200?text=Oatmeal",
                category=MealCategory.BREAKFAST,
                cost_price=4.00,
                dietary_tags=["VEGETARIAN", "VEGAN", "GLUTEN_FREE"],
                active=True,
            ),
            # Lunch
            Meal(
                name="Grilled Chicken Salad",
                description="Tender grilled chicken with mixed greens",
                photo_url="https://via.placeholder.com/300x200?text=Salad",
                category=MealCategory.LUNCH,
                cost_price=6.50,
                dietary_tags=["GLUTEN_FREE"],
                active=True,
            ),
            Meal(
                name="Vegan Buddha Bowl",
                description="Quinoa, roasted vegetables, and tahini dressing",
                photo_url="https://via.placeholder.com/300x200?text=Buddha",
                category=MealCategory.LUNCH,
                cost_price=7.00,
                dietary_tags=["VEGAN", "GLUTEN_FREE"],
                active=True,
            ),
            # Dinner
            Meal(
                name="Salmon with Asparagus",
                description="Pan-seared salmon with roasted asparagus",
                photo_url="https://via.placeholder.com/300x200?text=Salmon",
                category=MealCategory.DINNER,
                cost_price=10.00,
                dietary_tags=["GLUTEN_FREE"],
                active=True,
            ),
            Meal(
                name="Vegetarian Pasta",
                description="Penne with fresh vegetables and marinara sauce",
                photo_url="https://via.placeholder.com/300x200?text=Pasta",
                category=MealCategory.DINNER,
                cost_price=6.00,
                dietary_tags=["VEGETARIAN"],
                active=True,
            ),
            # Snacks
            Meal(
                name="Greek Yogurt with Granola",
                description="Creamy yogurt with house-made granola",
                photo_url="https://via.placeholder.com/300x200?text=Yogurt",
                category=MealCategory.SNACK,
                cost_price=2.50,
                dietary_tags=["VEGETARIAN", "GLUTEN_FREE"],
                active=True,
            ),
            Meal(
                name="Mixed Nuts & Fruit",
                description="Assorted nuts and dried fruit mix",
                photo_url="https://via.placeholder.com/300x200?text=Nuts",
                category=MealCategory.SNACK,
                cost_price=2.00,
                dietary_tags=["VEGAN", "GLUTEN_FREE"],
                active=True,
            ),
        ]
        
        db.add_all(meals)
        db.commit()
        
        logger.info(f"✓ Created {len(meals)} sample meals")
    except Exception as e:
        logger.error(f"✗ Failed to create meals: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Run all initialization tasks"""
    logger.info("=" * 50)
    logger.info("MealiFast Database Initialization")
    logger.info("=" * 50)
    
    create_tables()
    seed_admin_user()
    seed_subscription_plans()
    seed_meals()
    
    logger.info("=" * 50)
    logger.info("✓ Database initialization completed")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
