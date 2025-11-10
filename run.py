"""애플리케이션 실행 스크립트"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.application.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )

