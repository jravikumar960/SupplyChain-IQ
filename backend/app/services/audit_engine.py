from sqlalchemy.orm import Session
from datetime import datetime, timezone
from backend.app.models.models import AuditLog

def log_audit_event(db: Session, entity_type: str, entity_id: str, event_type: str, previous_state: str, new_state: str, explanation: str):
    audit = AuditLog(
        audit_id=f"AUDIT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        entity_type=entity_type,
        entity_id=entity_id,
        previous_state=previous_state,
        new_state=new_state,
        event_type=event_type,
        timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
        explanation=explanation
    )
    db.add(audit)
    db.commit()
    return audit
