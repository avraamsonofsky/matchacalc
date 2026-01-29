from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.calc.schemas import CalculationRequest, CalculationResponse
from app.calc.service import calculate_metrics
from app.db.models import PropertyClass

router = APIRouter()


@router.post("/preview", response_model=CalculationResponse)
def calculate_preview(
    request: CalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Разовый расчёт по ручному вводу
    Rate-limiting применяется через middleware
    """
    try:
        # WACC: если передан в процентах, конвертируем в долю; иначе None
        discount_rate = (request.wacc / 100.0) if request.wacc is not None else None

        result = calculate_metrics(
            db=db,
            purchase_price=request.purchase_price,
            area=request.area,
            location_group_id=request.location_group_id,
            report_id=request.report_id,
            scenario_id=request.scenario_id,
            holding_years=request.holding_years,
            property_class=request.property_class or PropertyClass.A,
            discount_rate=discount_rate
        )
        return CalculationResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка расчёта: {str(e)}"
        )
