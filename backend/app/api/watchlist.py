from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User, Watchlist
from app.schemas import WatchlistCreate, WatchlistResponse, WatchlistUpdate

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistResponse])
async def list_watchlist(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> list[Watchlist]:
    return list((await db.scalars(select(Watchlist).order_by(Watchlist.created_at.desc()))).all())


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist(payload: WatchlistCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> Watchlist:
    item = Watchlist(**payload.model_dump(), added_by=user.id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(watchlist_id: int, payload: WatchlistUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> Watchlist:
    item = await db.get(Watchlist, watchlist_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Watchlist entry not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(watchlist_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> None:
    item = await db.get(Watchlist, watchlist_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Watchlist entry not found")
    await db.delete(item)
    await db.commit()
