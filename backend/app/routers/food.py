from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import FoodItem
from app.schemas import FoodResponse


router = APIRouter(
    prefix="/food",
    tags=["Food"]
)


@router.get(
    "",
    response_model=list[FoodResponse]
)
async def get_food(
    db: AsyncSession =
        Depends(get_db)
):

    result = await db.scalars(
        select(FoodItem)
        .where(
            FoodItem.available == True
        )
        .order_by(FoodItem.id)
    )

    return list(result.all())