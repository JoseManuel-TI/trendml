import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from auth.deps import get_current_user, require_plan
from services import forecast_service

router = APIRouter(prefix='/api/lab', tags=['historical-inference'])
logger = logging.getLogger(__name__)

class ForecastRequest(BaseModel):
    product_id: str = Field(min_length=1, max_length=50)


def execute(operation):
    try:
        return operation()
    except KeyError:
        raise HTTPException(404, 'Producto no disponible en el catálogo histórico')
    except Exception:
        logger.exception('Historical inference unavailable')
        raise HTTPException(503, 'Modelo histórico no disponible. Preparar datos y entrenar v3 en el servidor.')


@router.get('/products')
def products(user=Depends(get_current_user)):
    return execute(forecast_service.catalog)


@router.post('/forecast')
def forecast(payload: ForecastRequest, user=Depends(require_plan('pro', 'premium'))):
    return execute(lambda: forecast_service.forecast(payload.product_id))
