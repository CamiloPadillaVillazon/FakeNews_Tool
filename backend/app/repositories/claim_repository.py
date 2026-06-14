from sqlalchemy.orm import Session
from ..models.claim import Claim


def save_claim(db: Session, data: dict) -> Claim:
    claim = Claim(**data)
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def get_all_claims(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Claim).order_by(Claim.timestamp.desc()).offset(skip).limit(limit).all()


def get_claim_by_id(db: Session, claim_id: int):
    return db.query(Claim).filter(Claim.id == claim_id).first()
