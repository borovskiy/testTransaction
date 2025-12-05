import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.schemas import TransferRequest, TransferResponse
from app.services import transfer_funds

app = FastAPI()


@app.post("/api/transfer", response_model=TransferResponse)
async def transfer(data: TransferRequest, session: AsyncSession = Depends(get_session)):
    result = await transfer_funds(
        session,
        data.from_wallet,
        data.to_wallet,
        data.amount,
    )
    return TransferResponse(success=True, **result)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",        # путь к приложению
        host="0.0.0.0",
        port=8000,
        reload=True            # авто-перезапуск при изменениях
    )